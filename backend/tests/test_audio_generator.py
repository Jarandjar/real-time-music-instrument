"""Tests for the audio generator service."""
import numpy as np
import pytest

from app.services.audio_generator import AudioGenerator, NOTE_FREQUENCIES


class TestAudioGenerator:
    """Test cases for AudioGenerator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = AudioGenerator(sample_rate=44100)

    def test_get_frequency_valid_note(self):
        """Test getting frequency for a valid note."""
        freq = self.generator.get_frequency("A4")
        assert freq == 440.0

    def test_get_frequency_with_sharp(self):
        """Test getting frequency for a sharp note."""
        freq = self.generator.get_frequency("C#4")
        assert freq == pytest.approx(277.18, rel=0.01)

    def test_get_frequency_invalid_note(self):
        """Test getting frequency for an invalid note raises error."""
        with pytest.raises(ValueError, match="Unknown note"):
            self.generator.get_frequency("X9")

    def test_get_frequency_case_insensitive(self):
        """Test that note lookup is case insensitive."""
        freq_lower = self.generator.get_frequency("c4")
        freq_upper = self.generator.get_frequency("C4")
        assert freq_lower == freq_upper

    def test_generate_sine_wave(self):
        """Test sine wave generation."""
        wave = self.generator.generate_sine_wave(440, 0.1, 0.5)

        # Check output is numpy array
        assert isinstance(wave, np.ndarray)

        # Check length matches expected samples
        expected_samples = int(44100 * 0.1)
        assert len(wave) == expected_samples

        # Check amplitude is within expected range
        assert np.max(np.abs(wave)) <= 0.5

    def test_generate_piano_tone(self):
        """Test piano tone generation."""
        wave = self.generator.generate_piano_tone(440, 0.5, 0.8)

        assert isinstance(wave, np.ndarray)
        assert len(wave) == int(44100 * 0.5)

    def test_generate_synth_tone(self):
        """Test synth tone generation."""
        wave = self.generator.generate_synth_tone(440, 0.5, 0.8)

        assert isinstance(wave, np.ndarray)
        assert len(wave) == int(44100 * 0.5)

    def test_generate_strings_tone(self):
        """Test strings tone generation."""
        wave = self.generator.generate_strings_tone(440, 0.5, 0.8)

        assert isinstance(wave, np.ndarray)
        assert len(wave) == int(44100 * 0.5)

    def test_generate_drums_tone(self):
        """Test drums tone generation."""
        wave = self.generator.generate_drums_tone(100, 0.5, 0.8)

        assert isinstance(wave, np.ndarray)
        assert len(wave) == int(44100 * 0.5)

    def test_generate_note_piano(self):
        """Test note generation for piano."""
        wave = self.generator.generate_note("C4", 0.5, 0.8, "piano")

        assert isinstance(wave, np.ndarray)
        assert len(wave) > 0

    def test_generate_note_unknown_instrument_defaults_to_piano(self):
        """Test that unknown instrument defaults to piano."""
        wave_unknown = self.generator.generate_note("C4", 0.5, 0.8, "unknown")
        wave_piano = self.generator.generate_note("C4", 0.5, 0.8, "piano")

        # Both should produce arrays of same length
        assert len(wave_unknown) == len(wave_piano)

    def test_apply_envelope(self):
        """Test ADSR envelope application."""
        samples = np.ones(44100)  # 1 second of samples
        enveloped = self.generator.apply_envelope(samples)

        # Envelope should modify the samples
        assert not np.array_equal(samples, enveloped)

        # Start should be near zero (attack)
        assert enveloped[0] < 0.1

        # End should be near zero (release)
        assert enveloped[-1] < 0.1

    def test_samples_to_wav_bytes(self):
        """Test WAV byte conversion."""
        samples = np.sin(np.linspace(0, 2 * np.pi, 1000))
        wav_bytes = self.generator.samples_to_wav_bytes(samples)

        # Check it starts with RIFF header
        assert wav_bytes[:4] == b"RIFF"

        # Check WAVE format
        assert wav_bytes[8:12] == b"WAVE"

    def test_samples_to_base64(self):
        """Test base64 encoding of audio."""
        samples = np.sin(np.linspace(0, 2 * np.pi, 1000))
        b64 = self.generator.samples_to_base64(samples)

        # Check it's a string
        assert isinstance(b64, str)

        # Check it's valid base64 (no exception on decode)
        import base64
        decoded = base64.b64decode(b64)
        assert decoded[:4] == b"RIFF"


class TestNoteFrequencies:
    """Test note frequency constants."""

    def test_a4_is_440(self):
        """Test that A4 is 440 Hz."""
        assert NOTE_FREQUENCIES["A4"] == 440.0

    def test_octave_doubles_frequency(self):
        """Test that each octave doubles the frequency."""
        # A3 should be half of A4
        assert NOTE_FREQUENCIES["A3"] == pytest.approx(
            NOTE_FREQUENCIES["A4"] / 2, rel=0.01
        )

        # A5 should be double A4
        assert NOTE_FREQUENCIES["A5"] == pytest.approx(
            NOTE_FREQUENCIES["A4"] * 2, rel=0.01
        )

    def test_all_notes_positive(self):
        """Test that all frequencies are positive."""
        for note, freq in NOTE_FREQUENCIES.items():
            assert freq > 0, f"Note {note} has non-positive frequency"
