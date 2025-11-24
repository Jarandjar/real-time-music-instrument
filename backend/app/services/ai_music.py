"""AI Music service for generating musical patterns and harmonies."""
import random
from typing import List, Tuple

from app.services.audio_generator import NOTE_FREQUENCIES


class AIMusic:
    """AI-powered music generation service."""

    # Common chord progressions
    CHORD_PROGRESSIONS = {
        "pop": ["C", "G", "Am", "F"],
        "jazz": ["Dm7", "G7", "Cmaj7", "Fmaj7"],
        "blues": ["A", "D", "A", "E"],
        "classical": ["C", "F", "G", "C"],
    }

    # Scale patterns (intervals from root)
    SCALES = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "pentatonic": [0, 2, 4, 7, 9],
        "blues": [0, 3, 5, 6, 7, 10],
    }

    # Note names
    NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def __init__(self):
        """Initialize the AI music service."""
        self.current_key = "C"
        self.current_scale = "major"
        self.current_octave = 4

    def get_scale_notes(
        self, root: str = "C", scale_type: str = "major", octave: int = 4
    ) -> List[str]:
        """Get notes in a scale.

        Args:
            root: Root note of the scale.
            scale_type: Type of scale.
            octave: Starting octave.

        Returns:
            List of note names with octaves.
        """
        if scale_type not in self.SCALES:
            scale_type = "major"

        # Clean up root note
        root_clean = root.upper()
        is_sharp = "#" in root_clean
        base_note = root_clean.replace("#", "").replace("B", "")
        
        # Handle empty base note
        if not base_note or base_note not in self.NOTE_NAMES:
            base_note = "C"
            is_sharp = False
        
        root_index = self.NOTE_NAMES.index(base_note)
        if is_sharp:
            root_index = (root_index + 1) % 12

        intervals = self.SCALES[scale_type]
        notes = []

        for interval in intervals:
            note_index = (root_index + interval) % 12
            note_name = self.NOTE_NAMES[note_index]
            note_octave = octave + (root_index + interval) // 12
            notes.append(f"{note_name}{note_octave}")

        return notes

    def suggest_next_note(
        self,
        current_note: str,
        scale_type: str = "major",
        style: str = "melodic",
    ) -> str:
        """Suggest the next note based on musical theory.

        Args:
            current_note: Current note being played.
            scale_type: Type of scale to use.
            style: Playing style (melodic, random, stepwise).

        Returns:
            Suggested next note.
        """
        # Extract note and octave
        note_name = current_note[:-1].upper()
        try:
            octave = int(current_note[-1])
        except (ValueError, IndexError):
            octave = 4

        # Get scale notes - extract root note (first letter, possibly with #)
        if len(note_name) >= 1:
            root = note_name[0]  # Get first character as root
        else:
            root = "C"  # Default to C
        scale_notes = self.get_scale_notes(root, scale_type, octave)

        if style == "stepwise":
            # Move by step (up or down)
            try:
                current_idx = scale_notes.index(current_note)
                next_idx = current_idx + random.choice([-1, 1])
                next_idx = max(0, min(next_idx, len(scale_notes) - 1))
                return scale_notes[next_idx]
            except ValueError:
                return random.choice(scale_notes)

        elif style == "melodic":
            # Favor consonant intervals
            weights = [0.3, 0.15, 0.15, 0.1, 0.1, 0.1, 0.1]
            if len(scale_notes) < len(weights):
                weights = weights[: len(scale_notes)]
            return random.choices(scale_notes, weights=weights)[0]

        else:
            # Random note from scale
            return random.choice(scale_notes)

    def generate_melody(
        self,
        length: int = 8,
        root: str = "C",
        scale_type: str = "major",
        octave: int = 4,
    ) -> List[Tuple[str, float, float]]:
        """Generate a simple melody.

        Args:
            length: Number of notes in the melody.
            root: Root note of the scale.
            scale_type: Type of scale.
            octave: Starting octave.

        Returns:
            List of tuples (note, duration, velocity).
        """
        scale_notes = self.get_scale_notes(root, scale_type, octave)
        melody = []

        current_note = random.choice(scale_notes[:3])  # Start on tonic area

        for i in range(length):
            # Vary duration
            duration = random.choice([0.25, 0.5, 0.5, 1.0])

            # Vary velocity for expression
            velocity = random.uniform(0.6, 0.9)

            melody.append((current_note, duration, velocity))

            # Get next note
            current_note = self.suggest_next_note(
                current_note, scale_type, "melodic"
            )

        return melody

    def harmonize_note(
        self, note: str, harmony_type: str = "third"
    ) -> List[str]:
        """Add harmony to a note.

        Args:
            note: Base note to harmonize.
            harmony_type: Type of harmony (third, fifth, octave, chord).

        Returns:
            List of notes including harmony.
        """
        note_name = note[:-1].upper()
        try:
            octave = int(note[-1])
        except (ValueError, IndexError):
            octave = 4

        try:
            note_index = self.NOTE_NAMES.index(note_name)
        except ValueError:
            return [note]

        harmonies = [note]

        if harmony_type == "third":
            # Major third (4 semitones)
            third_index = (note_index + 4) % 12
            third_octave = octave + (note_index + 4) // 12
            harmonies.append(f"{self.NOTE_NAMES[third_index]}{third_octave}")

        elif harmony_type == "fifth":
            # Perfect fifth (7 semitones)
            fifth_index = (note_index + 7) % 12
            fifth_octave = octave + (note_index + 7) // 12
            harmonies.append(f"{self.NOTE_NAMES[fifth_index]}{fifth_octave}")

        elif harmony_type == "octave":
            harmonies.append(f"{note_name}{octave + 1}")

        elif harmony_type == "chord":
            # Major triad
            third_index = (note_index + 4) % 12
            fifth_index = (note_index + 7) % 12
            harmonies.append(f"{self.NOTE_NAMES[third_index]}{octave}")
            harmonies.append(f"{self.NOTE_NAMES[fifth_index]}{octave}")

        return harmonies

    def analyze_notes(self, notes: List[str]) -> dict:
        """Analyze a sequence of notes.

        Args:
            notes: List of note names.

        Returns:
            Analysis dictionary with key, scale, and suggestions.
        """
        if not notes:
            return {
                "detected_key": "C",
                "detected_scale": "major",
                "confidence": 0.0,
                "suggestions": [],
            }

        # Count note occurrences
        note_counts = {}
        for note in notes:
            note_name = note[:-1].upper() if note[-1].isdigit() else note.upper()
            note_counts[note_name] = note_counts.get(note_name, 0) + 1

        # Simple key detection based on most common notes
        most_common = sorted(note_counts.items(), key=lambda x: -x[1])
        detected_key = most_common[0][0] if most_common else "C"

        return {
            "detected_key": detected_key,
            "detected_scale": "major",
            "confidence": 0.7,
            "suggestions": [
                f"Try adding a {detected_key} chord",
                "Consider varying the rhythm",
                "Add some passing tones for interest",
            ],
        }


# Singleton instance
ai_music = AIMusic()
