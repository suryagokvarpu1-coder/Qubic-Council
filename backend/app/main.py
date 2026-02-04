from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
from app.engine.graph import AntigravityEngine
from app.models import GraphState, ConversationSummary
from app.config.settings import set_keys, get_keys, update_keys, ApiKeys
from app.engine.persistence import list_conversations, load_conversation
from app.engine.providers import ProviderFactory, PROVIDER_OPENROUTER, PROVIDER_GROQ
from app.engine.llm import get_all_available_providers

app = FastAPI(
    title="Vibe-Coding Consensus Engine",
    description="Multi-LLM Consensus Platform with Peer Review",
    version="2.0.0"
)

# Path to static files (your custom frontend)
STATIC_DIR = Path(__file__).parent.parent / "static"

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = AntigravityEngine()

class RunRequest(BaseModel):
    prompt: str
    model_count: int = 4  # Default to all 4 models
    
    class Config:
        @staticmethod
        def validate_model_count(v):
            if v < 1 or v > 4:
                raise ValueError('model_count must be between 1 and 4')
            return v

class UpdateKeysRequest(BaseModel):
    """Request model for updating API keys."""
    openrouter_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    # Legacy support
    universal_key: Optional[str] = None
    openai_api_key: Optional[str] = None

# ===== FRONTEND ROUTES (Your Custom HTML Pages) =====

@app.get("/")
async def root():
    """
    Serves the loading page as the default landing page.
    """
    return FileResponse(STATIC_DIR / "loadingpage.html")

@app.get("/mainpage")
async def mainpage():
    """
    Serves the main application page.
    """
    return FileResponse(STATIC_DIR / "mainpage.html")

@app.get("/mainpage.html")
async def mainpage_html():
    """
    Serves the main application page (direct HTML file access).
    """
    return FileResponse(STATIC_DIR / "mainpage.html")

# ===== API HEALTH CHECK (for debugging) =====

@app.get("/api/status")
async def api_status():
    """
    API health check endpoint - confirms backend is running.
    """
    keys = get_keys()
    return {
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
        "providers_configured": keys.get_available_providers()
    }

# ===== API ENDPOINTS =====

@app.post("/run", response_model=GraphState)
async def run_consensus(request: RunRequest):
    """
    Triggers the full graph execution for a given prompt.
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    # Validate model_count
    model_count = max(1, min(4, request.model_count))
    
    final_state = await engine.run(request.prompt, model_count=model_count)
    return final_state

@app.post("/settings/keys")
async def update_api_keys(request: UpdateKeysRequest):
    """
    Updates the runtime API keys for LLM providers.
    
    Accepts separate keys for OpenRouter and Groq.
    Keys are never logged or returned in full for security.
    """
    keys = get_keys()
    updated_providers = []
    
    # Handle OpenRouter key
    if request.openrouter_api_key is not None:
        key = request.openrouter_api_key.strip() if request.openrouter_api_key else None
        if key:
            keys.openrouter_api_key = key
            updated_providers.append("openrouter")
        else:
            keys.openrouter_api_key = None
    
    # Handle Groq key
    if request.groq_api_key is not None:
        key = request.groq_api_key.strip() if request.groq_api_key else None
        if key:
            keys.groq_api_key = key
            updated_providers.append("groq")
        else:
            keys.groq_api_key = None
    
    # Legacy: Handle universal_key for backward compatibility
    if request.universal_key:
        detected = ProviderFactory.detect_provider(request.universal_key)
        if detected == PROVIDER_OPENROUTER:
            keys.openrouter_api_key = request.universal_key
            updated_providers.append("openrouter")
        elif detected == PROVIDER_GROQ:
            keys.groq_api_key = request.universal_key
            updated_providers.append("groq")
        else:
            # Store as universal for other detected providers
            keys.universal_key = request.universal_key
            keys.provider_id = detected
    
    # Legacy: Handle openai_api_key (treat as OpenRouter if it matches pattern)
    if request.openai_api_key:
        if request.openai_api_key.startswith("sk-or-"):
            keys.openrouter_api_key = request.openai_api_key
            updated_providers.append("openrouter")
    
    set_keys(keys)
    
    return {
        "status": "Keys updated successfully",
        "updated_providers": updated_providers,
        "available_providers": keys.get_available_providers(),
        "providers_status": keys.get_status()
    }

@app.get("/settings/keys/status")
async def get_keys_status():
    """
    Returns the current API key configuration status.
    Does NOT expose the actual keys, only their configuration state.
    """
    keys = get_keys()
    return {
        "providers": keys.get_status(),
        "available": keys.get_available_providers(),
        "all_providers": get_all_available_providers()
    }

@app.get("/conversations", response_model=List[ConversationSummary])
async def get_conversations():
    """
    List all saved conversations.
    """
    return list_conversations()

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation by ID.
    """
    conv = load_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv
