'use client';

import { useState, useCallback, useRef } from 'react';
import type { StreamEvent, QueryMode } from '@/types';

interface UseLLMStreamOptions {
  mode: QueryMode;
  onEvent?: (event: StreamEvent) => void;
  onComplete?: () => void;
  onError?: (error: Error) => void;
}

interface UseLLMStreamReturn {
  isStreaming: boolean;
  error: Error | null;
  startStream: (query: string, models?: string[]) => void;
  stopStream: () => void;
}

export function useLLMStream({
  mode,
  onEvent,
  onComplete,
  onError,
}: UseLLMStreamOptions): UseLLMStreamReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);

  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    if (readerRef.current) {
      readerRef.current.cancel();
      readerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const startStream = useCallback(
    async (query: string, models?: string[]) => {
      // Stop any existing stream
      stopStream();

      setIsStreaming(true);
      setError(null);

      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      try {
        const endpoint = `/api/${mode}/stream`;
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream',
          },
          body: JSON.stringify({
            query,
            mode,
            models: models || null,
            stream: true,
          }),
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        if (!response.body) {
          throw new Error('Response body is null');
        }

        const reader = response.body.getReader();
        readerRef.current = reader;
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          buffer += decoder.decode(value, { stream: true });

          // Process complete SSE messages
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim();
              if (data) {
                try {
                  const event: StreamEvent = JSON.parse(data);
                  onEvent?.(event);

                  if (event.event === 'done' || event.event === 'end') {
                    // Stream complete
                  }
                } catch (e) {
                  console.warn('Failed to parse SSE data:', data);
                }
              }
            }
          }
        }

        onComplete?.();
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          // Stream was intentionally stopped
          return;
        }
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        onError?.(error);
      } finally {
        setIsStreaming(false);
        abortControllerRef.current = null;
        readerRef.current = null;
      }
    },
    [mode, onEvent, onComplete, onError, stopStream]
  );

  return {
    isStreaming,
    error,
    startStream,
    stopStream,
  };
}

// Specialized hook for Hub mode with multiple streams
interface HubStreamState {
  index: number;
  model: string;
  displayName: string;
  content: string;
  status: 'pending' | 'streaming' | 'complete' | 'error';
}

interface UseHubStreamReturn {
  streams: HubStreamState[];
  isStreaming: boolean;
  error: Error | null;
  startStream: (query: string, models?: string[]) => void;
  stopStream: () => void;
}

export function useHubStream(): UseHubStreamReturn {
  const [streams, setStreams] = useState<HubStreamState[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const startStream = useCallback(async (query: string, models?: string[]) => {
    stopStream();
    setIsStreaming(true);
    setError(null);
    setStreams([]);

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      const response = await fetch('/api/hub/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify({
          query,
          mode: 'hub',
          models: models || null,
          stream: true,
        }),
        signal: abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data) {
              try {
                const event = JSON.parse(data);

                if (event.event === 'config') {
                  // Initialize all streams
                  setStreams(
                    event.streams.map((s: any) => ({
                      index: s.index,
                      model: s.model,
                      displayName: s.display_name,
                      content: '',
                      status: 'pending',
                    }))
                  );
                } else if (event.event === 'start') {
                  setStreams((prev) =>
                    prev.map((s) =>
                      s.index === event.index
                        ? { ...s, status: 'streaming' }
                        : s
                    )
                  );
                } else if (event.event === 'chunk') {
                  setStreams((prev) =>
                    prev.map((s) =>
                      s.index === event.index
                        ? { ...s, content: s.content + event.data }
                        : s
                    )
                  );
                } else if (event.event === 'end') {
                  setStreams((prev) =>
                    prev.map((s) =>
                      s.index === event.index
                        ? { ...s, status: 'complete' }
                        : s
                    )
                  );
                } else if (event.event === 'error') {
                  setStreams((prev) =>
                    prev.map((s) =>
                      s.index === event.index
                        ? { ...s, status: 'error', content: event.data }
                        : s
                    )
                  );
                }
              } catch (e) {
                console.warn('Failed to parse SSE data:', data);
              }
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') return;
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
    } finally {
      setIsStreaming(false);
    }
  }, [stopStream]);

  return {
    streams,
    isStreaming,
    error,
    startStream,
    stopStream,
  };
}
