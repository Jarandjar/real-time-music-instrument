"""Music API router for note generation and playback."""
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    InstrumentType,
    NoteRequest,
    NoteResponse,
)
from app.services.audio_generator import audio_generator
from app.services.ai_music import ai_music

router = APIRouter(prefix="/music", tags=["music"])


@router.post("/note", response_model=NoteResponse)
async def play_note(request: NoteRequest) -> NoteResponse:
    """Generate and return audio for a single note.

    Args:
        request: Note request with note, velocity, duration, and instrument.

    Returns:
        Note response with frequency and sample information.

    Raises:
        HTTPException: If the note is invalid.
    """
    try:
        frequency = audio_generator.get_frequency(request.note)
        samples = audio_generator.generate_note(
            note=request.note,
            duration=request.duration,
            velocity=request.velocity,
            instrument=request.instrument.value,
        )

        return NoteResponse(
            note=request.note,
            frequency=frequency,
            samples=len(samples),
            message=f"Generated {request.note} at {frequency:.2f}Hz",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/note/{note}/audio")
async def get_note_audio(
    note: str,
    duration: float = 0.5,
    velocity: float = 0.8,
    instrument: InstrumentType = InstrumentType.PIANO,
) -> dict:
    """Get base64-encoded audio for a note.

    Args:
        note: Musical note (e.g., 'C4').
        duration: Note duration in seconds.
        velocity: Note velocity (0.0-1.0).
        instrument: Instrument type.

    Returns:
        Dictionary with base64-encoded WAV audio.

    Raises:
        HTTPException: If the note is invalid.
    """
    try:
        samples = audio_generator.generate_note(
            note=note,
            duration=duration,
            velocity=velocity,
            instrument=instrument.value,
        )
        audio_base64 = audio_generator.samples_to_base64(samples)

        return {
            "note": note,
            "audio": audio_base64,
            "format": "wav",
            "encoding": "base64",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/scale/{root}")
async def get_scale(
    root: str,
    scale_type: str = "major",
    octave: int = 4,
) -> dict:
    """Get notes in a musical scale.

    Args:
        root: Root note of the scale.
        scale_type: Type of scale (major, minor, pentatonic, blues).
        octave: Starting octave.

    Returns:
        Dictionary with scale notes.
    """
    notes = ai_music.get_scale_notes(root, scale_type, octave)
    return {
        "root": root,
        "scale_type": scale_type,
        "octave": octave,
        "notes": notes,
    }


@router.post("/suggest")
async def suggest_next_note(
    current_note: str,
    scale_type: str = "major",
    style: str = "melodic",
) -> dict:
    """Get AI suggestion for the next note.

    Args:
        current_note: Current note being played.
        scale_type: Type of scale.
        style: Playing style.

    Returns:
        Dictionary with suggested note.
    """
    suggestion = ai_music.suggest_next_note(current_note, scale_type, style)
    return {
        "current_note": current_note,
        "suggested_note": suggestion,
        "scale_type": scale_type,
        "style": style,
    }


@router.post("/harmonize")
async def harmonize_note(
    note: str,
    harmony_type: str = "third",
) -> dict:
    """Add harmony to a note.

    Args:
        note: Base note to harmonize.
        harmony_type: Type of harmony.

    Returns:
        Dictionary with harmonized notes.
    """
    harmonies = ai_music.harmonize_note(note, harmony_type)
    return {
        "base_note": note,
        "harmony_type": harmony_type,
        "notes": harmonies,
    }


@router.get("/melody")
async def generate_melody(
    length: int = 8,
    root: str = "C",
    scale_type: str = "major",
    octave: int = 4,
) -> dict:
    """Generate an AI melody.

    Args:
        length: Number of notes.
        root: Root note.
        scale_type: Scale type.
        octave: Starting octave.

    Returns:
        Dictionary with melody notes.
    """
    melody = ai_music.generate_melody(length, root, scale_type, octave)
    return {
        "root": root,
        "scale_type": scale_type,
        "melody": [
            {"note": note, "duration": dur, "velocity": vel}
            for note, dur, vel in melody
        ],
    }


@router.get("/instruments")
async def list_instruments() -> dict:
    """List available instruments.

    Returns:
        Dictionary with available instruments.
    """
    return {
        "instruments": [instrument.value for instrument in InstrumentType],
    }
