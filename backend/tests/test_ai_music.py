"""Tests for the AI music service."""
import pytest

from app.services.ai_music import AIMusic


class TestAIMusic:
    """Test cases for AIMusic service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.ai_music = AIMusic()

    def test_get_scale_notes_major(self):
        """Test getting major scale notes."""
        notes = self.ai_music.get_scale_notes("C", "major", 4)

        assert len(notes) == 7
        assert notes[0] == "C4"

    def test_get_scale_notes_minor(self):
        """Test getting minor scale notes."""
        notes = self.ai_music.get_scale_notes("A", "minor", 4)

        assert len(notes) == 7
        assert notes[0] == "A4"

    def test_get_scale_notes_pentatonic(self):
        """Test getting pentatonic scale notes."""
        notes = self.ai_music.get_scale_notes("C", "pentatonic", 4)

        assert len(notes) == 5

    def test_get_scale_notes_blues(self):
        """Test getting blues scale notes."""
        notes = self.ai_music.get_scale_notes("A", "blues", 4)

        assert len(notes) == 6

    def test_get_scale_notes_invalid_scale_defaults_to_major(self):
        """Test that invalid scale type defaults to major."""
        notes = self.ai_music.get_scale_notes("C", "invalid_scale", 4)

        # Should return major scale (7 notes)
        assert len(notes) == 7

    def test_suggest_next_note_returns_valid_note(self):
        """Test that suggest_next_note returns a valid note."""
        suggestion = self.ai_music.suggest_next_note("C4", "major", "melodic")

        # Should return a note with octave
        assert len(suggestion) >= 2
        assert suggestion[-1].isdigit()

    def test_suggest_next_note_stepwise(self):
        """Test stepwise note suggestion."""
        # Run multiple times to check it returns valid notes
        for _ in range(10):
            suggestion = self.ai_music.suggest_next_note("C4", "major", "stepwise")
            assert len(suggestion) >= 2

    def test_suggest_next_note_random(self):
        """Test random note suggestion."""
        suggestion = self.ai_music.suggest_next_note("C4", "major", "random")
        assert len(suggestion) >= 2

    def test_generate_melody(self):
        """Test melody generation."""
        melody = self.ai_music.generate_melody(8, "C", "major", 4)

        assert len(melody) == 8

        for note, duration, velocity in melody:
            # Check note format
            assert len(note) >= 2
            assert note[-1].isdigit()

            # Check duration is positive
            assert duration > 0

            # Check velocity is in range
            assert 0 <= velocity <= 1

    def test_generate_melody_different_lengths(self):
        """Test melody generation with different lengths."""
        for length in [4, 8, 16]:
            melody = self.ai_music.generate_melody(length, "C", "major", 4)
            assert len(melody) == length

    def test_harmonize_note_third(self):
        """Test harmonizing with a third."""
        harmonies = self.ai_music.harmonize_note("C4", "third")

        assert len(harmonies) == 2
        assert harmonies[0] == "C4"
        assert "E" in harmonies[1]  # Major third

    def test_harmonize_note_fifth(self):
        """Test harmonizing with a fifth."""
        harmonies = self.ai_music.harmonize_note("C4", "fifth")

        assert len(harmonies) == 2
        assert harmonies[0] == "C4"
        assert "G" in harmonies[1]  # Perfect fifth

    def test_harmonize_note_octave(self):
        """Test harmonizing with an octave."""
        harmonies = self.ai_music.harmonize_note("C4", "octave")

        assert len(harmonies) == 2
        assert harmonies[0] == "C4"
        assert harmonies[1] == "C5"

    def test_harmonize_note_chord(self):
        """Test harmonizing with a full chord."""
        harmonies = self.ai_music.harmonize_note("C4", "chord")

        assert len(harmonies) == 3  # Root, third, fifth

    def test_analyze_notes_empty(self):
        """Test analyzing empty note list."""
        analysis = self.ai_music.analyze_notes([])

        assert "detected_key" in analysis
        assert "detected_scale" in analysis
        assert analysis["confidence"] == 0.0

    def test_analyze_notes_with_notes(self):
        """Test analyzing a list of notes."""
        notes = ["C4", "E4", "G4", "C4"]
        analysis = self.ai_music.analyze_notes(notes)

        assert "detected_key" in analysis
        assert "detected_scale" in analysis
        assert "suggestions" in analysis
        assert len(analysis["suggestions"]) > 0
