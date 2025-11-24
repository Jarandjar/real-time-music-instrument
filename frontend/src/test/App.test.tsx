import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App', () => {
  it('should render the app header', () => {
    render(<App />);
    
    expect(screen.getByText(/Real-time AI Music Instrument/i)).toBeInTheDocument();
  });

  it('should render the instrument controls', () => {
    render(<App />);
    
    // Check for instrument buttons by their role
    const pianoButton = screen.getByRole('button', { name: /Piano/i });
    const synthButton = screen.getByRole('button', { name: /Synth/i });
    const stringsButton = screen.getByRole('button', { name: /Strings/i });
    const drumsButton = screen.getByRole('button', { name: /Drums/i });
    
    expect(pianoButton).toBeInTheDocument();
    expect(synthButton).toBeInTheDocument();
    expect(stringsButton).toBeInTheDocument();
    expect(drumsButton).toBeInTheDocument();
  });

  it('should render the suggestion button', () => {
    render(<App />);
    
    expect(screen.getByRole('button', { name: /Get Suggestion/i })).toBeInTheDocument();
  });

  it('should show the last played note', () => {
    render(<App />);
    
    expect(screen.getByText(/Last played/i)).toBeInTheDocument();
  });
});
