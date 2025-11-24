import { useCallback, useMemo, useState } from 'react';
import { PianoKeyboard } from './components/PianoKeyboard';
import { Controls } from './components/Controls';
import { useWebSocket } from './hooks/useWebSocket';
import type { InstrumentType } from './types';
import './App.css';

function App() {
  const [instrument, setInstrument] = useState<InstrumentType>('piano');
  const [lastNote, setLastNote] = useState<string>('C4');
  const { isConnected, playNote, getSuggestion, lastMessage } = useWebSocket();

  // Derive suggested note from lastMessage
  const suggestedNote = useMemo(() => {
    if (lastMessage?.type === 'suggestion' && lastMessage.suggested_note) {
      return lastMessage.suggested_note;
    }
    return undefined;
  }, [lastMessage]);

  const handleNotePlay = useCallback(
    (note: string) => {
      setLastNote(note);
      playNote(note, 0.5, 0.8, instrument);
    },
    [playNote, instrument]
  );

  const handleGetSuggestion = useCallback(() => {
    getSuggestion(lastNote);
  }, [getSuggestion, lastNote]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎹 Real-time AI Music Instrument</h1>
        <p>Play music in real-time with AI-powered suggestions</p>
      </header>

      <main className="app-main">
        <Controls
          instrument={instrument}
          onInstrumentChange={setInstrument}
          isConnected={isConnected}
          onGetSuggestion={handleGetSuggestion}
          suggestedNote={suggestedNote}
        />

        <PianoKeyboard
          onNotePlay={handleNotePlay}
          instrument={instrument}
          suggestedNote={suggestedNote}
        />

        <div className="note-display">
          Last played: <strong>{lastNote}</strong>
        </div>
      </main>

      <footer className="app-footer">
        <p>Use your keyboard or click the keys to play. Press any key to get AI suggestions!</p>
      </footer>
    </div>
  );
}

export default App;
