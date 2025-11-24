import '@testing-library/jest-dom';

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.OPEN;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(_url: string) {
    // Store url to avoid unused variable warning
    void _url;
    setTimeout(() => {
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
      if (this.onmessage) {
        this.onmessage(new MessageEvent('message', {
          data: JSON.stringify({ type: 'connected', message: 'Connected' })
        }));
      }
    }, 0);
  }

  send(_data: string) {
    // Mock send - void to indicate intentionally unused
    void _data;
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
  }
}

// @ts-expect-error - Mocking global WebSocket
globalThis.WebSocket = MockWebSocket;

// Mock AudioContext
class MockAudioContext {
  destination = {};
  createBufferSource() {
    return {
      buffer: null,
      connect: () => {},
      start: () => {},
    };
  }
  createGain() {
    return {
      gain: { value: 1 },
      connect: () => {},
    };
  }
  decodeAudioData() {
    return Promise.resolve({});
  }
  close() {
    return Promise.resolve();
  }
}

// @ts-expect-error - Mocking global AudioContext
globalThis.AudioContext = MockAudioContext;
