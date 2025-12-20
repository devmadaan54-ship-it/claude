'use client';

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, User, Scale, Crown, Loader2 } from 'lucide-react';
import { ChatInterface } from '@/components/ChatInterface';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useLLMStream } from '@/hooks/useLLMStream';
import { cn, getModelColor } from '@/lib/utils';

interface DebateStep {
  step: number;
  name: string;
  role: string;
  model: string;
  content: string;
  status: 'pending' | 'streaming' | 'complete';
}

const roleIcons: Record<string, React.ElementType> = {
  'Advocate A': User,
  'Advocate B': User,
  Critic: Scale,
  Chairman: Crown,
};

const roleColors: Record<string, string> = {
  'Advocate A': 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  'Advocate B': 'text-green-500 bg-green-500/10 border-green-500/20',
  Critic: 'text-orange-500 bg-orange-500/10 border-orange-500/20',
  Chairman: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
};

export default function DebatePage() {
  const [steps, setSteps] = useState<DebateStep[]>([]);
  const [currentStep, setCurrentStep] = useState<number | null>(null);

  const handleEvent = useCallback((event: any) => {
    if (event.event === 'step_start') {
      setCurrentStep(event.step);
      setSteps((prev) => [
        ...prev,
        {
          step: event.step,
          name: event.name,
          role: event.role,
          model: event.model,
          content: '',
          status: 'streaming',
        },
      ]);
    } else if (event.event === 'chunk' && event.step !== undefined) {
      setSteps((prev) =>
        prev.map((s) =>
          s.step === event.step
            ? { ...s, content: s.content + (event.data || '') }
            : s
        )
      );
    } else if (event.event === 'step_end') {
      setSteps((prev) =>
        prev.map((s) =>
          s.step === event.step ? { ...s, status: 'complete' } : s
        )
      );
    }
  }, []);

  const { isStreaming, error, startStream, stopStream } = useLLMStream({
    mode: 'debate',
    onEvent: handleEvent,
  });

  const handleSubmit = (query: string) => {
    setSteps([]);
    setCurrentStep(null);
    startStream(query);
  };

  return (
    <div className="min-h-screen flex flex-col p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-blue-500/10">
            <Users className="h-6 w-6 text-blue-500" />
          </div>
          <h1 className="text-2xl font-bold">The Council</h1>
        </div>
        <p className="text-muted-foreground">
          Multi-step debate system: Two advocates argue, a critic analyzes, and a chairman delivers the verdict.
        </p>
      </div>

      {/* Content Area */}
      <div className="flex-1 mb-6 max-w-4xl mx-auto w-full overflow-y-auto">
        <AnimatePresence mode="wait">
          {steps.length === 0 && !isStreaming ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex items-center justify-center"
            >
              <div className="text-center text-muted-foreground">
                <Users className="h-16 w-16 mx-auto mb-4 opacity-20" />
                <p className="text-lg">Start a council debate</p>
                <p className="text-sm">
                  Watch as AI models argue, critique, and reach a final verdict
                </p>
                <div className="flex items-center justify-center gap-4 mt-6">
                  {Object.entries(roleIcons).map(([role, Icon]) => (
                    <div
                      key={role}
                      className={cn(
                        'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm border',
                        roleColors[role]
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      <span>{role}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-4"
            >
              {/* Timeline */}
              <div className="flex items-center justify-center gap-2 mb-6">
                {[1, 2, 3, 4].map((stepNum) => {
                  const step = steps.find((s) => s.step === stepNum);
                  const isComplete = step?.status === 'complete';
                  const isCurrent = stepNum === currentStep;

                  return (
                    <React.Fragment key={stepNum}>
                      <div
                        className={cn(
                          'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
                          isComplete && 'bg-green-500 text-white',
                          isCurrent && 'bg-primary text-primary-foreground',
                          !isComplete && !isCurrent && 'bg-muted text-muted-foreground'
                        )}
                      >
                        {isCurrent ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          stepNum
                        )}
                      </div>
                      {stepNum < 4 && (
                        <div
                          className={cn(
                            'w-12 h-0.5',
                            isComplete ? 'bg-green-500' : 'bg-muted'
                          )}
                        />
                      )}
                    </React.Fragment>
                  );
                })}
              </div>

              {/* Debate Steps */}
              {steps.map((step, i) => {
                const Icon = roleIcons[step.role] || User;

                return (
                  <motion.div
                    key={step.step}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <Card
                      className={cn(
                        'border-2 transition-all',
                        roleColors[step.role],
                        step.status === 'streaming' && 'shadow-lg'
                      )}
                    >
                      <CardHeader className="py-3">
                        <CardTitle className="text-sm flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Icon className="h-5 w-5" />
                            <span>{step.role}</span>
                            <span className="text-muted-foreground">•</span>
                            <span className="text-muted-foreground font-normal">
                              {step.name}
                            </span>
                          </div>
                          <span className={cn('text-xs', getModelColor(step.model))}>
                            {step.model}
                          </span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <pre className="text-sm whitespace-pre-wrap font-sans">
                          {step.content}
                          {step.status === 'streaming' && (
                            <span className="inline-block w-2 h-4 bg-primary ml-0.5 animate-pulse" />
                          )}
                        </pre>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
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
          placeholder="Pose a question for the council to debate..."
        />
      </div>
    </div>
  );
}
