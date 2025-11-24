"""Main FastAPI application for Real-time AI Music Instrument."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import HealthResponse
from app.routers import music, websocket

# Application metadata
APP_TITLE = "Real-time AI Music Instrument"
APP_DESCRIPTION = """
A real-time AI-powered music instrument that generates audio in real-time.

## Features

* **Real-time Audio Generation** - Generate audio samples for various instruments
* **WebSocket Support** - Real-time bidirectional communication for low-latency playback
* **AI Music Assistance** - Get suggestions for next notes, harmonies, and melodies
* **Multiple Instruments** - Piano, synth, strings, and drums

## Instruments

* `piano` - Realistic piano sounds with harmonics
* `synth` - Synthesizer tones
* `strings` - String instrument sounds with vibrato
* `drums` - Percussion sounds
"""
APP_VERSION = "1.0.0"

# Create FastAPI application
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(music.router)
app.include_router(websocket.router)


@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint returning API information.

    Returns:
        Dictionary with API information.
    """
    return {
        "name": APP_TITLE,
        "version": APP_VERSION,
        "docs": "/docs",
        "websocket": "/ws",
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        Health status response.
    """
    return HealthResponse(status="healthy", version=APP_VERSION)
