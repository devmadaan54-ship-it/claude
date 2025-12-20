import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getModelDisplayName(model: string): string {
  const displayNames: Record<string, string> = {
    'gpt-4o': 'GPT-4o',
    'gpt-4o-mini': 'GPT-4o Mini',
    'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet',
    'claude-3-haiku-20240307': 'Claude 3 Haiku',
    'gemini-1.5-pro': 'Gemini 1.5 Pro',
    'gemini-1.5-flash': 'Gemini 1.5 Flash',
  };
  return displayNames[model] || model;
}

export function getModelColor(model: string): string {
  if (model.includes('gpt')) return 'text-green-500';
  if (model.includes('claude')) return 'text-orange-500';
  if (model.includes('gemini')) return 'text-blue-500';
  return 'text-gray-500';
}

export function getModelBgColor(model: string): string {
  if (model.includes('gpt')) return 'bg-green-500/10 border-green-500/20';
  if (model.includes('claude')) return 'bg-orange-500/10 border-orange-500/20';
  if (model.includes('gemini')) return 'bg-blue-500/10 border-blue-500/20';
  return 'bg-gray-500/10 border-gray-500/20';
}
