/**
 * Types for the music instrument application.
 */

export type InstrumentType = 'piano' | 'synth' | 'strings' | 'drums';

export interface NoteData {
  note: string;
  frequency: number;
  samples: number;
  message: string;
}

export interface AudioResponse {
  note: string;
  audio: string;
  format: string;
  encoding: string;
}

export interface WebSocketMessage {
  type: string;
  data?: unknown;
  note?: string;
  audio?: string;
  message?: string;
  suggested_note?: string;
  notes?: string[];
  current_note?: string;
}

export interface MelodyNote {
  note: string;
  duration: number;
  velocity: number;
}

export interface ScaleData {
  root: string;
  scale_type: string;
  octave: number;
  notes: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
}

export interface KeyboardKey {
  note: string;
  isBlack: boolean;
  position: number;
}
