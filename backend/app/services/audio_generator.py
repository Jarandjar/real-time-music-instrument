"""Audio generation service for real-time music synthesis."""
import base64
import struct
from typing import Dict

import numpy as np

# Musical note frequencies (A4 = 440 Hz)
NOTE_FREQUENCIES: Dict[str, float] = {
    "C0": 16.35, "C#0": 17.32, "D0": 18.35, "D#0": 19.45, "E0": 20.60,
    "F0": 21.83, "F#0": 23.12, "G0": 24.50, "G#0": 25.96, "A0": 27.50,
    "A#0": 29.14, "B0": 30.87,
    "C1": 32.70, "C#1": 34.65, "D1": 36.71, "D#1": 38.89, "E1": 41.20,
    "F1": 43.65, "F#1": 46.25, "G1": 49.00, "G#1": 51.91, "A1": 55.00,
    "A#1": 58.27, "B1": 61.74,
    "C2": 65.41, "C#2": 69.30, "D2": 73.42, "D#2": 77.78, "E2": 82.41,
    "F2": 87.31, "F#2": 92.50, "G2": 98.00, "G#2": 103.83, "A2": 110.00,
    "A#2": 116.54, "B2": 123.47,
    "C3": 130.81, "C#3": 138.59, "D3": 146.83, "D#3": 155.56, "E3": 164.81,
    "F3": 174.61, "F#3": 185.00, "G3": 196.00, "G#3": 207.65, "A3": 220.00,
    "A#3": 233.08, "B3": 246.94,
    "C4": 261.63, "C#4": 277.18, "D4": 293.66, "D#4": 311.13, "E4": 329.63,
    "F4": 349.23, "F#4": 369.99, "G4": 392.00, "G#4": 415.30, "A4": 440.00,
    "A#4": 466.16, "B4": 493.88,
    "C5": 523.25, "C#5": 554.37, "D5": 587.33, "D#5": 622.25, "E5": 659.25,
    "F5": 698.46, "F#5": 739.99, "G5": 783.99, "G#5": 830.61, "A5": 880.00,
    "A#5": 932.33, "B5": 987.77,
    "C6": 1046.50, "C#6": 1108.73, "D6": 1174.66, "D#6": 1244.51, "E6": 1318.51,
    "F6": 1396.91, "F#6": 1479.98, "G6": 1567.98, "G#6": 1661.22, "A6": 1760.00,
    "A#6": 1864.66, "B6": 1975.53,
    "C7": 2093.00, "C#7": 2217.46, "D7": 2349.32, "D#7": 2489.02, "E7": 2637.02,
    "F7": 2793.83, "F#7": 2959.96, "G7": 3135.96, "G#7": 3322.44, "A7": 3520.00,
    "A#7": 3729.31, "B7": 3951.07,
    "C8": 4186.01,
}


