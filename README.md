# Real-time AI Music Instrument

A real-time AI-powered music instrument with a FastAPI backend and React frontend. Play music through an interactive piano keyboard interface with AI-powered suggestions for your next notes.

## Features

- 🎹 **Interactive Piano Keyboard** - Play notes using mouse clicks or keyboard keys
- 🎵 **Multiple Instruments** - Choose from Piano, Synth, Strings, and Drums
- 🤖 **AI Music Assistant** - Get intelligent suggestions for your next notes
- ⚡ **Real-time Audio** - WebSocket-based low-latency audio playback
- 🎼 **Music Theory Integration** - Scale-aware note suggestions and harmonization

## Project Structure

```
real-time-music-instrument/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API routes
│   │   └── services/       # Business logic
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
│
└── frontend/               # React frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── hooks/          # Custom hooks
    │   ├── types/          # TypeScript types
    │   └── utils/          # Utility functions
    └── package.json        # Node dependencies
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:5173

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `GET /health` - Health check
- `POST /music/note` - Play a note
- `GET /music/note/{note}/audio` - Get audio for a note
- `GET /music/scale/{root}` - Get scale notes
- `POST /music/suggest` - Get AI note suggestion
- `GET /music/melody` - Generate an AI melody
- `WS /ws` - WebSocket for real-time audio

## WebSocket Messages

### Play a Note
```json
{
  "type": "play_note",
  "note": "C4",
  "duration": 0.5,
  "velocity": 0.8,
  "instrument": "piano"
}
```

### Get Suggestion
```json
{
  "type": "get_suggestion",
  "current_note": "C4"
}
```

### Harmonize
```json
{
  "type": "harmonize",
  "note": "C4",
  "harmony_type": "chord"
}
```

## Keyboard Controls

| Key | Note | Key | Note |
|-----|------|-----|------|
| A   | C4   | W   | C#4  |
| S   | D4   | E   | D#4  |
| D   | E4   | T   | F#4  |
| F   | F4   | Y   | G#4  |
| G   | G4   | U   | A#4  |
| H   | A4   | O   | C#5  |
| J   | B4   | P   | D#5  |
| K   | C5   |     |      |
| L   | D5   |     |      |
| ;   | E5   |     |      |

## Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Technologies

### Backend
- FastAPI - Modern Python web framework
- WebSockets - Real-time communication
- NumPy - Audio signal processing
- Pydantic - Data validation

### Frontend
- React 19 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Web Audio API - Audio playback

## License

MIT License - see [LICENSE](LICENSE) for details.