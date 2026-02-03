from pydantic import BaseModel
from typing import Optional

class ApiKeys(BaseModel):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

# Global in-memory storage for runtime keys
# In a production app, this would be a secure vault or database
runtime_keys = ApiKeys()

def get_keys() -> ApiKeys:
    return runtime_keys

def set_keys(keys: ApiKeys):
    global runtime_keys
    runtime_keys = keys
