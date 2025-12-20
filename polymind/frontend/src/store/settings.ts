'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsState {
  // API Keys
  openaiApiKey: string;
  anthropicApiKey: string;
  googleApiKey: string;
  groqApiKey: string;

  // Mode settings
  mockMode: boolean;

  // Selected models (for custom overrides)
  selectedModels: Record<string, string[]>;

  // Actions
  setApiKey: (provider: string, key: string) => void;
  setMockMode: (enabled: boolean) => void;
  setSelectedModels: (mode: string, models: string[]) => void;
  syncWithBackend: () => Promise<void>;
}

export const useSettings = create<SettingsState>()(
  persist(
    (set, get) => ({
      openaiApiKey: '',
      anthropicApiKey: '',
      googleApiKey: '',
      groqApiKey: '',
      mockMode: true,
      selectedModels: {},

      setApiKey: (provider, key) => {
        const updates: Partial<SettingsState> = {};
        switch (provider) {
          case 'openai':
            updates.openaiApiKey = key;
            break;
          case 'anthropic':
            updates.anthropicApiKey = key;
            break;
          case 'google':
            updates.googleApiKey = key;
            break;
          case 'groq':
            updates.groqApiKey = key;
            break;
        }
        set(updates);
      },

      setMockMode: (enabled) => set({ mockMode: enabled }),

      setSelectedModels: (mode, models) =>
        set((state) => ({
          selectedModels: { ...state.selectedModels, [mode]: models },
        })),

      syncWithBackend: async () => {
        const state = get();
        try {
          await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              openai_api_key: state.openaiApiKey || null,
              anthropic_api_key: state.anthropicApiKey || null,
              google_api_key: state.googleApiKey || null,
              groq_api_key: state.groqApiKey || null,
              mock_mode: state.mockMode,
            }),
          });
        } catch (error) {
          console.error('Failed to sync settings with backend:', error);
        }
      },
    }),
    {
      name: 'polymind-settings',
      partialize: (state) => ({
        openaiApiKey: state.openaiApiKey,
        anthropicApiKey: state.anthropicApiKey,
        googleApiKey: state.googleApiKey,
        groqApiKey: state.groqApiKey,
        mockMode: state.mockMode,
        selectedModels: state.selectedModels,
      }),
    }
  )
);
