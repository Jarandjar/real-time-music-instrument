"""WebSocket router for real-time audio streaming."""
import json
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.audio_generator import audio_generator
from app.services.ai_music import ai_music

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept and store a new WebSocket connection.

        Args:
            websocket: WebSocket connection to accept.
        """
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection to remove.
        """
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients.

        Args:
            message: Message dictionary to broadcast.
        """
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time music interaction.

    Handles messages:
    - play_note: Play a single note
    - stop_note: Stop playing
    - get_suggestion: Get AI note suggestion
    - harmonize: Harmonize a note

    Args:
        websocket: WebSocket connection.
    """
    await manager.connect(websocket)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to real-time music instrument",
        })

        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
                continue

            msg_type = message.get("type", "")

            if msg_type == "play_note":
                await handle_play_note(websocket, message)

            elif msg_type == "stop_note":
                await websocket.send_json({
                    "type": "note_stopped",
                    "message": "Note stopped",
                })

            elif msg_type == "get_suggestion":
                await handle_get_suggestion(websocket, message)

            elif msg_type == "harmonize":
                await handle_harmonize(websocket, message)

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def handle_play_note(websocket: WebSocket, message: dict):
    """Handle play_note message.

    Args:
        websocket: WebSocket connection.
        message: Message dictionary with note data.
    """
    note = message.get("note", "C4")
    duration = message.get("duration", 0.5)
    velocity = message.get("velocity", 0.8)
    instrument = message.get("instrument", "piano")

    try:
        # Generate audio
        samples = audio_generator.generate_note(
            note=note,
            duration=duration,
            velocity=velocity,
            instrument=instrument,
        )

        # Convert to base64
        audio_base64 = audio_generator.samples_to_base64(samples)

        await websocket.send_json({
            "type": "audio",
            "note": note,
            "audio": audio_base64,
            "format": "wav",
            "encoding": "base64",
        })

    except ValueError as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e),
        })


async def handle_get_suggestion(websocket: WebSocket, message: dict):
    """Handle get_suggestion message.

    Args:
        websocket: WebSocket connection.
        message: Message dictionary with current note.
    """
    current_note = message.get("current_note", "C4")
    scale_type = message.get("scale_type", "major")
    style = message.get("style", "melodic")

    suggestion = ai_music.suggest_next_note(current_note, scale_type, style)

    await websocket.send_json({
        "type": "suggestion",
        "current_note": current_note,
        "suggested_note": suggestion,
    })


async def handle_harmonize(websocket: WebSocket, message: dict):
    """Handle harmonize message.

    Args:
        websocket: WebSocket connection.
        message: Message dictionary with note to harmonize.
    """
    note = message.get("note", "C4")
    harmony_type = message.get("harmony_type", "third")

    harmonies = ai_music.harmonize_note(note, harmony_type)

    await websocket.send_json({
        "type": "harmony",
        "base_note": note,
        "notes": harmonies,
    })
