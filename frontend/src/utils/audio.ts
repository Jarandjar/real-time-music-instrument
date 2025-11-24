/**
 * Audio utility functions.
 */

/**
 * Convert base64-encoded WAV to AudioBuffer.
 */
export async function base64ToAudioBuffer(
  base64: string,
  audioContext: AudioContext
): Promise<AudioBuffer> {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return audioContext.decodeAudioData(bytes.buffer);
}

/**
 * Play an AudioBuffer.
 */
export function playAudioBuffer(
  audioBuffer: AudioBuffer,
  audioContext: AudioContext,
  gainValue = 0.8
): AudioBufferSourceNode {
  const source = audioContext.createBufferSource();
  const gainNode = audioContext.createGain();

  source.buffer = audioBuffer;
  gainNode.gain.value = gainValue;

  source.connect(gainNode);
  gainNode.connect(audioContext.destination);

  source.start(0);
  return source;
}

/**
 * Get the keyboard layout for a given octave range.
 */
export function getKeyboardLayout(startOctave: number, endOctave: number) {
  const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const keys: Array<{ note: string; isBlack: boolean }> = [];

  for (let octave = startOctave; octave <= endOctave; octave++) {
    for (const note of notes) {
      keys.push({
        note: `${note}${octave}`,
        isBlack: note.includes('#'),
      });
    }
  }

  return keys;
}

/**
 * Map keyboard keys to notes.
 */
export const keyboardMapping: Record<string, string> = {
  // White keys (lower row)
  'a': 'C4',
  's': 'D4',
  'd': 'E4',
  'f': 'F4',
  'g': 'G4',
  'h': 'A4',
  'j': 'B4',
  'k': 'C5',
  'l': 'D5',
  ';': 'E5',
  // Black keys (upper row)
  'w': 'C#4',
  'e': 'D#4',
  't': 'F#4',
  'y': 'G#4',
  'u': 'A#4',
  'o': 'C#5',
  'p': 'D#5',
};
