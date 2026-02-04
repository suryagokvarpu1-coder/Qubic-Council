import re
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

# Provider Types
PROVIDER_OPENAI = "openai"
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_GROQ = "groq"
PROVIDER_GEMINI = "gemini"
PROVIDER_OPENROUTER = "openrouter"

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier for the provider."""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass
        
    @abstractmethod
    def get_client(self, api_key: str) -> AsyncOpenAI:
        """Return an initialized OpenAI-compatible AsyncClient."""
        pass
        
    @abstractmethod
    def get_default_models(self) -> List[Dict[str, str]]:
        """Return a list of compatible models with IDs and Names."""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities (chat, json_mode, tools, etc)."""
        pass

class OpenAIProvider(LLMProvider):
    @property
    def provider_id(self) -> str: return PROVIDER_OPENAI
    
    @property
    def name(self) -> str: return "OpenAI"
    
    def get_client(self, api_key: str) -> AsyncOpenAI:
        return AsyncOpenAI(api_key=api_key)
        
    def get_default_models(self) -> List[Dict[str, str]]:
        return [
            {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "provider": "openai"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai"},
        ]
        
    def get_capabilities(self) -> List[str]:
        return ["chat", "json_mode", "tools", "vision"]

class GroqProvider(LLMProvider):
    @property
    def provider_id(self) -> str: return PROVIDER_GROQ
    
    @property
    def name(self) -> str: return "Groq"
    
    def get_client(self, api_key: str) -> AsyncOpenAI:
        return AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        
    def get_default_models(self) -> List[Dict[str, str]]:
        return [
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B", "provider": "groq"},
            {"id": "llama3-70b-8192", "name": "Llama 3 70B", "provider": "groq"},
            {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "provider": "groq"},
        ]
        
    def get_capabilities(self) -> List[str]:
        return ["chat", "json_mode", "tools"]

class OpenRouterProvider(LLMProvider):
    @property
    def provider_id(self) -> str: return PROVIDER_OPENROUTER
    
    @property
    def name(self) -> str: return "OpenRouter"
    
    def get_client(self, api_key: str) -> AsyncOpenAI:
        return AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "The Qubic Consensus Engine"
            }
        )
        
    def get_default_models(self) -> List[Dict[str, str]]:
        return [
            {"id": "openai/gpt-4o", "name": "GPT-4o (OR)", "provider": "openrouter"},
            {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet (OR)", "provider": "openrouter"},
            {"id": "google/gemini-2.0-flash-exp:free", "name": "Gemini 2.0 Flash (OR)", "provider": "openrouter"},
        ]
        
    def get_capabilities(self) -> List[str]:
        return ["chat", "json_mode", "tools", "vision"]

class ProviderFactory:
    """Factory to detect provider and return adapter."""
    
    PATTERN_OPENAI = r"^sk-[a-zA-Z0-9]{48}$|^sk-proj-[a-zA-Z0-9_-]+$"
    PATTERN_ANTHROPIC = r"^sk-ant-api03-[a-zA-Z0-9_-]+$"
    PATTERN_GROQ = r"^gsk_[a-zA-Z0-9]{52}$"
    PATTERN_OPENROUTER = r"^sk-or-v1-[a-z0-9]{64}$"
    PATTERN_GEMINI = r"^AIza[0-9A-Za-z-_]{35}$"
    
    @classmethod
    def detect_provider(cls, api_key: str) -> str:
        if not api_key:
            return None
            
        if re.match(cls.PATTERN_GROQ, api_key):
            return PROVIDER_GROQ
        elif re.match(cls.PATTERN_OPENROUTER, api_key):
            return PROVIDER_OPENROUTER
        elif re.match(cls.PATTERN_OPENAI, api_key):
            return PROVIDER_OPENAI
        elif re.match(cls.PATTERN_ANTHROPIC, api_key):
            # For this MVP, we map Anthropic native keys to OpenRouter or similar if we haven't implemented native client
            # But the requirement asks for detection. Let's return Anthropic.
            # However, our system uses OpenAI SDK. 
            # Anthropic native requires `anthropic` package. 
            # For simplicty in this "Universal" layer which claims "Common OpenAI-compatible interface",
            # we might flag this as "Native Anthropic not fully supported via OpenAI SDK adapter yet" 
            # OR we implement an adapter that uses the Anthropic SDK but exposes the same interface.
            # To keep it simple and safe for now, let's treat it as detected but maybe fallback or warn.
            return PROVIDER_ANTHROPIC 
        elif re.match(cls.PATTERN_GEMINI, api_key):
            return PROVIDER_GEMINI
            
        # Default/Fallback heuristic
        if api_key.startswith("sk-or-"):
            return PROVIDER_OPENROUTER
        if api_key.startswith("gsk_"):
            return PROVIDER_GROQ
        if api_key.startswith("sk-ant-"):
            return PROVIDER_ANTHROPIC
        if api_key.startswith("sk-"):
            return PROVIDER_OPENAI
            
        return "unknown"
        
    @classmethod
    def get_adapter(cls, provider_id: str) -> LLMProvider:
        if provider_id == PROVIDER_OPENAI:
            return OpenAIProvider()
        elif provider_id == PROVIDER_GROQ:
            return GroqProvider()
        elif provider_id == PROVIDER_OPENROUTER:
            return OpenRouterProvider()
        else:
            # Fallback to OpenRouter for unknown types as it supports most models
            return OpenRouterProvider()
