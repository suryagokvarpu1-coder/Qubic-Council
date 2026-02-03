from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.engine.graph import AntigravityEngine
from app.models import GraphState, ConversationSummary
from app.config.settings import set_keys, ApiKeys
from app.nodes import list_conversations, load_conversation

app = FastAPI(
    title="Vibe-Coding Consensus Engine",
    description="Multi-LLM Consensus Platform with Peer Review",
    version="2.0.0"
)

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

@app.get("/")
async def root():
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
        ]
    }

@app.post("/run", response_model=GraphState)
async def run_consensus(request: RunRequest):
    """
    Triggers the full graph execution for a given prompt.
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    final_state = await engine.run(request.prompt)
    return final_state

@app.post("/settings/keys")
async def update_keys(keys: ApiKeys):
    """
    Updates the runtime API keys.
    """
    set_keys(keys)
    return {"status": "Keys updated successfully"}

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
