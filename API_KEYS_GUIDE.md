# Multi-Provider API Key Configuration Guide

This guide explains how to configure API keys for OpenRouter and Groq in the Qubic Consensus Engine.

## Overview

The system now supports **two separate API keys** for different LLM providers:

1. **OpenRouter API Key** - Access to GPT-4o, Claude 3.5, Gemini, and many other models
2. **Groq API Key** - Ultra-fast inference with Llama models

## How to Configure API Keys

### Through the Web UI (Recommended)

1. Open the main application page
2. Click the **⚙ COUNCIL_CONFIG** button in the top-right corner (or the gear icon on the sidebar toggle)
3. In the sidebar, scroll to the **API CONFIGURATION** section
4. Enter your API keys:
   - **OpenRouter API Key**: Starts with `sk-or-v1-...`
   - **Groq API Key**: Starts with `gsk_...`
5. Click **SAVE API KEYS**
6. The status indicators will update to show "✓ Connected" for each configured provider

### Getting API Keys

- **OpenRouter**: Get your key at [openrouter.ai/keys](https://openrouter.ai/keys)
- **Groq**: Get your key at [console.groq.com/keys](https://console.groq.com/keys)

## Backend API Endpoints

### Save API Keys
```
POST /settings/keys
```

**Request Body:**
```json
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

### Check API Key Status
```
GET /settings/keys/status
```

**Response:**
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
    "all_providers": [...]
}
```

## Architecture

### Backend Files

| File | Description |
|------|-------------|
| `backend/app/config/settings.py` | API key storage and validation |
| `backend/app/engine/providers.py` | Provider adapters (OpenRouter, Groq) |
| `backend/app/engine/llm.py` | Provider selection logic |
| `backend/app/main.py` | API endpoints |

### Frontend Files

| File | Description |
|------|-------------|
| `mainpage.html` | Main HTML page with API key configuration UI |
| `frontend/src/components/SettingsModal.jsx` | React settings component |

## Security Notes

- API keys are stored **in-memory only** and never logged
- Keys are cleared from input fields after saving
- Only key prefixes are returned in status responses (never full keys)

## Troubleshooting

### "Not configured" status doesn't update
- Ensure the backend server is running on `http://localhost:8000`
- Check browser console for any network errors
- Verify the API key format is correct

### API calls fail
- Ensure at least one API key is configured
- Check that the key has sufficient credits/quota
- Verify the key hasn't expired or been revoked
