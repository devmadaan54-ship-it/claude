'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, StopCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ChatInterfaceProps {
  onSubmit: (query: string) => void;
  isLoading?: boolean;
  onStop?: () => void;
  placeholder?: string;
  disabled?: boolean;
}

export function ChatInterface({
  onSubmit,
  isLoading = false,
  onStop,
  placeholder = 'Ask anything...',
  disabled = false,
}: ChatInterfaceProps) {
  const [query, setQuery] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [query]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading && !disabled) {
      onSubmit(query.trim());
      setQuery('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="relative flex items-end gap-2 rounded-xl border border-border bg-background p-3 shadow-lg"
    >
      <textarea
        ref={textareaRef}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={isLoading || disabled}
        rows={1}
        className="min-h-[40px] max-h-[200px] flex-1 resize-none bg-transparent px-2 py-1.5 text-sm placeholder:text-muted-foreground focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
      />

      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="stop"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
          >
            <Button
              type="button"
              size="icon"
              variant="destructive"
              onClick={onStop}
              className="h-10 w-10 rounded-lg"
            >
              <StopCircle className="h-5 w-5" />
            </Button>
          </motion.div>
        ) : (
          <motion.div
            key="send"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
          >
            <Button
              type="submit"
              size="icon"
              disabled={!query.trim() || disabled}
              className="h-10 w-10 rounded-lg"
            >
              <Send className="h-5 w-5" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </form>
  );
}

// Response display component with markdown support
interface ResponseDisplayProps {
  content: string;
  isStreaming?: boolean;
  model?: string;
  className?: string;
}

export function ResponseDisplay({
  content,
  isStreaming = false,
  model,
  className,
}: ResponseDisplayProps) {
  return (
    <div
      className={cn(
        'rounded-lg border border-border bg-muted/50 p-4',
        className
      )}
    >
      {model && (
        <div className="mb-2 text-xs font-medium text-muted-foreground">
          {model}
        </div>
      )}
      <div className="prose prose-sm dark:prose-invert max-w-none">
        <pre className="whitespace-pre-wrap font-sans text-sm">
          {content}
          {isStreaming && (
            <span className="inline-block h-4 w-1 animate-pulse bg-primary ml-0.5" />
          )}
        </pre>
      </div>
    </div>
  );
}

// Loading skeleton
export function ResponseSkeleton() {
  return (
    <div className="rounded-lg border border-border bg-muted/50 p-4">
      <div className="space-y-3">
        <div className="h-4 w-3/4 animate-pulse rounded bg-muted-foreground/20" />
        <div className="h-4 w-full animate-pulse rounded bg-muted-foreground/20" />
        <div className="h-4 w-2/3 animate-pulse rounded bg-muted-foreground/20" />
      </div>
    </div>
  );
}
