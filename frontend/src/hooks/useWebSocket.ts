import { useCallback, useEffect, useRef, useState } from 'react';
import type { WebSocketMessage } from '../types';
import { base64ToAudioBuffer, playAudioBuffer } from '../utils/audio';

interface UseWebSocketReturn {
  isConnected: boolean;
  sendMessage: (message: object) => void;
  lastMessage: WebSocketMessage | null;
  playNote: (note: string, duration?: number, velocity?: number, instrument?: string) => void;
  getSuggestion: (currentNote: string) => void;
  harmonize: (note: string, harmonyType?: string) => void;
}

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export function useWebSocket(): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // Initialize AudioContext
  useEffect(() => {
    audioContextRef.current = new AudioContext();
    return () => {
      audioContextRef.current?.close();
    };
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = window.setTimeout(connect, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onmessage = async (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setLastMessage(message);

        // Handle audio messages
        if (message.type === 'audio' && message.audio && audioContextRef.current) {
          const audioBuffer = await base64ToAudioBuffer(
            message.audio,
            audioContextRef.current
          );
          playAudioBuffer(audioBuffer, audioContextRef.current);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    wsRef.current = ws;
  }, []);

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((message: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const playNote = useCallback(
    (note: string, duration = 0.5, velocity = 0.8, instrument = 'piano') => {
      sendMessage({
        type: 'play_note',
        note,
        duration,
        velocity,
        instrument,
      });
    },
    [sendMessage]
  );

  const getSuggestion = useCallback(
    (currentNote: string) => {
      sendMessage({
        type: 'get_suggestion',
        current_note: currentNote,
      });
    },
    [sendMessage]
  );

  const harmonize = useCallback(
    (note: string, harmonyType = 'third') => {
      sendMessage({
        type: 'harmonize',
        note,
        harmony_type: harmonyType,
      });
    },
    [sendMessage]
  );

  return {
    isConnected,
    sendMessage,
    lastMessage,
    playNote,
    getSuggestion,
    harmonize,
  };
}
