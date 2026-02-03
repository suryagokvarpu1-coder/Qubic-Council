# OpenRouter Migration Guide

## What Changed?

We've migrated from using three separate API providers (OpenAI, Anthropic, Google) to **OpenRouter**, which provides unified access to all these models and more through a single API key.

---

## Benefits

### Before (3 APIs)
- ❌ 3 separate API keys to manage
- ❌ 3 different billing accounts
- ❌ 3 different rate limits
- ❌ Complex error handling for each provider
- ❌ Limited to 3 providers

### After (OpenRouter)
- ✅ 1 unified API key
- ✅ 1 billing account
- ✅ Unified rate limiting
- ✅ Consistent error handling
- ✅ Access to 20+ models from multiple providers

---

## How to Migrate

### Step 1: Get OpenRouter API Key

1. Visit [openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up or log in with your Google/GitHub account
3. Click "Create Key"
4. Copy your key (starts with `sk-or-v1-...`)
5. Add credits at [openrouter.ai/credits](https://openrouter.ai/credits)

**Recommended**: Start with $5-10 credits. Each query costs ~$0.02-0.05.

### Step 2: Update Your Configuration

**Option A: Environment Variable**

Create or update `backend/.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Option B: Settings UI**

1. Open http://localhost:5173
2. Click Settings (⚙️)
3. Paste your OpenRouter key
4. Click "Save API Key"

### Step 3: Remove Old Keys (Optional)

You can now delete your old API keys from:
- `backend/.env` (remove `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`)
- Settings UI (no longer needed)

---

## Models Available

The system now uses these models via OpenRouter:

| Layer | Model | Purpose |
|-------|-------|---------|
| Normalization | `openai/gpt-4o-mini` | Intent detection |
| Parallel Execution | `openai/gpt-4o` | Primary response |
| Parallel Execution | `anthropic/claude-3.5-sonnet` | Alternative perspective |
| Parallel Execution | `google/gemini-2.0-flash-exp:free` | Free tier option |
| Claim Extraction | `openai/gpt-4o-mini` | Extract atomic claims |
| Peer Review | `openai/gpt-4o-mini` | Review responses |
| Peer Review | `anthropic/claude-3.5-haiku` | Alternative reviewer |
| Chairman Synthesis | `openai/gpt-4o` | Final consensus |

**Note**: Gemini 2.0 Flash is FREE on OpenRouter (with rate limits)!

---

## Pricing Comparison

### Old System (Direct APIs)
- OpenAI GPT-4o: $2.50 / 1M input tokens
- Anthropic Claude 3.5 Sonnet: $3.00 / 1M input tokens
- Google Gemini 1.5 Pro: $1.25 / 1M input tokens
- **Total**: ~$6.75 / 1M tokens (if using all three)

### New System (OpenRouter)
- OpenAI GPT-4o: $2.50 / 1M input tokens
- Anthropic Claude 3.5 Sonnet: $3.00 / 1M input tokens
- Google Gemini 2.0 Flash: **FREE** (rate limited)
- **Total**: ~$5.50 / 1M tokens (same pricing, better free tier)

**Typical query cost**: $0.02-0.05 per full consensus run

---

## Code Changes

### Backend Changes

**Before** (`app/nodes/__init__.py`):
```python
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai

# Three separate clients
openai_client = AsyncOpenAI(api_key=openai_key)
anthropic_client = AsyncAnthropic(api_key=anthropic_key)
genai.configure(api_key=gemini_key)
```

**After** (`app/nodes/__init__.py`):
```python
from openai import AsyncOpenAI

# Single OpenRouter client
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_key
)

# Use with any model
response = await client.chat.completions.create(
    model="openai/gpt-4o",  # or "anthropic/claude-3.5-sonnet", etc.
    messages=[...]
)
```

### Frontend Changes

**Before** (`SettingsModal.jsx`):
```jsx
<input placeholder="OpenAI API Key" />
<input placeholder="Anthropic API Key" />
<input placeholder="Gemini API Key" />
```

**After** (`SettingsModal.jsx`):
```jsx
<input placeholder="OpenRouter API Key (sk-or-v1-...)" />
```

---

## Troubleshooting

### Error: "Invalid API key"
- Check your key starts with `sk-or-v1-`
- Verify it's active at [openrouter.ai/keys](https://openrouter.ai/keys)

### Error: "Insufficient credits"
- Add credits at [openrouter.ai/credits](https://openrouter.ai/credits)
- Or enable auto-top-up

### Error: "Model not found"
- Check model ID format: `provider/model-name`
- Example: `openai/gpt-4o`, not just `gpt-4o`

### Slow responses
- OpenRouter adds ~100-200ms latency vs direct APIs
- This is normal and worth the unified interface

---

## Advanced: Customizing Models

You can easily swap models by editing `backend/app/nodes/__init__.py`:

```python
# In execute_parallel_models()
models = [
    {"id": "openai/gpt-4o", "name": "gpt-4o"},
    {"id": "anthropic/claude-3.5-sonnet", "name": "claude-3.5-sonnet"},
    {"id": "google/gemini-2.0-flash-exp:free", "name": "gemini-2.0-flash"},
    # Add more models:
    {"id": "meta-llama/llama-3.3-70b-instruct", "name": "llama-3.3-70b"},
    {"id": "mistralai/mistral-large", "name": "mistral-large"},
]
```

Browse all available models at [openrouter.ai/models](https://openrouter.ai/models)

---

## FAQ

**Q: Can I still use my old OpenAI/Anthropic/Gemini keys?**  
A: No, the code has been migrated to OpenRouter only. But you can easily modify the code to support direct APIs if needed.

**Q: Is OpenRouter reliable?**  
A: Yes, it's used by thousands of developers and has 99.9% uptime. It's built by the team behind Anthropic's API.

**Q: Does this affect response quality?**  
A: No, OpenRouter is just a proxy. You get the exact same model responses as direct APIs.

**Q: Can I use free models?**  
A: Yes! Gemini 2.0 Flash is free on OpenRouter. You can also use other free models like Llama 3.3 70B.

---

## Rollback (If Needed)

If you need to rollback to the old system:

1. Restore `requirements.txt`:
```
openai
anthropic
google-generativeai
```

2. Restore the old `app/nodes/__init__.py` from git history:
```bash
git checkout HEAD~1 backend/app/nodes/__init__.py
```

3. Restart the backend

---

## Summary

✅ **Migration Complete**  
✅ **Single API key instead of 3**  
✅ **Access to 20+ models**  
✅ **Same pricing, better free tier**  
✅ **Simpler configuration**  

Get your OpenRouter key at [openrouter.ai/keys](https://openrouter.ai/keys) and start using the upgraded system!
