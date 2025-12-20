'use client';

import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Settings, Eye, EyeOff, Check, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useSettings } from '@/store/settings';
import { cn } from '@/lib/utils';

const providers = [
  {
    id: 'openai',
    name: 'OpenAI',
    description: 'GPT-4o, GPT-4o-mini',
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    description: 'Claude 3.5 Sonnet, Claude 3 Haiku',
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
  },
  {
    id: 'google',
    name: 'Google',
    description: 'Gemini 1.5 Pro, Gemini 1.5 Flash',
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
  },
  {
    id: 'groq',
    name: 'Groq',
    description: 'LLaMA, Mixtral (fast inference)',
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
  },
];

export default function SettingsPage() {
  const {
    openaiApiKey,
    anthropicApiKey,
    googleApiKey,
    groqApiKey,
    mockMode,
    setApiKey,
    setMockMode,
    syncWithBackend,
  } = useSettings();

  const [showKeys, setShowKeys] = React.useState<Record<string, boolean>>({});
  const [saved, setSaved] = React.useState(false);

  const getApiKey = (provider: string): string => {
    switch (provider) {
      case 'openai':
        return openaiApiKey;
      case 'anthropic':
        return anthropicApiKey;
      case 'google':
        return googleApiKey;
      case 'groq':
        return groqApiKey;
      default:
        return '';
    }
  };

  const handleSave = async () => {
    await syncWithBackend();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-muted">
              <Settings className="h-6 w-6" />
            </div>
            <h1 className="text-2xl font-bold">Settings</h1>
          </div>
          <p className="text-muted-foreground">
            Configure your API keys and preferences.
          </p>
        </div>

        {/* Mock Mode Toggle */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-yellow-500" />
                Mock Mode
              </CardTitle>
              <CardDescription>
                Enable mock mode to test the UI without making real API calls.
                This saves costs during development.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">
                    {mockMode ? 'Mock Mode Enabled' : 'Mock Mode Disabled'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {mockMode
                      ? 'Using simulated responses'
                      : 'Using real API calls'}
                  </p>
                </div>
                <Button
                  variant={mockMode ? 'default' : 'outline'}
                  onClick={() => setMockMode(!mockMode)}
                >
                  {mockMode ? 'Disable' : 'Enable'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* API Keys */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">API Keys</CardTitle>
              <CardDescription>
                Enter your API keys for each provider. Keys are stored locally
                in your browser.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {providers.map((provider, i) => (
                <motion.div
                  key={provider.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + i * 0.05 }}
                >
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div
                        className={cn(
                          'w-2 h-2 rounded-full',
                          getApiKey(provider.id)
                            ? 'bg-green-500'
                            : 'bg-muted-foreground'
                        )}
                      />
                      <label
                        className={cn('font-medium', provider.color)}
                        htmlFor={provider.id}
                      >
                        {provider.name}
                      </label>
                      <span className="text-xs text-muted-foreground">
                        {provider.description}
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Input
                          id={provider.id}
                          type={showKeys[provider.id] ? 'text' : 'password'}
                          placeholder={`Enter ${provider.name} API key`}
                          value={getApiKey(provider.id)}
                          onChange={(e) =>
                            setApiKey(provider.id, e.target.value)
                          }
                          className="pr-10"
                        />
                        <button
                          type="button"
                          onClick={() =>
                            setShowKeys((prev) => ({
                              ...prev,
                              [provider.id]: !prev[provider.id],
                            }))
                          }
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        >
                          {showKeys[provider.id] ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}

              <div className="pt-4 border-t">
                <Button onClick={handleSave} className="w-full">
                  {saved ? (
                    <>
                      <Check className="h-4 w-4 mr-2" />
                      Saved!
                    </>
                  ) : (
                    'Save Settings'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Info Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-6"
        >
          <Card className="bg-muted/50">
            <CardContent className="py-4">
              <p className="text-sm text-muted-foreground">
                <strong>Note:</strong> API keys are stored securely in your
                browser's local storage and sent to the backend for API calls.
                When mock mode is enabled, no real API calls are made.
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
