"""Tests for the FastAPI application endpoints."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestRootEndpoint:
    """Test cases for root endpoint."""

    def test_root_returns_api_info(self, client):
        """Test that root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestHealthEndpoint:
    """Test cases for health endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestMusicEndpoints:
    """Test cases for music endpoints."""

    def test_play_note(self, client):
        """Test playing a note."""
        response = client.post(
            "/music/note",
            json={
                "note": "C4",
                "velocity": 0.8,
                "duration": 0.5,
                "instrument": "piano",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["note"] == "C4"
        assert "frequency" in data
        assert "samples" in data

    def test_play_note_invalid_note(self, client):
        """Test playing an invalid note returns error."""
        response = client.post(
            "/music/note",
            json={
                "note": "X9",
                "velocity": 0.8,
                "duration": 0.5,
                "instrument": "piano",
            },
        )

        assert response.status_code == 400

    def test_get_note_audio(self, client):
        """Test getting note audio."""
        response = client.get("/music/note/C4/audio")

        assert response.status_code == 200
        data = response.json()
        assert data["note"] == "C4"
        assert "audio" in data
        assert data["format"] == "wav"
        assert data["encoding"] == "base64"

    def test_get_note_audio_with_params(self, client):
        """Test getting note audio with parameters."""
        response = client.get(
            "/music/note/A4/audio",
            params={
                "duration": 1.0,
                "velocity": 0.5,
                "instrument": "synth",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["note"] == "A4"

    def test_get_scale(self, client):
        """Test getting scale notes."""
        response = client.get("/music/scale/C")

        assert response.status_code == 200
        data = response.json()
        assert data["root"] == "C"
        assert "notes" in data
        assert len(data["notes"]) == 7

    def test_get_scale_with_params(self, client):
        """Test getting scale with parameters."""
        response = client.get(
            "/music/scale/A",
            params={"scale_type": "minor", "octave": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["scale_type"] == "minor"

    def test_suggest_next_note(self, client):
        """Test note suggestion."""
        response = client.post(
            "/music/suggest",
            params={"current_note": "C4"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["current_note"] == "C4"
        assert "suggested_note" in data

    def test_harmonize_note(self, client):
        """Test note harmonization."""
        response = client.post(
            "/music/harmonize",
            params={"note": "C4", "harmony_type": "third"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["base_note"] == "C4"
        assert "notes" in data
        assert len(data["notes"]) >= 2

    def test_generate_melody(self, client):
        """Test melody generation."""
        response = client.get("/music/melody")

        assert response.status_code == 200
        data = response.json()
        assert "melody" in data
        assert len(data["melody"]) == 8

    def test_list_instruments(self, client):
        """Test listing instruments."""
        response = client.get("/music/instruments")

        assert response.status_code == 200
        data = response.json()
        assert "instruments" in data
        assert "piano" in data["instruments"]
        assert "synth" in data["instruments"]


class TestWebSocket:
    """Test cases for WebSocket endpoint."""

    def test_websocket_connect(self, client):
        """Test WebSocket connection."""
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connected"

    def test_websocket_ping_pong(self, client):
        """Test WebSocket ping/pong."""
        with client.websocket_connect("/ws") as websocket:
            # Receive welcome message
            websocket.receive_json()

            # Send ping
            websocket.send_json({"type": "ping"})
            response = websocket.receive_json()
            assert response["type"] == "pong"

    def test_websocket_play_note(self, client):
        """Test playing note via WebSocket."""
        with client.websocket_connect("/ws") as websocket:
            # Receive welcome message
            websocket.receive_json()

            # Send play note message
            websocket.send_json({
                "type": "play_note",
                "note": "C4",
                "duration": 0.5,
                "velocity": 0.8,
                "instrument": "piano",
            })

            response = websocket.receive_json()
            assert response["type"] == "audio"
            assert response["note"] == "C4"
            assert "audio" in response

    def test_websocket_invalid_note(self, client):
        """Test playing invalid note via WebSocket."""
        with client.websocket_connect("/ws") as websocket:
            # Receive welcome message
            websocket.receive_json()

            # Send invalid note
            websocket.send_json({
                "type": "play_note",
                "note": "X9",
            })

            response = websocket.receive_json()
            assert response["type"] == "error"

    def test_websocket_get_suggestion(self, client):
        """Test getting suggestion via WebSocket."""
        with client.websocket_connect("/ws") as websocket:
            # Receive welcome message
            websocket.receive_json()

            # Request suggestion
            websocket.send_json({
                "type": "get_suggestion",
                "current_note": "C4",
            })

            response = websocket.receive_json()
            assert response["type"] == "suggestion"
            assert "suggested_note" in response

    def test_websocket_harmonize(self, client):
        """Test harmonizing via WebSocket."""
        with client.websocket_connect("/ws") as websocket:
            # Receive welcome message
            websocket.receive_json()

            # Request harmonization
            websocket.send_json({
                "type": "harmonize",
                "note": "C4",
                "harmony_type": "chord",
            })

            response = websocket.receive_json()
            assert response["type"] == "harmony"
            assert "notes" in response

    def test_websocket_unknown_type(self, client):
        """Test unknown message type."""
        with client.websocket_connect("/ws") as websocket:
            # Receive welcome message
            websocket.receive_json()

            # Send unknown type
            websocket.send_json({"type": "unknown_type"})

            response = websocket.receive_json()
            assert response["type"] == "error"
