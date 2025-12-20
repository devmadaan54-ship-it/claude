'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Grid3X3, Loader2 } from 'lucide-react';
import { ChatInterface } from '@/components/ChatInterface';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useHubStream } from '@/hooks/useLLMStream';
import { cn, getModelColor, getModelBgColor } from '@/lib/utils';

export default function HubPage() {
  const { streams, isStreaming, error, startStream, stopStream } = useHubStream();
  const [hasQueried, setHasQueried] = useState(false);

  const handleSubmit = (query: string) => {
    setHasQueried(true);
    startStream(query);
  };

  return (
    <div className="min-h-screen flex flex-col p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-green-500/10">
            <Grid3X3 className="h-6 w-6 text-green-500" />
          </div>
          <h1 className="text-2xl font-bold">The Hub</h1>
        </div>
        <p className="text-muted-foreground">
          Fan-out architecture: Query 6 models simultaneously with real-time parallel streaming.
        </p>
      </div>

      {/* Grid View */}
      <div className="flex-1 mb-6">
        {!hasQueried ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <Grid3X3 className="h-16 w-16 mx-auto mb-4 opacity-20" />
              <p className="text-lg">Enter a query to see 6 models respond in parallel</p>
              <p className="text-sm">All responses stream simultaneously and independently</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 h-full">
            <AnimatePresence mode="wait">
              {streams.length === 0 && isStreaming ? (
                // Loading placeholder
                Array.from({ length: 6 }).map((_, i) => (
                  <motion.div
                    key={`placeholder-${i}`}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    <Card className="h-64 flex items-center justify-center">
                      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </Card>
                  </motion.div>
                ))
              ) : (
                streams.map((stream, i) => (
                  <motion.div
                    key={stream.index}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    <Card
                      className={cn(
                        'h-64 flex flex-col overflow-hidden border-2 transition-colors',
                        stream.status === 'streaming' && 'border-primary/50',
                        stream.status === 'complete' && 'border-green-500/30',
                        stream.status === 'error' && 'border-red-500/30',
                        getModelBgColor(stream.model)
                      )}
                    >
                      <CardHeader className="py-3 px-4 border-b border-border/50">
                        <CardTitle className="text-sm flex items-center justify-between">
                          <span className={getModelColor(stream.model)}>
                            {stream.displayName}
                          </span>
                          <StatusIndicator status={stream.status} />
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="flex-1 p-4 overflow-auto">
                        <pre className="text-sm whitespace-pre-wrap font-sans">
                          {stream.content}
                          {stream.status === 'streaming' && (
                            <span className="inline-block w-2 h-4 bg-primary ml-0.5 animate-pulse" />
                          )}
                        </pre>
                        {stream.status === 'pending' && (
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            <span className="text-sm">Waiting...</span>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500">
          {error.message}
        </div>
      )}

      {/* Chat Input */}
      <div className="max-w-3xl mx-auto w-full">
        <ChatInterface
          onSubmit={handleSubmit}
          isLoading={isStreaming}
          onStop={stopStream}
          placeholder="Ask a question to see 6 models respond in parallel..."
        />
      </div>
    </div>
  );
}

function StatusIndicator({ status }: { status: string }) {
  switch (status) {
    case 'pending':
      return (
        <span className="flex items-center gap-1 text-xs text-muted-foreground">
          <span className="w-2 h-2 rounded-full bg-muted-foreground animate-pulse" />
          Waiting
        </span>
      );
    case 'streaming':
      return (
        <span className="flex items-center gap-1 text-xs text-primary">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          Streaming
        </span>
      );
    case 'complete':
      return (
        <span className="flex items-center gap-1 text-xs text-green-500">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          Complete
        </span>
      );
    case 'error':
      return (
        <span className="flex items-center gap-1 text-xs text-red-500">
          <span className="w-2 h-2 rounded-full bg-red-500" />
          Error
        </span>
      );
    default:
      return null;
  }
}
