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
│   │   ├── vote.py          # Mode E: Voting
│   │   └── tracxn.py        # Tracxn data API routes
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── utils/
│   │   ├── llm_client.py    # LiteLLM wrapper with mock mode
│   │   └── tracxn_client.py # Tracxn API client with mock mode
│   ├── scripts/
│   │   └── check_tracxn.py  # Tracxn connection checker
│   └── tests/
│       └── test_tracxn.py   # Tracxn client and route tests
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

### Tracxn Data API
- `GET /tracxn/status` - Verify the Tracxn connection
- `POST /tracxn/search` - Search one page of a dataset (max 20 records)
- `POST /tracxn/collect` - Page through a dataset up to a record limit
- `POST /tracxn/config` - Update the Tracxn token at runtime

### Settings
- `GET /settings` - Get current settings
- `POST /settings` - Update API keys and mock mode

### Health
- `GET /health` - Health check
- `GET /` - API information

## Connecting to Tracxn

Tracxn is a **REST API, not a SQL database** - there is no host, port or
connection string. You authenticate with an access token and POST JSON filter
bodies to `https://platform.tracxn.com/api/2.2`.

### 1. Get an access token

Generate one from the API Token page in your Tracxn account:
<https://platform.tracxn.com/a/api/apitoken>

API access is a paid add-on. If the token page is unavailable, your plan does
not include API access - contact <support@tracxn.com>.

### 2. Configure the backend

Add to `backend/.env`:

```bash
TRACXN_ACCESS_TOKEN=your-token-here
TRACXN_MOCK_MODE=False        # True serves mock rows and spends no credits
```

Optional overrides (defaults shown):

```bash
TRACXN_BASE_URL=https://platform.tracxn.com/api/2.2
TRACXN_AUTH_HEADER=accessToken
TRACXN_TIMEOUT=30
TRACXN_MAX_RETRIES=3
```

### 3. Verify the connection

```bash
cd backend
python scripts/check_tracxn.py
```

The checker pings the API, then runs a one-record sample query against each
dataset so you can see which ones your plan includes.

If it fails, find out why:

```bash
python scripts/check_tracxn.py --probe-headers
```

Tracxn separates the two failure modes cleanly, and the probe reads that signal:

| Response | Meaning | Fix |
|---|---|---|
| `401 Token was not recognised` | Header was read; the **token** is wrong or expired | Regenerate the token |
| `403 Invalid web session access. No user.` | Header was **ignored** | Wrong header name, or no API access on your plan |

Trial-account tokens are revoked automatically when the trial ends, so a token
that worked last week can start returning 401.

### 4. Query it

```bash
curl -X POST http://localhost:8000/tracxn/search \
  -H 'Content-Type: application/json' \
  -d '{"dataset": "companies", "name": "Stripe"}'
```

Datasets: `companies`, `investors`, `fundings`, `acquisitions`. Availability
depends on your plan.

From Python:

```python
from utils.tracxn_client import TracxnClient

async with TracxnClient() as client:
    page = await client.search("companies", {"companyName": ["Stripe"]})
    print(page.total_count, page.rows)

    # Paginate past the 20-record cap; `limit` is a hard stop on credits spent.
    rows = await client.collect("fundings", {"round": ["Series A"]}, limit=100)
```

`filters` is passed to the API untouched, so any filter your plan supports
works without changing the client.

### Notes on cost and limits

- A single call returns at most **20 records**; use `collect()` to paginate.
- Every call consumes account credits. Calls returning empty results do not.
- Rate limits (429) are retried with exponential backoff, honouring `Retry-After`.
- Keep `TRACXN_MOCK_MODE=True` during UI work to avoid spending credits.

### If you wanted an actual database

Tracxn also offers scheduled SFTP dumps and Snowflake / BigQuery data shares on
some plans. Those *are* real database connections and would need a warehouse
driver instead of this client - ask your Tracxn account manager whether your
plan includes them.


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
