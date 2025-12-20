'use client';

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, CheckCircle2, Loader2 } from 'lucide-react';
import { ChatInterface, ResponseDisplay } from '@/components/ChatInterface';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useLLMStream } from '@/hooks/useLLMStream';
import { cn, getModelColor } from '@/lib/utils';

interface SynthesisState {
  phase: string;
  message: string;
  responses: Array<{ model: string; preview: string }>;
  synthesizedContent: string;
  synthesizerModel: string | null;
}

export default function SynthesizerPage() {
  const [state, setState] = useState<SynthesisState>({
    phase: '',
    message: '',
    responses: [],
    synthesizedContent: '',
    synthesizerModel: null,
  });

  const handleEvent = useCallback((event: any) => {
    if (event.event === 'phase') {
      setState((prev) => ({
        ...prev,
        phase: event.phase,
        message: event.message,
      }));
    } else if (event.event === 'response') {
      setState((prev) => ({
        ...prev,
        responses: [
          ...prev.responses,
          { model: event.model, preview: event.preview },
        ],
      }));
    } else if (event.event === 'start') {
      setState((prev) => ({
        ...prev,
        synthesizerModel: event.model,
      }));
    } else if (event.event === 'chunk') {
      setState((prev) => ({
        ...prev,
        synthesizedContent: prev.synthesizedContent + (event.data || ''),
      }));
    }
  }, []);

  const { isStreaming, error, startStream, stopStream } = useLLMStream({
    mode: 'synthesizer',
    onEvent: handleEvent,
  });

  const handleSubmit = (query: string) => {
    setState({
      phase: '',
      message: '',
      responses: [],
      synthesizedContent: '',
      synthesizerModel: null,
    });
    startStream(query);
  };

  return (
    <div className="min-h-screen flex flex-col p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-purple-500/10">
            <Layers className="h-6 w-6 text-purple-500" />
          </div>
          <h1 className="text-2xl font-bold">The Synthesizer</h1>
        </div>
        <p className="text-muted-foreground">
          Query multiple top-tier models in parallel and merge their insights into one master answer.
        </p>
      </div>

      {/* Content Area */}
      <div className="flex-1 mb-6 max-w-4xl mx-auto w-full">
        <AnimatePresence mode="wait">
          {!state.phase && !isStreaming ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex items-center justify-center"
            >
              <div className="text-center text-muted-foreground">
                <Layers className="h-16 w-16 mx-auto mb-4 opacity-20" />
                <p className="text-lg">Get the best of multiple AI models</p>
                <p className="text-sm">
                  GPT-4o, Claude 3.5, and Gemini 1.5 will answer, then their responses are synthesized
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              {/* Progress Timeline */}
              <Card className="border-primary/20">
                <CardContent className="py-4">
                  <div className="flex items-center gap-4">
                    <PhaseIndicator
                      phase="querying"
                      currentPhase={state.phase}
                      label="Querying Models"
                    />
                    <div className="flex-1 h-0.5 bg-border" />
                    <PhaseIndicator
                      phase="collected"
                      currentPhase={state.phase}
                      label="Responses Collected"
                    />
                    <div className="flex-1 h-0.5 bg-border" />
                    <PhaseIndicator
                      phase="synthesizing"
                      currentPhase={state.phase}
                      label="Synthesizing"
                    />
                  </div>
                  {state.message && (
                    <p className="text-sm text-muted-foreground mt-3 text-center">
                      {state.message}
                    </p>
                  )}
                </CardContent>
              </Card>

              {/* Individual Responses Preview */}
              {state.responses.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {state.responses.map((resp, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.1 }}
                    >
                      <Card className="h-32">
                        <CardHeader className="py-2 px-3">
                          <CardTitle
                            className={cn('text-xs', getModelColor(resp.model))}
                          >
                            {resp.model}
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="px-3 pb-3">
                          <p className="text-xs text-muted-foreground line-clamp-3">
                            {resp.preview}
                          </p>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              )}

              {/* Synthesized Response */}
              {(state.synthesizedContent || state.phase === 'synthesizing') && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium mb-2 flex items-center gap-2">
                    <Layers className="h-4 w-4 text-purple-500" />
                    Synthesized Response
                  </h3>
                  <ResponseDisplay
                    content={state.synthesizedContent}
                    isStreaming={isStreaming && state.phase === 'synthesizing'}
                    model={state.synthesizerModel || undefined}
                  />
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 max-w-4xl mx-auto w-full">
          {error.message}
        </div>
      )}

      {/* Chat Input */}
      <div className="max-w-3xl mx-auto w-full">
        <ChatInterface
          onSubmit={handleSubmit}
          isLoading={isStreaming}
          onStop={stopStream}
          placeholder="Ask a question to synthesize answers from 3 top models..."
        />
      </div>
    </div>
  );
}

function PhaseIndicator({
  phase,
  currentPhase,
  label,
}: {
  phase: string;
  currentPhase: string;
  label: string;
}) {
  const phases = ['querying', 'collected', 'synthesizing'];
  const currentIndex = phases.indexOf(currentPhase);
  const thisIndex = phases.indexOf(phase);

  const isComplete = thisIndex < currentIndex;
  const isCurrent = phase === currentPhase;

  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center',
          isComplete && 'bg-green-500 text-white',
          isCurrent && 'bg-primary text-primary-foreground',
          !isComplete && !isCurrent && 'bg-muted text-muted-foreground'
        )}
      >
        {isComplete ? (
          <CheckCircle2 className="h-5 w-5" />
        ) : isCurrent ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : (
          <span className="text-sm">{thisIndex + 1}</span>
        )}
      </div>
      <span className="text-xs text-muted-foreground text-center max-w-[80px]">
        {label}
      </span>
    </div>
  );
}
