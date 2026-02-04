# 📖 API Documentation

## Overview

The Vibe-Coding Consensus Engine provides a RESTful API for orchestrating multi-LLM consensus queries. The API follows standard REST conventions and returns JSON responses.

**Base URL:** `http://localhost:8000`

---

## Authentication

The API supports **multi-provider configuration** with separate API keys for each LLM provider. You can configure one or both providers.

### Supported Providers

| Provider | Key Format | Description |
|----------|------------|-------------|
| OpenRouter | `sk-or-v1-...` | Access to GPT-4o, Claude, Gemini & more |
| Groq | `gsk_...` | Ultra-fast Llama inference |

### Setting API Keys (Recommended)

Configure each provider separately for maximum clarity:

```http
POST /settings/keys
Content-Type: application/json

{
  "openrouter_api_key": "sk-or-v1-your-key-here",
  "groq_api_key": "gsk_your-key-here"
}
```

**Response:**
```json
{
  "status": "Keys updated successfully",
  "updated_providers": ["openrouter", "groq"],
  "available_providers": ["openrouter", "groq"],
  "providers_status": {
    "openrouter": {
      "configured": true,
      "key_prefix": "sk-or-v1-..."
    },
    "groq": {
      "configured": true,
      "key_prefix": "gsk_..."
    }
  }
}
```

### Legacy Universal Key (Still Supported)

For backward compatibility, you can still use a universal key that auto-detects the provider:

```json
{
  "universal_key": "sk-or-v1-your-key-here"
}
```

---

## Endpoints

### Health Check

#### GET /api/status

Returns the current status of the API server and configured providers.

**Request:**
```http
GET /api/status
```

**Response (200 OK):**
```json
{
  "status": "Online",
  "system": "Antigravity Vibe-Coding Consensus Engine v2.0",
  "features": [
    "Real LLM-powered normalization",
    "Parallel multi-model execution",
    "Atomic claim extraction",
    "Anonymous peer review",
    "Confidence scoring",
    "Chairman synthesis",
    "Conversation persistence"
  ],
  "providers_configured": ["openrouter", "groq"]
}
```

---

### Run Consensus Query

#### POST /run

Executes the full consensus engine graph for a given prompt.

**Request:**
```http
POST /run
Content-Type: application/json

{
  "prompt": "What is the best frontend framework for a new project?",
  "model_count": 4
}
```

**Request Body Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | The query to send to the LLM council |
| `model_count` | integer | No | 4 | Number of models to query (1-4) |

**Response (200 OK):**
```json
{
  "raw_input": "What is the best frontend framework?",
  "conversation_id": "uuid-string",
  "normalized": {
    "intent": "compare_options",
    "domain": "web_dev",
    "explicit_constraints": {},
    "inferred_constraints": {"language": "english"},
    "normalized_prompt": "Compare frontend frameworks..."
  },
  "locked_context": {
    "locked_constraints": {...},
    "constraint_hash": "abc123def456",
    "normalized_prompt_data": {...}
  },
  "model_responses": [
    {
      "model_id": "GPT-4o (OR)",
      "response_text": "...",
      "token_count": 250
    }
  ],
  "all_claims": [
    {
      "model_id": "GPT-4o (OR)",
      "claims": [
        {"claim_id": "uuid", "text": "React is widely used"}
      ]
    }
  ],
  "peer_reviews": [
    {
      "reviewer_model": "gpt-4o",
      "reviewed_model": "claude-3.5-sonnet",
      "accuracy_score": 8,
      "insight_score": 7,
      "constraint_adherence": 9,
      "feedback": "Good analysis..."
    }
  ],
  "agreement_clusters": [...],
  "scored_clusters": [
    {
      "cluster_id": "abc123",
      "canonical_claim": "Topic: Frontend",
      "supporting_models": ["GPT-4o", "Claude"],
      "conflicting_models": [],
      "confidence_score": 0.85,
      "reasons": ["Strong agreement: 3 models support this"]
    }
  ],
  "consensus": {
    "final_answer": "Based on the council's analysis...",
    "confidence": 0.82,
    "uncertain_areas": ["Performance benchmarks vary"],
    "reasoning_trace": [
      {"step": "normalization", "details": "Intent: compare_options"},
      {"step": "execution", "details": "Queried 4 models"},
      {"step": "synthesis", "details": "Chairman synthesized answer"}
    ]
  },
  "errors": []
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| 400 | Prompt is required (empty string) |
| 422 | Validation error (missing fields) |
| 500 | Internal server error |

---

### Update API Keys

#### POST /settings/keys

Updates the runtime API keys for LLM providers. Supports multiple configuration formats.

**Preferred Format (Separate Keys):**
```http
POST /settings/keys
Content-Type: application/json

