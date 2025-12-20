export type QueryMode = 'router' | 'synthesizer' | 'debate' | 'hub' | 'vote';

export interface StreamEvent {
  event: string;
  model?: string;
  data?: string;
  index?: number;
  step?: number;
  display_name?: string;
  [key: string]: any;
}

export interface HubStream {
  index: number;
  model: string;
  displayName: string;
  content: string;
  status: 'pending' | 'streaming' | 'complete' | 'error';
}

export interface VoteData {
  model: string;
  displayName: string;
  vote: 'Yes' | 'No';
  confidence: number;
  reasoning: string;
}

export interface VotingResult {
  yesCount: number;
  noCount: number;
  consensus: 'Yes' | 'No' | 'Tie';
  averageConfidence: number;
  winnerReasoning: string;
}

export interface DebateStep {
  step: number;
  name: string;
  role: string;
  model: string;
  content: string;
  status: 'pending' | 'streaming' | 'complete';
}

export interface RouterResult {
  intent: string;
  model: string;
  reasoning: string;
  content: string;
}

export interface SynthesisPhase {
  phase: string;
  message: string;
}

export interface ModelResponse {
  model: string;
  preview: string;
}

export interface Settings {
  openaiApiKey: string;
  anthropicApiKey: string;
  googleApiKey: string;
  groqApiKey: string;
  mockMode: boolean;
}
