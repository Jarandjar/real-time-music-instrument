"""Pydantic models for the music instrument API."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class InstrumentType(str, Enum):
    """Available instrument types."""

    PIANO = "piano"
    SYNTH = "synth"
    STRINGS = "strings"
    DRUMS = "drums"


class NoteRequest(BaseModel):
    """Request model for playing a note."""

    note: str = Field(..., description="Musical note (e.g., 'C4', 'A#3')")
    velocity: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Note velocity (0.0-1.0)"
    )
    duration: float = Field(
        default=0.5, ge=0.0, le=10.0, description="Note duration in seconds"
    )
    instrument: InstrumentType = Field(
        default=InstrumentType.PIANO, description="Instrument type"
    )


class NoteResponse(BaseModel):
    """Response model for note generation."""

    note: str
    frequency: float
    samples: int
    message: str


class AudioSettings(BaseModel):
    """Audio settings configuration."""

    sample_rate: int = Field(default=44100, description="Sample rate in Hz")
    channels: int = Field(default=1, ge=1, le=2, description="Number of channels")
    bit_depth: int = Field(default=16, description="Bit depth")


class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    type: str = Field(..., description="Message type")
    data: Optional[dict] = Field(default=None, description="Message data")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
