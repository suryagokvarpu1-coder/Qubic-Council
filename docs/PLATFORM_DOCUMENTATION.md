# 🏗️ Platform Architecture Documentation

## System Overview

The **Vibe-Coding Consensus Engine** (also known as "The Qubic") is a multi-LLM orchestration platform that achieves consensus through parallel model execution, peer review, and synthesis. The system is designed to reduce hallucinations and provide more reliable AI responses by leveraging the collective intelligence of multiple language models.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Loading Page    │  │   Main Page      │  │  React Frontend  │  │
│  │  (Vanilla HTML)  │  │  (Vanilla HTML)  │  │  (Vite/React)    │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                     │             │
└───────────┼─────────────────────┼─────────────────────┼─────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                            │
│  Port: 8000                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │   Routes    │  │   Engine    │  │  Providers  │                  │
│  │  /run       │──│  Graph      │──│  OpenAI     │                  │
│  │  /settings  │  │  Execution  │  │  OpenRouter │                  │
│  │  /conv...   │  │             │  │  Groq       │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL LLM PROVIDERS                            │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │
│  │  OpenAI   │  │  Anthropic│  │  Google   │  │   Meta    │        │
│  │  GPT-4o   │  │  Claude   │  │  Gemini   │  │  Llama    │        │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The 8-Layer Consensus Graph

The core of the system is an 8-layer processing graph that transforms raw user queries into authoritative consensus answers.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONSENSUS GRAPH PIPELINE                          │
│                                                                      │
│  Layer 1: NORMALIZATION                                              │
│  ├─ LLM analyzes user query                                         │
│  ├─ Extracts: intent, domain, constraints                           │
│  └─ Produces: NormalizedPrompt                                      │
│                         │                                            │
│                         ▼                                            │
│  Layer 2: CONSTRAINT LOCKING                                         │
│  ├─ Merges explicit + inferred constraints                          │
│  ├─ Generates cryptographic hash                                    │
│  └─ Produces: LockedContext                                         │
│                         │                                            │
│                         ▼                                            │
│  Layer 3: PARALLEL EXECUTION                                         │
│  ├─ Queries 1-4 models concurrently                                 │
│  ├─ Uses AsyncIO for parallelism                                    │
│  └─ Produces: List[ModelResponse]                                   │
│                         │                                            │
│                         ▼                                            │
│  Layer 4: CLAIM EXTRACTION                                           │
│  ├─ LLM extracts atomic, testable claims                            │
│  ├─ Splits compound statements                                      │
│  └─ Produces: List[ClaimsResponse]                                  │
│                         │                                            │
│                         ▼                                            │
│  Layer 4.5: PEER REVIEW                                              │
│  ├─ Models review each other anonymously                            │
│  ├─ Scores: accuracy, insight, constraint_adherence                 │
│  └─ Produces: List[PeerReview]                                      │
│                         │                                            │
│                         ▼                                            │
│  Layer 5: AGREEMENT DETECTION                                        │
│  ├─ Groups similar claims into clusters                             │
│  ├─ Identifies supporting/conflicting models                        │
│  └─ Produces: List[ClaimCluster]                                    │
│                         │                                            │
│                         ▼                                            │
│  Layer 6: CONFIDENCE SCORING                                         │
│  ├─ Calculates scores based on agreement                            │
│  ├─ Incorporates peer review scores                                 │
│  └─ Produces: List[ScoredCluster]                                   │
│                         │                                            │
│                         ▼                                            │
│  Layer 7: SYNTHESIS (Chairman)                                       │
│  ├─ Chairman LLM synthesizes final answer                           │
│  ├─ Emphasizes high-confidence conclusions                          │
│  └─ Produces: FinalConsensus                                        │
│                         │                                            │
│                         ▼                                            │
│  Layer 8: PERSISTENCE                                                │
│  ├─ Saves conversation to JSON                                      │
│  └─ Returns: GraphState with conversation_id                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
test-llm-council/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, routes
│   │   ├── models.py            # Pydantic data models
│   │   ├── config/
│   │   │   └── settings.py      # Runtime key storage
│   │   ├── engine/
│   │   │   ├── graph.py         # AntigravityEngine orchestrator
│   │   │   ├── normalization.py # Layer 1-2 (prompt analysis)
│   │   │   ├── execution.py     # Layer 3-4.5 (parallel LLM calls)
│   │   │   ├── synthesis.py     # Layer 5-7 (agreement, scoring)
│   │   │   ├── persistence.py   # Layer 8 (save/load conversations)
│   │   │   ├── providers.py     # LLM provider adapters
│   │   │   └── llm.py           # Provider context management
│   │   ├── nodes/               # (Legacy, deprecated)
│   │   └── utils/
│   │       └── logger.py        # Logging utilities
│   ├── static/
│   │   ├── loadingpage.html     # Landing/loading page
│   │   └── mainpage.html        # Main application UI
│   ├── data/
│   │   └── conversations/       # Saved conversation JSON files
│   ├── tests/
│   │   ├── test_api.py          # API endpoint tests
│   │   └── test_logic.py        # Core logic tests
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .env.example
├── frontend/                    # React/Vite frontend (alternative UI)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ConsensusView.jsx
│   │   │   ├── InputSection.jsx
│   │   │   ├── NodeInspector.jsx
│   │   │   ├── PeerReviewPanel.jsx
│   │   │   ├── SettingsModal.jsx
│   │   │   └── HistoryPanel.jsx
│   │   └── index.css
│   └── package.json
├── docs/
│   └── API_DOCUMENTATION.md
├── requirements.txt
└── README.md
```

---

## Data Flow

### Request Flow

1. **User Input** → User enters query in the UI
2. **API Call** → Frontend POSTs to `/run` with prompt and model_count
3. **Normalization** → LLM analyzes intent, domain, constraints
4. **Constraint Locking** → Creates immutable context with hash
5. **Parallel Execution** → Queries 1-4 LLMs concurrently
6. **Claim Extraction** → LLM extracts atomic claims from responses
7. **Peer Review** → Models review and score each other
8. **Agreement Detection** → Groups claims into topic clusters
9. **Confidence Scoring** → Calculates confidence per cluster
10. **Synthesis** → Chairman LLM produces final answer
11. **Persistence** → Saves to JSON file
12. **Response** → Returns complete GraphState to frontend

### State Object (GraphState)

```python
class GraphState:
    raw_input: str                    # Original user query
    conversation_id: Optional[str]    # UUID after save
    normalized: NormalizedPrompt      # Layer 1 output
    locked_context: LockedContext     # Layer 2 output
    model_responses: List[ModelResponse]  # Layer 3 output
    all_claims: List[ClaimsResponse]  # Layer 4 output
    peer_reviews: List[PeerReview]    # Layer 4.5 output
    agreement_clusters: List[ClaimCluster]  # Layer 5 output
    scored_clusters: List[ScoredCluster]    # Layer 6 output
    consensus: FinalConsensus         # Layer 7 output
    errors: List[str]                 # Any errors during processing
