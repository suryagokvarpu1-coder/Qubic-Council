import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Data directory for conversation persistence
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "conversations")
os.makedirs(DATA_DIR, exist_ok=True)

def save_conversation(state: dict, conversation_id: str = None) -> str:
    """Save conversation to JSON file."""
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    
    data = {
        "id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "state": state
    }
    
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save conversation {conversation_id}: {e}")
        raise e
    
    return conversation_id

def load_conversation(conversation_id: str) -> Optional[dict]:
    """Load conversation from JSON file."""
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load conversation {conversation_id}: {e}")
            return None
    return None

def list_conversations() -> List[dict]:
    """List all saved conversations."""
    conversations = []
    if not os.path.exists(DATA_DIR):
        return []
        
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    # Basic validation of data structure
                    if isinstance(data, dict):
                        conversations.append({
                            "id": data.get("id"),
                            "timestamp": data.get("timestamp"),
                            "query": data.get("state", {}).get("raw_input", "")[:100]
                        })
            except Exception as e:
                logger.warning(f"Skipping malformed conversation file {filename}: {e}")
                
    return sorted(conversations, key=lambda x: x.get("timestamp", ""), reverse=True)
