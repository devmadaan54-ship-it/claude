'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Zap,
  Layers,
  Users,
  Grid3X3,
  Vote,
  Settings,
  Brain,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  description: string;
  color: string;
}

const navItems: NavItem[] = [
  {
    name: 'Auto-Router',
    href: '/router',
    icon: Zap,
    description: 'Intelligent model selection',
    color: 'text-yellow-500',
  },
  {
    name: 'Synthesizer',
    href: '/synthesizer',
    icon: Layers,
    description: 'Parallel merge responses',
    color: 'text-purple-500',
  },
  {
    name: 'Council',
    href: '/debate',
    icon: Users,
    description: 'Multi-model debate',
    color: 'text-blue-500',
  },
  {
    name: 'Hub',
    href: '/hub',
    icon: Grid3X3,
    description: '6-grid matrix streaming',
    color: 'text-green-500',
  },
  {
    name: 'Voting',
    href: '/vote',
    icon: Vote,
    description: 'Consensus voting',
    color: 'text-orange-500',
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 border-b border-border px-6">
          <Brain className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold">PolyMind</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 rounded-lg bg-primary/10"
                    transition={{ type: 'spring', duration: 0.5 }}
                  />
                )}
                <Icon className={cn('h-5 w-5 relative z-10', item.color)} />
                <div className="relative z-10">
                  <div>{item.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {item.description}
                  </div>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Settings */}
        <div className="border-t border-border p-3">
          <Link
            href="/settings"
            className={cn(
              'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
              pathname === '/settings'
                ? 'bg-primary/10 text-primary'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
            )}
          >
            <Settings className="h-5 w-5" />
            <span>Settings</span>
          </Link>
        </div>
      </div>
    </aside>
  );
}
