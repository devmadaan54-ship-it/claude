'use client';

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, ArrowRight, Code, Sparkles, Brain, BookOpen } from 'lucide-react';
import { ChatInterface, ResponseDisplay } from '@/components/ChatInterface';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useLLMStream } from '@/hooks/useLLMStream';
import { cn } from '@/lib/utils';

interface RouterState {
  intent: string | null;
  model: string | null;
  reasoning: string | null;
  content: string;
}

const intentIcons: Record<string, React.ElementType> = {
  coding: Code,
  creative: Sparkles,
  reasoning: Brain,
  factual: BookOpen,
};

const intentColors: Record<string, string> = {
  coding: 'text-green-500 bg-green-500/10',
  creative: 'text-purple-500 bg-purple-500/10',
  reasoning: 'text-blue-500 bg-blue-500/10',
  factual: 'text-orange-500 bg-orange-500/10',
};

export default function RouterPage() {
  const [state, setState] = useState<RouterState>({
    intent: null,
    model: null,
    reasoning: null,
    content: '',
  });

  const handleEvent = useCallback((event: any) => {
    if (event.event === 'routing') {
      setState((prev) => ({
        ...prev,
        intent: event.intent,
        model: event.model,
        reasoning: event.reasoning,
      }));
    } else if (event.event === 'chunk') {
      setState((prev) => ({
        ...prev,
        content: prev.content + (event.data || ''),
      }));
    }
  }, []);

  const { isStreaming, error, startStream, stopStream } = useLLMStream({
    mode: 'router',
    onEvent: handleEvent,
  });

  const handleSubmit = (query: string) => {
    setState({ intent: null, model: null, reasoning: null, content: '' });
    startStream(query);
  };

  const IntentIcon = state.intent ? intentIcons[state.intent] || Zap : Zap;

  return (
    <div className="min-h-screen flex flex-col p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-yellow-500/10">
            <Zap className="h-6 w-6 text-yellow-500" />
          </div>
          <h1 className="text-2xl font-bold">Auto-Router</h1>
        </div>
        <p className="text-muted-foreground">
          Intelligent intent classification that automatically routes your query to the optimal model.
        </p>
      </div>

      {/* Content Area */}
      <div className="flex-1 mb-6 max-w-4xl mx-auto w-full">
        <AnimatePresence mode="wait">
          {!state.intent && !isStreaming ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex items-center justify-center"
            >
              <div className="text-center text-muted-foreground">
                <Zap className="h-16 w-16 mx-auto mb-4 opacity-20" />
                <p className="text-lg">Ask any question</p>
                <p className="text-sm">The router will classify your intent and select the best model</p>
                <div className="flex items-center justify-center gap-4 mt-6">
                  {Object.entries(intentIcons).map(([intent, Icon]) => (
                    <div
                      key={intent}
                      className={cn(
                        'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm',
                        intentColors[intent]
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      <span className="capitalize">{intent}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              {/* Routing Info */}
              {state.intent && (
                <Card className="border-primary/20">
                  <CardContent className="py-4">
                    <div className="flex items-center gap-4">
                      <div
                        className={cn(
                          'p-3 rounded-lg',
                          intentColors[state.intent]
                        )}
                      >
                        <IntentIcon className="h-6 w-6" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span className="capitalize font-medium">
                            {state.intent}
                          </span>
                          <ArrowRight className="h-4 w-4" />
                          <span className="text-primary font-medium">
                            {state.model}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {state.reasoning}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Response */}
              {(state.content || isStreaming) && (
                <ResponseDisplay
                  content={state.content}
                  isStreaming={isStreaming}
                  model={state.model || undefined}
                />
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
          placeholder="Ask anything - I'll route it to the best model..."
        />
      </div>
    </div>
  );
}