{
  "openrouter_api_key": "sk-or-v1-your-key-here",
  "groq_api_key": "gsk_your-key-here"
}
```

You can also set just one key:
```json
{
  "openrouter_api_key": "sk-or-v1-your-key-here"
}
```

**Legacy Format (Universal Key):**
```json
{
  "universal_key": "sk-or-v1-your-key-here"
}
```

**Response (200 OK):**
```json
{
  "status": "Keys updated successfully",
  "updated_providers": ["openrouter"],
  "available_providers": ["openrouter", "groq"],
  "providers_status": {
    "openrouter": {
      "configured": true,
      "key_prefix": "sk-or-v1-..."
    },
    "groq": {
      "configured": true,
      "key_prefix": "gsk_..."
    }
  }
}
```

> ⚠️ **Security Note:** Full API keys are never returned in responses. Only truncated prefixes are shown for verification.

---

### Get API Keys Status

#### GET /settings/keys/status

Returns the current configuration status of API keys without exposing the actual keys.

**Request:**
```http
GET /settings/keys/status
```

**Response (200 OK):**
```json
{
  "providers": {
    "openrouter": {
      "configured": true,
      "key_prefix": "sk-or-v1-..."
    },
    "groq": {
      "configured": false,
      "key_prefix": null
    },
    "available_providers": ["openrouter"]
  },
  "available": ["openrouter"],
  "all_providers": [
    {
      "id": "openrouter",
      "name": "OpenRouter",
      "available": true,
      "models": [...],
      "capabilities": ["chat", "json_mode", "tools"]
    },
    {
      "id": "groq",
      "name": "Groq",
      "available": false,
      "models": [],
      "capabilities": ["chat", "fast_inference"]
    }
  ]
}
```

---

### List Conversations

#### GET /conversations

Returns a list of all saved conversation summaries.

**Request:**
```http
GET /conversations
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid-string",
    "timestamp": "2025-02-04T12:00:00.000000",
    "query": "What is the best frontend framework?"
  }
]
```

---

### Get Conversation

#### GET /conversations/{conversation_id}

Retrieves a specific saved conversation by ID.

**Request:**
```http
GET /conversations/abc123-uuid
```

**Response (200 OK):**
```json
{
  "id": "abc123-uuid",
  "timestamp": "2025-02-04T12:00:00.000000",
  "state": {
    "raw_input": "...",
    "consensus": {...},
    ...
  }
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| 404 | Conversation not found |

---

### Frontend Pages

#### GET /

Serves the loading page (`loadingpage.html`).

#### GET /mainpage

Serves the main application page (`mainpage.html`).

---

## Data Models

### NormalizedPrompt

```typescript
{
  intent: string;           // e.g., "build_app", "compare_options"
  domain: string;           // e.g., "web_dev", "machine_learning"
  explicit_constraints: object;
  inferred_constraints: object;
  normalized_prompt: string;
}
```

### ModelResponse

```typescript
{
  model_id: string;         // Model name/identifier
  response_text: string;    // Full response from the model
  token_count: number;      // Approximate token count
}
```

### AtomicClaim

```typescript
{
  claim_id: string;         // UUID
  text: string;             // The claim text
}
```

### PeerReview

```typescript
{
  reviewer_model: string;
  reviewed_model: string;
  accuracy_score: number;   // 1-10
  insight_score: number;    // 1-10
  constraint_adherence: number; // 1-10
  feedback: string;
}
```

### FinalConsensus

```typescript
{
  final_answer: string;
  confidence: number;       // 0.0-1.0
  uncertain_areas: string[];
  reasoning_trace: Array<{step: string, details: string}>;
}
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Missing/invalid fields |
| 500 | Internal Server Error |

---

## Rate Limiting

No built-in rate limiting is implemented. Rate limits depend on your LLM provider's API limits.

---

## CORS

CORS is enabled for all origins (`*`) to allow frontend development.

---

## Example Usage

### cURL

```bash
# Check API status
curl http://localhost:8000/api/status

# Check configured providers
curl http://localhost:8000/settings/keys/status

# Set API keys (both providers)
curl -X POST http://localhost:8000/settings/keys \
  -H "Content-Type: application/json" \
  -d '{"openrouter_api_key": "sk-or-v1-your-key", "groq_api_key": "gsk_your-key"}'

# Set single provider key
curl -X POST http://localhost:8000/settings/keys \
  -H "Content-Type: application/json" \
  -d '{"openrouter_api_key": "sk-or-v1-your-key"}'

# Run a consensus query
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the best database for a startup?", "model_count": 3}'
```

### JavaScript (Fetch)

```javascript
// Set API keys
await fetch('http://localhost:8000/settings/keys', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    openrouter_api_key: 'sk-or-v1-your-key',
    groq_api_key: 'gsk_your-key'
  })
});

// Check provider status
const statusRes = await fetch('http://localhost:8000/settings/keys/status');
const status = await statusRes.json();
console.log('Available providers:', status.available);

// Run consensus query
const response = await fetch('http://localhost:8000/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'Should I use React or Vue for my project?',
    model_count: 4
  })
});
const result = await response.json();
console.log(result.consensus.final_answer);
```

### Python (requests)

```python
import requests

# Set API keys
requests.post('http://localhost:8000/settings/keys', json={
    'openrouter_api_key': 'sk-or-v1-your-key',
    'groq_api_key': 'gsk_your-key'
})

# Check provider status
status = requests.get('http://localhost:8000/settings/keys/status').json()
print(f"Available providers: {status['available']}")

# Run query
response = requests.post('http://localhost:8000/run', json={
    'prompt': 'Compare Python and JavaScript for backend development',
    'model_count': 4
})
print(response.json()['consensus']['final_answer'])
```

