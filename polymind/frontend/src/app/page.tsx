'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  Zap,
  Layers,
  Users,
  Grid3X3,
  Vote,
  ArrowRight,
  Brain,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const modes = [
  {
    name: 'Auto-Router',
    description: 'Intelligent intent classification that automatically routes your query to the optimal model.',
    href: '/router',
    icon: Zap,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-500/10',
  },
  {
    name: 'Synthesizer',
    description: 'Query multiple top-tier models in parallel and merge their insights into one master answer.',
    href: '/synthesizer',
    icon: Layers,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
  },
  {
    name: 'Council',
    description: 'Multi-step debate system where models argue, critique, and a chairman delivers the verdict.',
    href: '/debate',
    icon: Users,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
  },
  {
    name: 'Hub',
    description: 'Fan-out to 6 models simultaneously with real-time parallel streaming in a grid view.',
    href: '/hub',
    icon: Grid3X3,
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
  },
  {
    name: 'Voting',
    description: 'Structured consensus voting with confidence scores and mathematical majority.',
    href: '/vote',
    icon: Vote,
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
  },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function Home() {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Brain className="h-12 w-12 text-primary" />
            <h1 className="text-4xl font-bold">PolyMind</h1>
          </div>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Production-grade LLM Orchestration Platform with multi-model routing,
            synthesis, debate, and consensus voting.
          </p>
        </motion.div>

        {/* Mode Cards */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {modes.map((mode) => {
            const Icon = mode.icon;
            return (
              <motion.div key={mode.name} variants={item}>
                <Link href={mode.href}>
                  <Card className="h-full transition-all hover:shadow-lg hover:border-primary/50 cursor-pointer group">
                    <CardHeader>
                      <div className={`inline-flex p-3 rounded-lg ${mode.bgColor} w-fit mb-2`}>
                        <Icon className={`h-6 w-6 ${mode.color}`} />
                      </div>
                      <CardTitle className="flex items-center gap-2">
                        {mode.name}
                        <ArrowRight className="h-4 w-4 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                      </CardTitle>
                      <CardDescription>{mode.description}</CardDescription>
                    </CardHeader>
                  </Card>
                </Link>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Quick Start */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center"
        >
          <p className="text-muted-foreground mb-4">
            Get started by selecting a mode from the sidebar or clicking a card above.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link href="/hub">
              <Button size="lg">
                <Grid3X3 className="mr-2 h-5 w-5" />
                Try Hub Mode
              </Button>
            </Link>
            <Link href="/settings">
              <Button variant="outline" size="lg">
                Configure API Keys
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
