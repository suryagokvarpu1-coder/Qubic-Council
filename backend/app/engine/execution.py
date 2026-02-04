import asyncio
import json
import uuid
from typing import List
from app.models import ModelResponse, LockedContext, ClaimsResponse, AtomicClaim, PeerReview
from app.engine.llm import get_active_provider_context, get_unified_models, get_provider_client
from app.engine.providers import PROVIDER_OPENROUTER, PROVIDER_GROQ
from app.utils.logger import get_logger

logger = get_logger(__name__)

async def execute_parallel_models(context: LockedContext, model_count: int = 4) -> List[ModelResponse]:
    """
    Query available models in parallel.
    model_count: Number of models to query (1-4). Models are selected in order of priority.
    """
    
    # NEW: Get unified list of models from all providers
    available_models = get_unified_models()
    
    prompt = context.normalized_prompt_data.normalized_prompt
    constraints_context = f"\n\nConstraints: {json.dumps(context.locked_constraints)}"
    full_prompt = prompt + constraints_context
    
    if not available_models:
        return [ModelResponse(model_id="system", response_text="No API keys configured. Please configure keys in Settings.", token_count=0)]
    
    # Select models based on model_count
    # e.g. if model_count=4, we might get [GPT-4o(OR), Claude(OR), Gemini(OR), Llama(Groq)]
    count = min(model_count, len(available_models))
    selected_models = available_models[:count]
    
    async def call_model(model_config):
        """Call a model via its specific provider client."""
        try:
            # Dynamically get client for this specific model
            m_client, _ = get_provider_client(model_config["provider"])
            
            if not m_client:
                 return ModelResponse(
                    model_id=model_config["name"], 
                    response_text=f"Error: No client for provider {model_config['provider']}", 
                    token_count=0
                )

            completion = await m_client.chat.completions.create(
                model=model_config["id"],
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=2048
            )
            text = completion.choices[0].message.content
            return ModelResponse(
                model_id=model_config["name"], 
                response_text=text, 
                token_count=len(text.split())
            )
        except Exception as e:
            logger.error(f"Model call failed ({model_config['name']}): {e}")
            return ModelResponse(
                model_id=model_config["name"], 
                response_text=f"Error ({model_config['provider']}): {str(e)}", 
                token_count=0
            )
    
    tasks = [call_model(m) for m in selected_models]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]

async def extract_claims(responses: List[ModelResponse]) -> List[ClaimsResponse]:
    """Use LLM to extract atomic claims from each model's response."""
    client, _, provider_id = get_active_provider_context()
    
    system_prompt = """Extract atomic, testable claims from the following text.
Each claim should be:
- A single, standalone statement
- Verifiable or falsifiable
- Free of subjective language
- Split compound statements (with 'and', 'but', 'because') into separate claims

Respond with a JSON array of strings:
["claim 1", "claim 2", ...]"""

    async def extract_for_model(response: ModelResponse) -> ClaimsResponse:
        claims = []
        try:
            if client:
                model = "openai/gpt-4o-mini" if provider_id == PROVIDER_OPENROUTER else "gpt-3.5-turbo"
                if provider_id == PROVIDER_GROQ: model = "llama3-70b-8192"
                
                # Dynamic Model Selection for Extraction
                target_model = model
                if provider_id != PROVIDER_OPENROUTER and provider_id != PROVIDER_GROQ:
                     try:
                        target_model = (await client.models.list()).data[0].id
                     except: pass

                result = await client.chat.completions.create(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": response.response_text[:4000]}
                    ],
                    response_format={"type": "json_object"}
                )
                parsed = json.loads(result.choices[0].message.content)
                if isinstance(parsed, dict) and "claims" in parsed:
                    claim_texts = parsed["claims"]
                elif isinstance(parsed, list):
                    claim_texts = parsed
                else:
                    claim_texts = [str(parsed)]
                    
                claims = [AtomicClaim(claim_id=str(uuid.uuid4()), text=c) for c in claim_texts[:20]]
        except Exception as e:
            logger.error(f"Claim extraction error: {e}")
            # Fallback
            sentences = response.response_text.split('. ')
            claims = [AtomicClaim(claim_id=str(uuid.uuid4()), text=s.strip()) for s in sentences[:10] if len(s) > 20]
        
        return ClaimsResponse(
            model_id=response.model_id, 
            claims=claims if claims else [AtomicClaim(claim_id=str(uuid.uuid4()), text=response.response_text[:200])]
        )

    tasks = [extract_for_model(r) for r in responses]
    return await asyncio.gather(*tasks)

async def conduct_peer_review(responses: List[ModelResponse], context: LockedContext) -> List[PeerReview]:
    """Each model reviews and ranks the other models' responses anonymously."""
    client, available_models, provider_id = get_active_provider_context()
    reviews = []
    
    if not client:
        return reviews
    
    # Anonymize
    anonymized = []
    model_map = {}
    for i, r in enumerate(responses):
        anon_id = f"Response_{chr(65+i)}"
        model_map[anon_id] = r.model_id
        anonymized.append({"id": anon_id, "text": r.response_text[:2000]})
    
    review_prompt = f"""You are reviewing responses to this query: "{context.normalized_prompt_data.normalized_prompt}"

Constraints: {json.dumps(context.locked_constraints)}

Anonymized responses:
{json.dumps(anonymized, indent=2)}

Provide:
1. accuracy_score (1-10)
2. insight_score (1-10)
3. constraint_adherence (1-10)
4. brief_feedback

Respond with JSON:
{{ "reviews": [ {{ "response_id": "Response_A", "accuracy": 8, "insight": 7, "constraint_adherence": 9, "feedback": "..." }} ] }}"""
    
    # Use up to 2 models
    review_models = [m["id"] for m in available_models[:2]]
    
    async def get_review_from_model(reviewer_model: str):
        try:
            result = await client.chat.completions.create(
                model=reviewer_model,
                messages=[{"role": "user", "content": review_prompt}],
                response_format={"type": "json_object"}
            )
            parsed = json.loads(result.choices[0].message.content)
            for r in parsed.get("reviews", []):
                original_model = model_map.get(r["response_id"], r["response_id"])
                # Extract provider-less name if possible, or just raw
                rev_name = reviewer_model.split('/')[-1] if '/' in reviewer_model else reviewer_model
                
                reviews.append(PeerReview(
                    reviewer_model=rev_name,
                    reviewed_model=original_model,
                    accuracy_score=r.get("accuracy", 5),
                    insight_score=r.get("insight", 5),
                    constraint_adherence=r.get("constraint_adherence", 5),
                    feedback=r.get("feedback", "")
                ))
        except Exception as e:
            logger.error(f"Peer review error from {reviewer_model}: {e}")

    tasks = [get_review_from_model(m) for m in review_models]
    await asyncio.gather(*tasks)
    
    return reviews
