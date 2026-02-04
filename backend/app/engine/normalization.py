import json
import hashlib
from app.models import NormalizedPrompt, LockedContext
from app.engine.llm import get_active_provider_context
from app.engine.providers import PROVIDER_OPENROUTER
from app.utils.logger import get_logger

logger = get_logger(__name__)

async def normalize_prompt(raw_input: str) -> NormalizedPrompt:
    """Use LLM to detect intent and extract constraints from user input."""
    client, _, provider_id = get_active_provider_context()
    
    system_prompt = """You are a prompt analyzer. Given a user query, extract:
1. intent: The main goal (e.g., "build_app", "explain_concept", "compare_options", "debug_code", "generate_code")
2. domain: The subject area (e.g., "web_dev", "machine_learning", "databases", "devops")
3. explicit_constraints: Constraints explicitly stated by the user (as JSON object)
4. inferred_constraints: Reasonable defaults to infer (as JSON object)
5. normalized_prompt: A clean, unambiguous rewrite of the query

Respond ONLY with valid JSON in this exact format:
{
  "intent": "string",
  "domain": "string", 
  "explicit_constraints": {},
  "inferred_constraints": {},
  "normalized_prompt": "string"
}"""

    try:
        if client:
            # Select appropriate model based on provider
            if provider_id == PROVIDER_OPENROUTER:
                model = "openai/gpt-4o-mini"
            elif provider_id == "groq":
                model = "llama3-70b-8192"
            else:
                # For OpenAI or unknown providers, use a safe default
                model = "gpt-3.5-turbo"
                # Try to get first available model, but don't fail if it doesn't work
                try:
                    available = await client.models.list()
                    if available.data:
                        model = available.data[0].id
                except Exception:
                    pass  # Stick with default

            response = await client.chat.completions.create(
                model=model, 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_input}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            return NormalizedPrompt(**result)
    except Exception as e:
        logger.error(f"Normalization error: {e}")
    
    # Fallback to basic normalization
    return NormalizedPrompt(
        intent="general_query",
        domain="technology",
        explicit_constraints={},
        inferred_constraints={"language": "english", "depth": "intermediate"},
        normalized_prompt=raw_input
    )

async def lock_constraints(normalized: NormalizedPrompt) -> LockedContext:
    """Freeze constraints with cryptographic hash for verification."""
    merged = {**normalized.explicit_constraints, **normalized.inferred_constraints}
    constraint_str = json.dumps(merged, sort_keys=True)
    constraint_hash = hashlib.sha256(constraint_str.encode()).hexdigest()[:12]
    
    return LockedContext(
        locked_constraints=merged,
        constraint_hash=constraint_hash,
        normalized_prompt_data=normalized
    )
