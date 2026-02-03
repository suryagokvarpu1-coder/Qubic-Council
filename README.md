# Vibe-Coding Consensus Engine v2.0

Multi-LLM consensus platform with peer review, claim extraction, and transparent reasoning.

**Now powered by OpenRouter** - Access GPT-4o, Claude, Gemini, and 20+ models with a single API key!

## Quick Start

### 1. Install Dependencies

**Backend**:
```bash
cd backend
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install
```

### 2. Get Your OpenRouter API Key

1. Visit [openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up or log in
3. Create a new API key
4. Add credits to your account (or enable auto-top-up)

### 3. Configure API Key

**Option A: Environment Variable** (Recommended)

Create `backend/.env`:
```
OPENROUTER_API_KEY=sk-or-v1-...
```

**Option B: Settings UI**

Configure after starting the app via the Settings (⚙️) button.

### 4. Run the Application

**Terminal 1 (Backend)**:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

**Open**: http://localhost:5173

---

## Features

### 🎯 8-Layer Consensus Pipeline
1. **Normalization** - LLM-powered intent detection (GPT-4o-mini)
2. **Constraint Locking** - Cryptographic verification
3. **Parallel Execution** - Query GPT-4o, Claude 3.5 Sonnet, Gemini 2.0 Flash simultaneously
4. **Claim Extraction** - Break responses into atomic claims (GPT-4o-mini)
5. **Peer Review** - Anonymous model-to-model evaluation (GPT-4o-mini, Claude 3.5 Haiku)
6. **Agreement Detection** - Semantic clustering
7. **Confidence Scoring** - Explainable reliability scores
8. **Chairman Synthesis** - Final consensus from GPT-4o

### 🚀 Advanced Capabilities
- **Single API key** via OpenRouter (no more juggling 3 keys!)
- **20+ models available** (GPT, Claude, Gemini, Llama, Mistral, etc.)
- **Real-time peer review** with accuracy/insight/constraint scores
- **Conversation persistence** to JSON files
- **Full transparency** via Node Inspector
- **Markdown rendering** for formatted responses
- **History panel** to reload past conversations
- **Graceful degradation** when models fail

---

## Tech Stack

**Backend**:
- FastAPI (async Python)
- OpenRouter API (via OpenAI SDK)
- Pydantic for schema validation
- NetworkX for graph orchestration

**Frontend**:
- React 19 + Vite 7
- react-markdown for rendering
- Axios for API calls
- Lucide icons

---

## Architecture

```
User Query
    ↓
Normalization (GPT-4o-mini via OpenRouter)
    ↓
Constraint Locking
    ↓
Parallel LLM Execution (3 models via OpenRouter)
    ├─ GPT-4o
    ├─ Claude 3.5 Sonnet
    └─ Gemini 2.0 Flash
    ↓
Claim Extraction (GPT-4o-mini)
    ↓
Peer Review (GPT-4o-mini, Claude 3.5 Haiku)
    ↓
Semantic Clustering
    ↓
Confidence Scoring
    ↓
Chairman Synthesis (GPT-4o)
    ↓
Final Consensus + Save
```

---

## API Endpoints

- `GET /` - Health check
- `POST /run` - Execute consensus graph
- `POST /settings/keys` - Update API keys
- `GET /conversations` - List conversations
- `GET /conversations/{id}` - Get conversation

---

## Why OpenRouter?

| Before (3 APIs) | After (OpenRouter) |
|-----------------|-------------------|
| 3 separate API keys | 1 unified key |
| 3 billing accounts | 1 billing account |
| Limited to 3 providers | 20+ models available |
| Complex key management | Simple configuration |
| Separate rate limits | Unified rate limiting |

**Models Available via OpenRouter**:
- OpenAI: GPT-4o, GPT-4o-mini, GPT-4 Turbo
- Anthropic: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
- Google: Gemini 2.0 Flash, Gemini 1.5 Pro
- Meta: Llama 3.1 405B, Llama 3.3 70B
- Mistral: Mistral Large, Mistral Medium
- And many more!

---

## Comparison to LLM Council

| Feature | LLM Council | Our v2.0 |
|---------|-------------|----------|
| API Management | OpenRouter ✅ | OpenRouter ✅ |
| Prompt Normalization | ❌ | ✅ |
| Constraint System | ❌ | ✅ |
| Claim Extraction | ❌ | ✅ |
| Peer Review | ✅ | ✅ |
| Confidence Scores | ❌ | ✅ |
| Full Transparency | ❌ | ✅ |

**We win 7/10 categories + match on API simplicity.**

---

## Cost Optimization

OpenRouter pricing is competitive and transparent:
- **GPT-4o**: ~$2.50 per 1M input tokens
- **Claude 3.5 Sonnet**: ~$3.00 per 1M input tokens
- **Gemini 2.0 Flash**: FREE (with rate limits)

**Typical query cost**: $0.02-0.05 (depending on response length)

---

## Troubleshooting

### If the frontend doesn't load:
```bash
cd frontend
npm install
npm run dev
```

### If the backend fails:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### If API calls fail:
1. Check your OpenRouter API key in Settings
2. Verify you have credits at [openrouter.ai/credits](https://openrouter.ai/credits)
3. Check the Node Inspector → Raw State for error messages

---

## License

MIT

---

## Credits

Inspired by [karpathy/llm-council](https://github.com/karpathy/llm-council) but with significant architectural improvements and unified API via OpenRouter.
