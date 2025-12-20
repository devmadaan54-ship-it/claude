'use client';

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Vote, ThumbsUp, ThumbsDown, Loader2 } from 'lucide-react';
import { ChatInterface } from '@/components/ChatInterface';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useLLMStream } from '@/hooks/useLLMStream';
import { cn, getModelColor } from '@/lib/utils';

interface VoteData {
  model: string;
  displayName: string;
  vote: 'Yes' | 'No';
  confidence: number;
  reasoning: string;
}

interface VotingResult {
  yesCount: number;
  noCount: number;
  consensus: 'Yes' | 'No' | 'Tie';
  averageConfidence: number;
  winnerReasoning: string;
}

export default function VotePage() {
  const [votes, setVotes] = useState<VoteData[]>([]);
  const [result, setResult] = useState<VotingResult | null>(null);

  const handleEvent = useCallback((event: any) => {
    if (event.event === 'vote') {
      setVotes((prev) => [
        ...prev,
        {
          model: event.model,
          displayName: event.display_name,
          vote: event.vote,
          confidence: event.confidence,
          reasoning: event.reasoning,
        },
      ]);
    } else if (event.event === 'result') {
      setResult({
        yesCount: event.yes_count,
        noCount: event.no_count,
        consensus: event.consensus,
        averageConfidence: event.average_confidence,
        winnerReasoning: event.winner_reasoning,
      });
    }
  }, []);

  const { isStreaming, error, startStream, stopStream } = useLLMStream({
    mode: 'vote',
    onEvent: handleEvent,
  });

  const handleSubmit = (query: string) => {
    setVotes([]);
    setResult(null);
    startStream(query);
  };

  return (
    <div className="min-h-screen flex flex-col p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-orange-500/10">
            <Vote className="h-6 w-6 text-orange-500" />
          </div>
          <h1 className="text-2xl font-bold">Consensus Voting</h1>
        </div>
        <p className="text-muted-foreground">
          Query 5 models with structured JSON output. Get confidence scores and mathematical majority.
        </p>
      </div>

      {/* Content Area */}
      <div className="flex-1 mb-6 max-w-4xl mx-auto w-full">
        <AnimatePresence mode="wait">
          {votes.length === 0 && !isStreaming ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex items-center justify-center"
            >
              <div className="text-center text-muted-foreground">
                <Vote className="h-16 w-16 mx-auto mb-4 opacity-20" />
                <p className="text-lg">Ask a Yes/No question</p>
                <p className="text-sm">
                  5 AI models will vote with confidence scores
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              {/* Result Summary */}
              {result && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <Card
                    className={cn(
                      'border-2',
                      result.consensus === 'Yes' &&
                        'border-green-500 bg-green-500/5',
                      result.consensus === 'No' &&
                        'border-red-500 bg-red-500/5',
                      result.consensus === 'Tie' &&
                        'border-yellow-500 bg-yellow-500/5'
                    )}
                  >
                    <CardContent className="py-6">
                      <div className="flex items-center justify-center gap-8">
                        {/* Yes Count */}
                        <div className="text-center">
                          <div className="flex items-center gap-2 justify-center mb-2">
                            <ThumbsUp className="h-8 w-8 text-green-500" />
                            <span className="text-4xl font-bold text-green-500">
                              {result.yesCount}
                            </span>
                          </div>
                          <span className="text-sm text-muted-foreground">
                            Yes Votes
                          </span>
                        </div>

                        {/* VS */}
                        <div className="text-2xl font-bold text-muted-foreground">
                          vs
                        </div>

                        {/* No Count */}
                        <div className="text-center">
                          <div className="flex items-center gap-2 justify-center mb-2">
                            <ThumbsDown className="h-8 w-8 text-red-500" />
                            <span className="text-4xl font-bold text-red-500">
                              {result.noCount}
                            </span>
                          </div>
                          <span className="text-sm text-muted-foreground">
                            No Votes
                          </span>
                        </div>
                      </div>

                      <div className="mt-6 text-center">
                        <div
                          className={cn(
                            'inline-block px-4 py-2 rounded-full font-medium',
                            result.consensus === 'Yes' &&
                              'bg-green-500 text-white',
                            result.consensus === 'No' &&
                              'bg-red-500 text-white',
                            result.consensus === 'Tie' &&
                              'bg-yellow-500 text-black'
                          )}
                        >
                          Consensus: {result.consensus}
                        </div>
                        <p className="mt-2 text-sm text-muted-foreground">
                          Average Confidence:{' '}
                          {(result.averageConfidence * 100).toFixed(0)}%
                        </p>
                        <p className="mt-2 text-sm max-w-md mx-auto">
                          {result.winnerReasoning}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              {/* Individual Votes */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {votes.map((vote, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <Card
                      className={cn(
                        'border-2',
                        vote.vote === 'Yes' &&
                          'border-green-500/50 bg-green-500/5',
                        vote.vote === 'No' && 'border-red-500/50 bg-red-500/5'
                      )}
                    >
                      <CardHeader className="py-3">
                        <CardTitle className="text-sm flex items-center justify-between">
                          <span className={getModelColor(vote.model)}>
                            {vote.displayName}
                          </span>
                          <div
                            className={cn(
                              'flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium',
                              vote.vote === 'Yes' &&
                                'bg-green-500/20 text-green-500',
                              vote.vote === 'No' && 'bg-red-500/20 text-red-500'
                            )}
                          >
                            {vote.vote === 'Yes' ? (
                              <ThumbsUp className="h-3 w-3" />
                            ) : (
                              <ThumbsDown className="h-3 w-3" />
                            )}
                            {vote.vote}
                          </div>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="mb-2">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-muted-foreground">
                              Confidence
                            </span>
                            <span className="font-medium">
                              {(vote.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className={cn(
                                'h-full transition-all duration-500',
                                vote.vote === 'Yes'
                                  ? 'bg-green-500'
                                  : 'bg-red-500'
                              )}
                              style={{ width: `${vote.confidence * 100}%` }}
                            />
                          </div>
                        </div>
                        <p className="text-xs text-muted-foreground line-clamp-2">
                          {vote.reasoning}
                        </p>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}

                {/* Loading placeholders */}
                {isStreaming &&
                  votes.length < 5 &&
                  Array.from({ length: 5 - votes.length }).map((_, i) => (
                    <Card
                      key={`loading-${i}`}
                      className="border-2 border-dashed"
                    >
                      <CardContent className="py-8 flex items-center justify-center">
                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                      </CardContent>
                    </Card>
                  ))}
              </div>
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
          placeholder="Ask a Yes/No question for the models to vote on..."
        />
      </div>
    </div>
  );
}
