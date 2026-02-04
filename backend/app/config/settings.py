from pydantic import BaseModel, field_validator
from typing import Optional, Dict, List
import re

class ApiKeys(BaseModel):
    """
    API key configuration supporting multiple LLM providers.
    Each provider has its own dedicated key field for clarity and security.
    """
    # Primary supported providers
    openrouter_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # Legacy/alternative keys (for backward compatibility)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Universal key (deprecated, but kept for backward compatibility)
    universal_key: Optional[str] = None
    provider_id: Optional[str] = None
    
    @field_validator('openrouter_api_key')
    @classmethod
    def validate_openrouter_key(cls, v):
        if v is not None and v.strip():
            v = v.strip()
            # OpenRouter keys should start with sk-or-
            if not v.startswith('sk-or-'):
                # Allow it but don't fail - might be a valid key format we don't know
                pass
        return v if v and v.strip() else None
    
    @field_validator('groq_api_key')
    @classmethod
    def validate_groq_key(cls, v):
        if v is not None and v.strip():
            v = v.strip()
            # Groq keys should start with gsk_
            if not v.startswith('gsk_'):
                # Allow it but don't fail - might be a valid key format we don't know
                pass
        return v if v and v.strip() else None
    
    def has_openrouter(self) -> bool:
        """Check if OpenRouter API key is configured."""
        return bool(self.openrouter_api_key and self.openrouter_api_key.strip())
    
    def has_groq(self) -> bool:
        """Check if Groq API key is configured."""
        return bool(self.groq_api_key and self.groq_api_key.strip())
    
    def has_any_key(self) -> bool:
        """Check if any API key is configured."""
        return self.has_openrouter() or self.has_groq()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers based on configured keys."""
        providers = []
        if self.has_openrouter():
            providers.append("openrouter")
        if self.has_groq():
            providers.append("groq")
        return providers
    
    def get_status(self) -> Dict[str, any]:
        """Get configuration status without exposing actual keys."""
        return {
            "openrouter": {
                "configured": self.has_openrouter(),
                "key_prefix": self.openrouter_api_key[:12] + "..." if self.has_openrouter() else None
            },
            "groq": {
                "configured": self.has_groq(),
                "key_prefix": self.groq_api_key[:8] + "..." if self.has_groq() else None
            },
            "available_providers": self.get_available_providers()
        }


# Global in-memory storage for runtime keys
# In a production app, this would be a secure vault or database
runtime_keys = ApiKeys()

def get_keys() -> ApiKeys:
    """Get the current runtime API keys configuration."""
    return runtime_keys

def set_keys(keys: ApiKeys):
    """Update the runtime API keys configuration."""
    global runtime_keys
    runtime_keys = keys
    
def update_keys(openrouter_key: Optional[str] = None, groq_key: Optional[str] = None) -> ApiKeys:
    """
    Update specific keys without overwriting others.
    Returns the updated keys configuration.
    """
    global runtime_keys
    
    if openrouter_key is not None:
        runtime_keys.openrouter_api_key = openrouter_key.strip() if openrouter_key.strip() else None
    
    if groq_key is not None:
        runtime_keys.groq_api_key = groq_key.strip() if groq_key.strip() else None
    
    return runtime_keys
