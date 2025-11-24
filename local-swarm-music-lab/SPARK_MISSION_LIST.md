# Spark Mission List – Real-Time AI Music Instrument

Reference blueprint: `local-swarm-music-lab/REAL_TIME_AI_MUSIC_INSTRUMENT.md`. Each mission below can be assigned to Spark AI or tackled manually; acceptance checks keep scope verifiable.

## Mission 1 – Core Spec & Data Structures
- [ ] **Define `StyleProfile` schema** in Python (pydantic/dataclass) and JSON Schema form. Fields: `guitar`, `drums`, `harmony`, `rhythm`, `arrangement`, `lead`, `dynamics`. Sliders are floats 0–1, dropdowns are enums, toggles booleans. Include `energyCurve` placeholder (array of `{ "beat": int, "value": float }`).
- [ ] **Emit preset JSON files** under `local-swarm-music-lab/style_profiles/`: `southern_rock_free_bird_like.json`, `spacey_floyd_like.json`, `metal_80s_chug.json`, `lofi_chill.json`. Each must conform to schema and cite source inspiration in a `meta.notes` block.
- [ ] **Session state struct** (`session_state.py`): `sessionId`, `currentStyleProfile`, `currentSection`, `currentKey`, `currentTempo`, `barCounter`, `energyPosition`, plus timestamps. Include helper to advance sections.

*Acceptance:* Schema passes validation tests; presets load via schema; session struct round-trips through `json.dumps()`.

## Mission 2 – Backend APIs (FastAPI skeleton)
- [ ] `/analyze-style` (POST): accept audio upload, return hardcoded StyleProfile + `analysisNotes` explaining placeholder status.
- [ ] `/session` (POST): start session from StyleProfile or preset name; store in in-memory registry.
- [ ] `/session/{id}/style` (PATCH): merge partial JSON (deep merge); return updated profile hash.
- [ ] `/session/{id}/generate-bar` (POST/GET): respond with `{ barNumber, tempo, midiEventsByTrack }`; use deterministic patterns for now.
- [ ] `/session/{id}/section` (POST): update `currentSection` + adjust engine hints.
- [ ] `/session/{id}/stop` (DELETE): remove registry entry, return summary log.

*Acceptance:* Add pytest covering happy-path for each endpoint; in-memory registry cleared when stopping session.

## Mission 3 – Rule-Based Music Engine (MVP)
- [ ] Implement `ChordEngine` with mode presets (rock-blues, modal, jazz) and `chordChangeRate` weighting; expose `next_bar_chords(state)`.
- [ ] Add per-track generators: `DrumPattern`, `BassLine`, `RhythmGuitar`, `LeadLine`. Map style sliders → behavior (e.g., `drums.humanization` → timing jitter, `lead.soloIntensity` → notes/bar & pitch span).
- [ ] Encode "section scripts" (intro/verse/build/solo) per arrangement preset; tie into energy curve to scale layer counts and velocities.
- [ ] Provide `generate_bar(style, state)` orchestrator returning normalized MIDI event list.

*Acceptance:* Unit tests prove slider extremes change output stats (e.g., soloIntensity=1.0 ⇒ ≥8 notes/bar). Generators deterministic under seeded RNG.

## Mission 4 – Audio Rendering & Scheduling
- [ ] Define internal MIDI event schema `{ track, channel, note, velocity, start_beats, duration_beats }` used everywhere.
- [ ] Integrate FluidSynth (server-side) to render each bar into WAV/OGG chunks; configurable soundfont per track.
- [ ] Implement bar scheduler buffering 1–2 bars ahead; expose `/session/{id}/stream` (Server-Sent Events or WebSocket) to send audio+MIDI.
- [ ] Provide CLI `python run_demo.py --preset southern_rock_free_bird_like --bars 32` exporting stems to `outputs/demo/`.

*Acceptance:* Manual demo command generates audio without glitches; latency metrics logged (<250 ms generation per bar on dev GPU/CPU).

## Mission 5 – Frontend / Spark GUI
- [ ] Build StyleProfile editor (tabs for Guitar, Drums, Harmony, Rhythm, Arrangement, Lead, Dynamics) with synchronized slider/dropdown/toggle components.
- [ ] Preset selector (Southern Rock Ballad/Jam, Psychedelic Space Rock, Lo-fi Chill Beat) loading JSON files via new `/presets` endpoint or static bundle.
- [ ] Style Mixer XY pad blending two profiles + conservative↔experimental axis; use weighted interpolation per field.
- [ ] Transport controls (Play/Stop, Next Section, Cue Solo) hitting `/session`, `/generate-bar`, `/section`.
- [ ] Visualizer: rolling piano-roll/drum grid for last N bars + energy curve overlay.

*Acceptance:* Cypress/e2e test ensures UI sends PATCH updates and receives bar streams; visualizer updates within 500 ms of new bar message.

## Mission 6 – Style Analysis & Copyright Guardrails
- [ ] Extend `/analyze-style` to call Essentia + Basic Pitch (behind feature flag). Map BPM → tempo, dynamic range → `microDynamics`, onset curves → `energyCurve`, chord stats → harmony sliders.
- [ ] Enforce "high-level features only": discard raw audio after analysis, return aggregate metrics, log compliance.
- [ ] UI copy update: “Upload your own track to craft a preset. We only extract tempo/chord/dynamics, audio stays local.”
- [ ] Add unit test verifying analyzer output never includes audio samples or raw MIDI blobs.

*Acceptance:* Running analyzer on sample WAV outputs deterministic StyleProfile snippet; logs prove audio deleted immediately.

## Mission 7 – Dev Experience, Tests, & Local Mode
- [ ] Add pytest suite for style→engine mappings, section transitions, registry lifecycle.
- [ ] Implement `demo_mode.py` CLI: "Generate 32-bar Southern Rock Jam" end-to-end (analysis skipped).
- [ ] Structured logging per bar (style snapshot, section, timing). Include latency + buffer depth metrics.
- [ ] Document "local-only" workflow in `README` (backend + FluidSynth + React dev server on one machine); provide VS Code launch tasks.

*Acceptance:* CI job runs engine/unit tests; demo mode produces audio & logs; README section verified by teammate following steps.