class AudioGenerator:
    """Generates audio samples for different instruments."""

    def __init__(self, sample_rate: int = 44100):
        """Initialize the audio generator.

        Args:
            sample_rate: Audio sample rate in Hz.
        """
        self.sample_rate = sample_rate

    def get_frequency(self, note: str) -> float:
        """Get the frequency for a musical note.

        Args:
            note: Musical note string (e.g., 'C4', 'A#3').

        Returns:
            Frequency in Hz.

        Raises:
            ValueError: If the note is not recognized.
        """
        note_upper = note.upper()
        if note_upper not in NOTE_FREQUENCIES:
            raise ValueError(f"Unknown note: {note}")
        return NOTE_FREQUENCIES[note_upper]

    def generate_sine_wave(
        self,
        frequency: float,
        duration: float,
        amplitude: float = 0.8,
    ) -> np.ndarray:
        """Generate a sine wave.

        Args:
            frequency: Frequency in Hz.
            duration: Duration in seconds.
            amplitude: Wave amplitude (0.0-1.0).

        Returns:
            NumPy array of audio samples.
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = amplitude * np.sin(2 * np.pi * frequency * t)
        return wave

    def apply_envelope(
        self,
        samples: np.ndarray,
        attack: float = 0.01,
        decay: float = 0.1,
        sustain: float = 0.7,
        release: float = 0.1,
    ) -> np.ndarray:
        """Apply ADSR envelope to audio samples.

        Args:
            samples: Audio samples.
            attack: Attack time in seconds.
            decay: Decay time in seconds.
            sustain: Sustain level (0.0-1.0).
            release: Release time in seconds.

        Returns:
            Audio samples with envelope applied.
        """
        total_samples = len(samples)
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)

        envelope = np.ones(total_samples)

        # Attack phase
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay phase
        decay_end = attack_samples + decay_samples
        if decay_samples > 0 and decay_end <= total_samples:
            envelope[attack_samples:decay_end] = np.linspace(1, sustain, decay_samples)

        # Sustain phase
        sustain_end = total_samples - release_samples
        if sustain_end > decay_end:
            envelope[decay_end:sustain_end] = sustain

        # Release phase
        if release_samples > 0 and sustain_end < total_samples:
            envelope[sustain_end:] = np.linspace(
                sustain, 0, total_samples - sustain_end
            )

        return samples * envelope

    def generate_piano_tone(
        self,
        frequency: float,
        duration: float,
        velocity: float = 0.8,
    ) -> np.ndarray:
        """Generate a piano-like tone with harmonics.

        Args:
            frequency: Fundamental frequency in Hz.
            duration: Duration in seconds.
            velocity: Note velocity (0.0-1.0).

        Returns:
            NumPy array of audio samples.
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        # Add harmonics for richer sound
        wave = np.zeros_like(t)
        harmonics = [1.0, 0.5, 0.25, 0.125, 0.0625]

        for i, amp in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            if harmonic_freq < self.sample_rate / 2:  # Nyquist limit
                wave += amp * np.sin(2 * np.pi * harmonic_freq * t)

        # Normalize and apply velocity
        wave = wave / np.max(np.abs(wave)) * velocity

        # Apply piano-like envelope
        return self.apply_envelope(
            wave, attack=0.005, decay=0.2, sustain=0.5, release=0.3
        )

    def generate_synth_tone(
        self,
        frequency: float,
        duration: float,
        velocity: float = 0.8,
    ) -> np.ndarray:
        """Generate a synthesizer tone.

        Args:
            frequency: Fundamental frequency in Hz.
            duration: Duration in seconds.
            velocity: Note velocity (0.0-1.0).

        Returns:
            NumPy array of audio samples.
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        # Sawtooth wave for synth sound
        wave = 2 * (t * frequency - np.floor(0.5 + t * frequency))
        wave = wave * velocity

        return self.apply_envelope(
            wave, attack=0.02, decay=0.1, sustain=0.8, release=0.2
        )

    def generate_strings_tone(
        self,
        frequency: float,
        duration: float,
        velocity: float = 0.8,
    ) -> np.ndarray:
        """Generate a strings-like tone.

        Args:
            frequency: Fundamental frequency in Hz.
            duration: Duration in seconds.
            velocity: Note velocity (0.0-1.0).

        Returns:
            NumPy array of audio samples.
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        # Layered sine waves with vibrato
        vibrato_freq = 5  # Hz
        vibrato_depth = 0.005

        freq_mod = frequency * (1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t))
        wave = np.sin(2 * np.pi * np.cumsum(freq_mod) / self.sample_rate)
        wave = wave * velocity

        return self.apply_envelope(
            wave, attack=0.1, decay=0.1, sustain=0.9, release=0.3
        )

    def generate_drums_tone(
        self,
        frequency: float,
        duration: float,
        velocity: float = 0.8,
    ) -> np.ndarray:
        """Generate a drum-like sound.

        Args:
            frequency: Fundamental frequency in Hz.
            duration: Duration in seconds.
            velocity: Note velocity (0.0-1.0).

        Returns:
            NumPy array of audio samples.
        """
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)

        # Noise component for attack
        noise = np.random.uniform(-1, 1, num_samples)

        # Decaying sine wave for body
        decay = np.exp(-10 * t)
        body = np.sin(2 * np.pi * frequency * t) * decay

        # Combine
        wave = (0.3 * noise * np.exp(-30 * t) + 0.7 * body) * velocity

        return self.apply_envelope(
            wave, attack=0.001, decay=0.05, sustain=0.2, release=0.1
        )

    def generate_note(
        self,
        note: str,
        duration: float = 0.5,
        velocity: float = 0.8,
        instrument: str = "piano",
    ) -> np.ndarray:
        """Generate audio samples for a musical note.

        Args:
            note: Musical note string (e.g., 'C4').
            duration: Duration in seconds.
            velocity: Note velocity (0.0-1.0).
            instrument: Instrument type.

        Returns:
            NumPy array of audio samples.
        """
        frequency = self.get_frequency(note)

        generators = {
            "piano": self.generate_piano_tone,
            "synth": self.generate_synth_tone,
            "strings": self.generate_strings_tone,
            "drums": self.generate_drums_tone,
        }

        generator = generators.get(instrument.lower(), self.generate_piano_tone)
        return generator(frequency, duration, velocity)

    def samples_to_wav_bytes(self, samples: np.ndarray) -> bytes:
        """Convert audio samples to WAV format bytes.

        Args:
            samples: NumPy array of audio samples (-1.0 to 1.0).

        Returns:
            WAV file bytes.
        """
        # Convert to 16-bit PCM
        samples_int16 = (samples * 32767).astype(np.int16)

        # Create WAV header
        num_samples = len(samples_int16)
        data_size = num_samples * 2  # 16-bit = 2 bytes per sample
        file_size = 36 + data_size

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            file_size,
            b"WAVE",
            b"fmt ",
            16,  # fmt chunk size
            1,  # PCM format
            1,  # mono
            self.sample_rate,
            self.sample_rate * 2,  # byte rate
            2,  # block align
            16,  # bits per sample
            b"data",
            data_size,
        )

        return header + samples_int16.tobytes()

    def samples_to_base64(self, samples: np.ndarray) -> str:
        """Convert audio samples to base64-encoded WAV.

        Args:
            samples: NumPy array of audio samples.

        Returns:
            Base64-encoded WAV data.
        """
        wav_bytes = self.samples_to_wav_bytes(samples)
        return base64.b64encode(wav_bytes).decode("utf-8")


# Singleton instance
audio_generator = AudioGenerator()