```

---

## Provider System

The system uses a **Universal API Key** approach with automatic provider detection.

### Provider Detection Logic

```python
Key Prefix → Provider
─────────────────────
sk-or-v1-  → OpenRouter
gsk_       → Groq
sk-ant-    → Anthropic
sk-        → OpenAI (default)
AIza       → Google (Gemini)
```

### Provider Adapters

Each provider implements the `LLMProvider` abstract class:

```python
class LLMProvider(ABC):
    @property
    def provider_id(self) -> str: ...
    @property
    def name(self) -> str: ...
    def get_client(self, api_key: str) -> AsyncOpenAI: ...
    def get_default_models(self) -> List[Dict[str, str]]: ...
    def get_capabilities(self) -> List[str]: ...
```

### Available Models by Provider

| Provider | Models |
|----------|--------|
| OpenRouter | GPT-4o, Claude 3.5 Sonnet, Gemini 2.0 Flash |
| Groq | Llama 3.3 70B, Llama 3 70B, Mixtral 8x7B |
| OpenAI | GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo |

---

## Frontend Architecture

### Static HTML Frontend (Primary)

Located in `backend/static/`, served by FastAPI's `StaticFiles`:

- **loadingpage.html**: Animated loading screen with 3D rotating cube
- **mainpage.html**: Main application with:
  - Query input field
  - Sidebar for council configuration
  - Model selection (1-4 models)
  - API key management
  - Results display with confidence scoring
  - Animated geometric background (Canvas)

### React Frontend (Alternative)

Located in `frontend/`, built with Vite:

- Modern component-based architecture
- Uses axios for API calls
- React Markdown for rendering responses
- Lucide icons for UI elements

---

## Configuration

### Environment Variables

Create `.env` file in `backend/` directory:

```env
# OpenRouter API Key (recommended)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Groq API Key (optional, for fast inference)
GROQ_API_KEY=gsk_your-key-here
```

### Runtime Configuration

API keys can also be set at runtime via the `/settings/keys` endpoint or the UI sidebar.

---

## Running the Application

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend (React - optional)

```bash
cd frontend
npm install
npm run dev
```

### URLs

- **Backend + Static UI**: http://localhost:8000
- **API Status**: http://localhost:8000/api/status
- **Main Page**: http://localhost:8000/mainpage
- **React Frontend**: http://localhost:5173 (if running separately)

---

## Testing

### Run Tests

```bash
cd backend
pip install pytest pytest-asyncio
python -m pytest tests/ -v
```

### Test Coverage

- **test_api.py**: API endpoint tests
  - Health check endpoints
  - Consensus query endpoints
  - Settings/keys endpoints
  - Conversation endpoints

- **test_logic.py**: Core logic tests
  - Prompt normalization
  - Constraint locking
  - Agreement detection
  - Hash consistency

---

## Key Design Decisions

1. **All LLM calls use OpenAI SDK**: Even for non-OpenAI providers, we use the OpenAI Python SDK with custom base URLs for compatibility.

2. **Fallback behavior**: If no API key is provided or LLM calls fail, the system returns sensible defaults rather than erroring.

3. **Anonymous peer review**: Models review each other without knowing which model produced which response.

4. **Cryptographic constraint hashing**: Ensures constraint immutability throughout the pipeline.

5. **Topic-based clustering**: Uses keyword matching for claim grouping (simple but effective for MVP).

6. **Chairman synthesis**: A designated model (usually GPT-4o) synthesizes the final answer from all inputs.

---

## Extending the System

### Adding a New Provider

1. Create a class extending `LLMProvider` in `providers.py`
2. Add detection pattern to `ProviderFactory.detect_provider()`
3. Add adapter instantiation to `ProviderFactory.get_adapter()`

### Adding New Graph Layers

1. Create a new function in the appropriate engine module
2. Add output type to `models.py`
3. Add field to `GraphState`
4. Call the function in `graph.py`'s `run()` method

### Modifying Confidence Scoring

Edit `score_clusters()` in `synthesis.py` to adjust:
- Base scores
- Agreement bonuses
- Conflict penalties
- Peer review weight

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No API key provided" | Set key via UI sidebar or `/settings/keys` |
| Slow responses | Reduce `model_count` or use Groq for speed |
| Empty consensus | Check if models are responding (view individual responses) |
| Tests failing | Ensure `pytest-asyncio` is installed |

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

## License

MIT License - See LICENSE file for details.
