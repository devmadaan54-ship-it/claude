# PolyMind - LLM Orchestration Platform

A production-grade LLM orchestration platform with multi-model routing, synthesis, debate, and consensus voting.

## Features

### 5 Core Modes

1. **Auto-Router (Mode A)** - Intelligent intent classification that automatically routes queries to the optimal model
2. **Synthesizer (Mode B)** - Query multiple top-tier models in parallel and merge insights into one master answer
3. **Council (Mode C)** - Multi-step debate system with advocates, critics, and a chairman for final verdict
4. **Hub (Mode D)** - Fan-out to 6 models simultaneously with real-time parallel SSE streaming
5. **Voting (Mode E)** - Structured consensus voting with JSON output, confidence scores, and mathematical majority

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Shadcn UI components
- Framer Motion for animations
- Zustand for state management
- Lucide React icons

### Backend
- Python 3.11+
- FastAPI
- LiteLLM (unified interface for OpenAI, Anthropic, Google, Groq)
- SSE (Server-Sent Events) for real-time streaming
- Pydantic for data validation
- Asyncio for parallel execution

## Project Structure

```
polymind/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings and configuration
│   ├── requirements.txt     # Python dependencies
│   ├── routers/
│   │   ├── router.py        # Mode A: Auto-Router
│   │   ├── synthesis.py     # Mode B: Synthesizer
│   │   ├── debate.py        # Mode C: Council
│   │   ├── hub.py           # Mode D: Hub
│   │   └── vote.py          # Mode E: Voting
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── utils/
│       └── llm_client.py    # LiteLLM wrapper with mock mode
│
└── frontend/
    ├── src/
    │   ├── app/             # Next.js App Router pages
    │   ├── components/      # React components
    │   ├── hooks/           # Custom hooks (useLLMStream)
    │   ├── store/           # Zustand stores
    │   ├── lib/             # Utilities
    │   └── types/           # TypeScript types
    ├── package.json
    └── tailwind.config.ts
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Start the server (mock mode enabled by default)
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Configuration

### Mock Mode

Mock mode is enabled by default (`MOCK_MODE=True`), which allows you to test the UI without making real API calls. This is useful for:
- Development and testing
- UI design work
- Cost savings during development

To disable mock mode and use real APIs:
1. Set `MOCK_MODE=False` in your `.env` file
2. Add your API keys for the providers you want to use

### API Keys

You can configure API keys in two ways:
1. Environment variables in `.env` file
2. Through the Settings page in the frontend UI

Supported providers:
- **OpenAI**: GPT-4o, GPT-4o-mini
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Haiku
- **Google**: Gemini 1.5 Pro, Gemini 1.5 Flash
- **Groq**: LLaMA, Mixtral

## API Endpoints

### Unified Query Endpoint
```
POST /query
{
  "query": "Your question here",
  "mode": "router|synthesizer|debate|hub|vote",
  "stream": true,
  "models": ["gpt-4o", "claude-3-5-sonnet-20241022"]  // optional override
}
```

### Mode-Specific Endpoints
- `POST /router/stream` - Auto-router with streaming
- `POST /synthesizer/stream` - Synthesizer with streaming
- `POST /debate/stream` - Debate with streaming
- `POST /hub/stream` - Hub with parallel streaming
- `POST /vote/stream` - Voting with streaming

### Settings
- `GET /settings` - Get current settings
- `POST /settings` - Update API keys and mock mode

### Health
- `GET /health` - Health check
- `GET /` - API information

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run lint
```

### Building for Production

```bash
# Frontend
cd frontend
npm run build

# Backend - use uvicorn with production settings
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Architecture Highlights

### Parallel Streaming (Hub Mode)
The Hub mode demonstrates a sophisticated fan-out architecture where:
1. A single user query triggers 6 simultaneous API calls
2. Each model's response streams independently via SSE
3. The frontend renders all 6 streams in a responsive grid
4. No model waits for another - true parallel execution

### Structured Output (Voting Mode)
Voting mode enforces JSON-only responses using Pydantic schemas:
```json
{
  "vote": "Yes|No",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation"
}
```

### Intent Classification (Router Mode)
The auto-router uses a lightweight model (GPT-4o-mini) to classify intents:
- Coding → Claude 3.5 Sonnet
- Creative → GPT-4o
- Reasoning → Claude 3.5 Sonnet
- Factual → Gemini 1.5 Pro

## License

MIT
