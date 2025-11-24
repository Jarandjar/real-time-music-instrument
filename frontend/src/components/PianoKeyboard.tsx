import { useCallback, useEffect, useState } from 'react';
import type { InstrumentType } from '../types';
import { keyboardMapping } from '../utils/audio';
import './PianoKeyboard.css';

interface PianoKeyboardProps {
  onNotePlay: (note: string) => void;
  instrument: InstrumentType;
  suggestedNote?: string;
  activeNotes?: string[];
}

interface KeyInfo {
  note: string;
  isBlack: boolean;
  keyBinding?: string;
}

export function PianoKeyboard({
  onNotePlay,
  instrument,
  suggestedNote,
  activeNotes = [],
}: PianoKeyboardProps) {
  const [pressedKeys, setPressedKeys] = useState<Set<string>>(new Set());

  // Generate piano keys for octaves 3-5
  const generateKeys = (): KeyInfo[] => {
    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const keys: KeyInfo[] = [];

    for (let octave = 3; octave <= 5; octave++) {
      for (const note of notes) {
        const fullNote = `${note}${octave}`;
        const keyBinding = Object.entries(keyboardMapping).find(
          ([, n]) => n === fullNote
        )?.[0];

        keys.push({
          note: fullNote,
          isBlack: note.includes('#'),
          keyBinding,
        });
      }
    }

    return keys;
  };

  const keys = generateKeys();

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.repeat) return;

      const note = keyboardMapping[e.key.toLowerCase()];
      if (note && !pressedKeys.has(note)) {
        setPressedKeys((prev) => new Set(prev).add(note));
        onNotePlay(note);
      }
    },
    [onNotePlay, pressedKeys]
  );

  const handleKeyUp = useCallback((e: KeyboardEvent) => {
    const note = keyboardMapping[e.key.toLowerCase()];
    if (note) {
      setPressedKeys((prev) => {
        const next = new Set(prev);
        next.delete(note);
        return next;
      });
    }
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [handleKeyDown, handleKeyUp]);

  const handleMouseDown = (note: string) => {
    setPressedKeys((prev) => new Set(prev).add(note));
    onNotePlay(note);
  };

  const handleMouseUp = (note: string) => {
    setPressedKeys((prev) => {
      const next = new Set(prev);
      next.delete(note);
      return next;
    });
  };

  return (
    <div className="piano-container">
      <div className="instrument-label">{instrument.toUpperCase()}</div>
      <div className="keyboard">
        {keys.map((key) => (
          <div
            key={key.note}
            className={`key ${key.isBlack ? 'black' : 'white'} ${
              pressedKeys.has(key.note) || activeNotes.includes(key.note)
                ? 'pressed'
                : ''
            } ${suggestedNote === key.note ? 'suggested' : ''}`}
            onMouseDown={() => handleMouseDown(key.note)}
            onMouseUp={() => handleMouseUp(key.note)}
            onMouseLeave={() => handleMouseUp(key.note)}
          >
            <span className="key-label">{key.note}</span>
            {key.keyBinding && (
              <span className="key-binding">{key.keyBinding.toUpperCase()}</span>
            )}
          </div>
        ))}
      </div>
      <div className="keyboard-help">
        Use keyboard keys A-L and W-P to play notes
      </div>
    </div>
  );
}
