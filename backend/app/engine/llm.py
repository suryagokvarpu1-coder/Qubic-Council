import os
from dotenv import load_dotenv
from typing import Tuple, List, Dict, Optional, Any
from app.config.settings import get_keys
from app.engine.providers import (
    ProviderFactory, 
    PROVIDER_OPENROUTER, 
    PROVIDER_GROQ,
    PROVIDER_OPENAI,
    LLMProvider
)
from openai import AsyncOpenAI

load_dotenv()

def get_active_provider_context(preferred_provider: Optional[str] = None) -> Tuple[Optional[AsyncOpenAI], List[Dict[str, str]], Optional[str]]:
    """
    Determine the best available provider and return the client, models, and provider ID.
    
    Priority order:
    1. If preferred_provider is specified and available, use it
    2. OpenRouter (most diverse model access)
    3. Groq (fast inference)
    4. Environment variables as fallback
    
    Args:
        preferred_provider: Optional provider ID to prefer ("openrouter" or "groq")
    
    Returns:
        Tuple of (client, available_models, provider_id)
        Returns (None, [], None) if no provider is available
    """
    keys = get_keys()
    
    # If a preferred provider is specified and available, use it
    if preferred_provider:
        if preferred_provider == PROVIDER_OPENROUTER and keys.has_openrouter():
            adapter = ProviderFactory.get_adapter(PROVIDER_OPENROUTER)
            client = adapter.get_client(keys.openrouter_api_key)
            models = adapter.get_default_models()
            return client, models, PROVIDER_OPENROUTER
        
        if preferred_provider == PROVIDER_GROQ and keys.has_groq():
            adapter = ProviderFactory.get_adapter(PROVIDER_GROQ)
            client = adapter.get_client(keys.groq_api_key)
            models = adapter.get_default_models()
            return client, models, PROVIDER_GROQ
    
    # Priority 1: OpenRouter (access to multiple models including Claude, GPT-4, Gemini)
    if keys.has_openrouter():
        adapter = ProviderFactory.get_adapter(PROVIDER_OPENROUTER)
        client = adapter.get_client(keys.openrouter_api_key)
        models = adapter.get_default_models()
        return client, models, PROVIDER_OPENROUTER
    
    # Priority 2: Groq (fast inference with Llama models)
    if keys.has_groq():
        adapter = ProviderFactory.get_adapter(PROVIDER_GROQ)
        client = adapter.get_client(keys.groq_api_key)
        models = adapter.get_default_models()
        return client, models, PROVIDER_GROQ
    
    # Legacy: Check universal_key for backward compatibility
    if keys.universal_key:
        provider_id = keys.provider_id or ProviderFactory.detect_provider(keys.universal_key)
        adapter = ProviderFactory.get_adapter(provider_id)
        if adapter:
            client = adapter.get_client(keys.universal_key)
            models = adapter.get_default_models()
            return client, models, provider_id

    # Fallback to Environment Variables
    env_openrouter = os.getenv("OPENROUTER_API_KEY")
    if env_openrouter:
        adapter = ProviderFactory.get_adapter(PROVIDER_OPENROUTER)
        client = adapter.get_client(env_openrouter)
        models = adapter.get_default_models()
        return client, models, PROVIDER_OPENROUTER
    
    env_groq = os.getenv("GROQ_API_KEY")
    if env_groq:
        adapter = ProviderFactory.get_adapter(PROVIDER_GROQ)
        client = adapter.get_client(env_groq)
        models = adapter.get_default_models()
        return client, models, PROVIDER_GROQ
    
    # Legacy: OPENAI_API_KEY treated as OpenRouter
    env_openai = os.getenv("OPENAI_API_KEY")
    if env_openai:
        # Check if it's actually an OpenRouter key
        if env_openai.startswith("sk-or-"):
            adapter = ProviderFactory.get_adapter(PROVIDER_OPENROUTER)
            client = adapter.get_client(env_openai)
            models = adapter.get_default_models()
            return client, models, PROVIDER_OPENROUTER
        else:
            adapter = ProviderFactory.get_adapter(PROVIDER_OPENAI)
            client = adapter.get_client(env_openai)
            models = adapter.get_default_models()
            return client, models, PROVIDER_OPENAI
    
    return None, [], None


def get_all_available_providers() -> List[Dict[str, Any]]:
    """
    Get information about all available providers based on configured keys.
    
    Returns:
        List of provider info dicts with id, name, available status, and model count
    """
    keys = get_keys()
    providers = []
    
    # OpenRouter
    openrouter_adapter = ProviderFactory.get_adapter(PROVIDER_OPENROUTER)
    providers.append({
        "id": PROVIDER_OPENROUTER,
        "name": openrouter_adapter.name,
        "available": keys.has_openrouter(),
        "models": openrouter_adapter.get_default_models() if keys.has_openrouter() else [],
        "capabilities": openrouter_adapter.get_capabilities()
    })
    
    # Groq
    groq_adapter = ProviderFactory.get_adapter(PROVIDER_GROQ)
    providers.append({
        "id": PROVIDER_GROQ,
        "name": groq_adapter.name,
        "available": keys.has_groq(),
        "models": groq_adapter.get_default_models() if keys.has_groq() else [],
        "capabilities": groq_adapter.get_capabilities()
    })
    
    return providers


def get_provider_client(provider_id: str) -> Tuple[Optional[AsyncOpenAI], List[Dict[str, str]]]:
    """
    Get a client for a specific provider.
    
    Args:
        provider_id: The provider ID ("openrouter" or "groq")
    
    Returns:
        Tuple of (client, models) or (None, []) if provider not available
    """
    keys = get_keys()
    
    if provider_id == PROVIDER_OPENROUTER and keys.has_openrouter():
        adapter = ProviderFactory.get_adapter(PROVIDER_OPENROUTER)
        client = adapter.get_client(keys.openrouter_api_key)
        models = adapter.get_default_models()
        return client, models
    
    if provider_id == PROVIDER_GROQ and keys.has_groq():
        adapter = ProviderFactory.get_adapter(PROVIDER_GROQ)
        client = adapter.get_client(keys.groq_api_key)
        models = adapter.get_default_models()
        return client, models
    
    return None, []


def get_unified_models() -> List[Dict[str, str]]:
    """
    Get a combined list of models from all available providers.
    Returns models in a priority order suitable for slicing by model_count.
    """
    keys = get_keys()
    all_models = []
    
    # 1. OpenRouter (High Capability Models)
    if keys.has_openrouter():
        try:
            adapter = ProviderFactory.get_adapter(PROVIDER_OPENROUTER)
            all_models.extend(adapter.get_default_models())
        except Exception:
            pass
            
    # 2. Groq (High Speed Models)
    if keys.has_groq():
        try:
            adapter = ProviderFactory.get_adapter(PROVIDER_GROQ)
            all_models.extend(adapter.get_default_models())
        except Exception:
            pass
            
    # 3. Legacy / Fallbacks
    if not all_models and keys.universal_key:
        provider_id = keys.provider_id or ProviderFactory.detect_provider(keys.universal_key)
        adapter = ProviderFactory.get_adapter(provider_id)
        if adapter:
            all_models.extend(adapter.get_default_models())
            
    return all_models
