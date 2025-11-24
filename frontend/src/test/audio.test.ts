import { describe, it, expect } from 'vitest';
import { getKeyboardLayout, keyboardMapping } from '../utils/audio';

describe('Audio Utils', () => {
  describe('getKeyboardLayout', () => {
    it('should generate keyboard layout for a given octave range', () => {
      const keys = getKeyboardLayout(4, 4);
      
      expect(keys).toHaveLength(12);
      expect(keys[0].note).toBe('C4');
      expect(keys[0].isBlack).toBe(false);
      expect(keys[1].note).toBe('C#4');
      expect(keys[1].isBlack).toBe(true);
    });

    it('should generate correct number of keys for multiple octaves', () => {
      const keys = getKeyboardLayout(3, 5);
      
      expect(keys).toHaveLength(36); // 12 notes * 3 octaves
    });
  });

  describe('keyboardMapping', () => {
    it('should have valid note mappings', () => {
      expect(keyboardMapping['a']).toBe('C4');
      expect(keyboardMapping['s']).toBe('D4');
      expect(keyboardMapping['w']).toBe('C#4');
    });

    it('should map black keys correctly', () => {
      expect(keyboardMapping['w']).toContain('#');
      expect(keyboardMapping['e']).toContain('#');
    });
  });
});
