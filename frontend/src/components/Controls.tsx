import type { InstrumentType } from '../types';
import './Controls.css';

interface ControlsProps {
  instrument: InstrumentType;
  onInstrumentChange: (instrument: InstrumentType) => void;
  isConnected: boolean;
  onGetSuggestion: () => void;
  suggestedNote?: string;
}

const INSTRUMENTS: InstrumentType[] = ['piano', 'synth', 'strings', 'drums'];

export function Controls({
  instrument,
  onInstrumentChange,
  isConnected,
  onGetSuggestion,
  suggestedNote,
}: ControlsProps) {
  return (
    <div className="controls">
      <div className="control-group">
        <label>Instrument</label>
        <div className="instrument-buttons">
          {INSTRUMENTS.map((inst) => (
            <button
              key={inst}
              className={`instrument-btn ${inst === instrument ? 'active' : ''}`}
              onClick={() => onInstrumentChange(inst)}
            >
              {inst.charAt(0).toUpperCase() + inst.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="control-group">
        <label>AI Assistant</label>
        <button
          className="suggestion-btn"
          onClick={onGetSuggestion}
          disabled={!isConnected}
        >
          Get Suggestion
        </button>
        {suggestedNote && (
          <div className="suggestion-display">
            Suggested: <strong>{suggestedNote}</strong>
          </div>
        )}
      </div>

      <div className="connection-status">
        <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`} />
        {isConnected ? 'Connected' : 'Disconnected'}
      </div>
    </div>
  );
}
