import asyncio
import uuid
import os
import json
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.models import (
    NormalizedPrompt, LockedContext, ModelResponse, 
    ClaimsResponse, AtomicClaim, ClaimCluster, 
    ScoredCluster, FinalConsensus, PeerReview
)
from app.config.settings import get_keys

# Load environment variables
load_dotenv()

# Data directory for conversation persistence
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "conversations")
os.makedirs(DATA_DIR, exist_ok=True)

# OpenRouter configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def get_api_keys():
    """Get API keys from runtime or fallback."""
    runtime = get_keys()
    return {
        "openrouter": runtime.openai_api_key or os.getenv("OPENROUTER_API_KEY"),
    }

def get_openrouter_client(api_key: str) -> AsyncOpenAI:
    """Create OpenRouter client using OpenAI SDK."""
    return AsyncOpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "Vibe-Coding Consensus Engine"
        }
    )

# ============== LAYER 1: REAL PROMPT NORMALIZATION ==============
async def normalize_prompt(raw_input: str) -> NormalizedPrompt:
    """Use LLM to detect intent and extract constraints from user input."""
    keys = get_api_keys()
    
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
        if keys["openrouter"]:
            client = get_openrouter_client(keys["openrouter"])
            response = await client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_input}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            return NormalizedPrompt(**result)
    except Exception as e:
        print(f"Normalization error: {e}")
    
    # Fallback to basic normalization
    return NormalizedPrompt(
        intent="general_query",
        domain="technology",
        explicit_constraints={},
        inferred_constraints={"language": "english", "depth": "intermediate"},
        normalized_prompt=raw_input
    )

# ============== LAYER 2: CONSTRAINT LOCKING ==============
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

# ============== LAYER 3: PARALLEL LLM EXECUTION ==============
async def execute_parallel_models(context: LockedContext) -> List[ModelResponse]:
    """Query all available models in parallel via OpenRouter."""
    keys = get_api_keys()
    prompt = context.normalized_prompt_data.normalized_prompt
    constraints_context = f"\n\nConstraints: {json.dumps(context.locked_constraints)}"
    full_prompt = prompt + constraints_context
    
    if not keys["openrouter"]:
        return [ModelResponse(model_id="system", response_text="No OpenRouter API key provided.", token_count=0)]
    
    client = get_openrouter_client(keys["openrouter"])
    
    # Define models to query
    models = [
        {"id": "openai/gpt-4o", "name": "gpt-4o"},
        {"id": "anthropic/claude-3.5-sonnet", "name": "claude-3.5-sonnet"},
        {"id": "google/gemini-2.0-flash-exp:free", "name": "gemini-2.0-flash"},
    ]
    
    async def call_model(model_config):
        try:
            completion = await client.chat.completions.create(
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
            return ModelResponse(
                model_id=model_config["name"], 
                response_text=f"Error: {str(e)}", 
                token_count=0
            )
    
    tasks = [call_model(m) for m in models]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]

# ============== LAYER 4: REAL CLAIM EXTRACTION ==============
async def extract_claims(responses: List[ModelResponse]) -> List[ClaimsResponse]:
    """Use LLM to extract atomic claims from each model's response."""
    keys = get_api_keys()
    
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
            if keys["openrouter"]:
                client = get_openrouter_client(keys["openrouter"])
                result = await client.chat.completions.create(
                    model="openai/gpt-4o-mini",
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
            print(f"Claim extraction error: {e}")
            # Fallback: split by sentences
            sentences = response.response_text.split('. ')
            claims = [AtomicClaim(claim_id=str(uuid.uuid4()), text=s.strip()) for s in sentences[:10] if len(s) > 20]
        
        return ClaimsResponse(
            model_id=response.model_id, 
            claims=claims if claims else [AtomicClaim(claim_id=str(uuid.uuid4()), text=response.response_text[:200])]
        )

    tasks = [extract_for_model(r) for r in responses]
    return await asyncio.gather(*tasks)

# ============== LAYER 4.5: PEER REVIEW (NEW!) ==============
async def conduct_peer_review(responses: List[ModelResponse], context: LockedContext) -> List[PeerReview]:
    """Each model reviews and ranks the other models' responses anonymously."""
    keys = get_api_keys()
    reviews = []
    
    if not keys["openrouter"]:
        return reviews
    
    # Anonymize responses
    anonymized = []
    model_map = {}
    for i, r in enumerate(responses):
        anon_id = f"Response_{chr(65+i)}"  # Response_A, Response_B, etc.
        model_map[anon_id] = r.model_id
        anonymized.append({"id": anon_id, "text": r.response_text[:2000]})
    
    review_prompt = f"""You are reviewing responses to this query: "{context.normalized_prompt_data.normalized_prompt}"

Constraints that must be followed: {json.dumps(context.locked_constraints)}

Here are the anonymized responses:
{json.dumps(anonymized, indent=2)}

For each response, provide:
1. accuracy_score (1-10): How factually accurate is it?
2. insight_score (1-10): How insightful and valuable is it?
3. constraint_adherence (1-10): How well does it follow the constraints?
4. brief_feedback: One sentence of constructive feedback

Respond with JSON:
{{
  "reviews": [
    {{"response_id": "Response_A", "accuracy": 8, "insight": 7, "constraint_adherence": 9, "feedback": "..."}},
    ...
  ]
}}"""

    client = get_openrouter_client(keys["openrouter"])
    
    # Use two different models for peer review
    review_models = [
        "openai/gpt-4o-mini",
        "anthropic/claude-3.5-haiku"
    ]
    
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
                reviews.append(PeerReview(
                    reviewer_model=reviewer_model.split('/')[-1],
                    reviewed_model=original_model,
                    accuracy_score=r.get("accuracy", 5),
                    insight_score=r.get("insight", 5),
                    constraint_adherence=r.get("constraint_adherence", 5),
                    feedback=r.get("feedback", "")
                ))
        except Exception as e:
            print(f"Peer review error from {reviewer_model}: {e}")

    tasks = [get_review_from_model(m) for m in review_models]
    await asyncio.gather(*tasks)
    
    return reviews

# ============== LAYER 5: AGREEMENT DETECTION ==============
async def detect_agreement(all_claims: List[ClaimsResponse], peer_reviews: List[PeerReview] = None) -> List[ClaimCluster]:
    """Group similar claims and detect agreement/conflict patterns."""
    all_claim_list = []
    for cr in all_claims:
        for claim in cr.claims:
            all_claim_list.append({"model": cr.model_id, "claim": claim})
    
    if not all_claim_list:
        return []
    
    # Simple keyword-based clustering
    clusters = {}
    for item in all_claim_list:
        text_lower = item["claim"].text.lower()
        
        topics = []
        if any(w in text_lower for w in ["react", "vue", "angular", "frontend", "ui"]):
            topics.append("frontend_framework")
        if any(w in text_lower for w in ["node", "python", "backend", "server", "api"]):
            topics.append("backend")
        if any(w in text_lower for w in ["database", "sql", "mongo", "postgres"]):
            topics.append("database")
        if any(w in text_lower for w in ["deploy", "docker", "kubernetes", "cloud"]):
            topics.append("deployment")
        if not topics:
            topics.append("general")
        
        for topic in topics:
            if topic not in clusters:
                clusters[topic] = {"claims": [], "models": set()}
            clusters[topic]["claims"].append(item["claim"].text)
            clusters[topic]["models"].add(item["model"])
    
    result = []
    for topic, data in clusters.items():
        supporting = list(data["models"])
        all_models = ["gpt-4o", "claude-3.5-sonnet", "gemini-2.0-flash"]
        conflicting = [m for m in all_models if m not in supporting]
        
        result.append(ClaimCluster(
            cluster_id=str(uuid.uuid4())[:8],
            canonical_claim=f"Topic: {topic.replace('_', ' ').title()}",
            supporting_models=supporting,
            conflicting_models=conflicting[:1] if len(conflicting) > 0 else []
        ))
    
    return result

# ============== LAYER 6: CONFIDENCE SCORING ==============
async def score_clusters(clusters: List[ClaimCluster], context: LockedContext, peer_reviews: List[PeerReview] = None) -> List[ScoredCluster]:
    """Calculate confidence scores based on agreement and peer reviews."""
    scored = []
    
    model_scores = {}
    if peer_reviews:
        for pr in peer_reviews:
            if pr.reviewed_model not in model_scores:
                model_scores[pr.reviewed_model] = []
            avg = (pr.accuracy_score + pr.insight_score + pr.constraint_adherence) / 3
            model_scores[pr.reviewed_model].append(avg)
    
    for cluster in clusters:
        reasons = []
        base_score = 0.5
        
        support_count = len(cluster.supporting_models)
        if support_count >= 3:
            base_score += 0.3
            reasons.append(f"Strong agreement: {support_count} models support this")
        elif support_count == 2:
            base_score += 0.15
            reasons.append(f"Moderate agreement: {support_count} models support this")
        else:
            reasons.append("Single model claim - lower confidence")
        
        if cluster.conflicting_models:
            base_score -= 0.1 * len(cluster.conflicting_models)
            reasons.append(f"Conflict detected: {len(cluster.conflicting_models)} models disagree")
        
        if model_scores:
            relevant_scores = []
            for model in cluster.supporting_models:
                if model in model_scores:
                    relevant_scores.extend(model_scores[model])
            if relevant_scores:
                avg_peer_score = sum(relevant_scores) / len(relevant_scores) / 10
                base_score += avg_peer_score * 0.2
                reasons.append(f"Peer review average: {avg_peer_score*10:.1f}/10")
        
        final_score = max(0.1, min(1.0, base_score))
        
        scored.append(ScoredCluster(
            cluster_id=cluster.cluster_id,
            canonical_claim=cluster.canonical_claim,
            supporting_models=cluster.supporting_models,
            conflicting_models=cluster.conflicting_models,
            confidence_score=round(final_score, 2),
            reasons=reasons
        ))
    
    return sorted(scored, key=lambda x: x.confidence_score, reverse=True)

# ============== LAYER 7: CONSENSUS SYNTHESIS ==============
async def synthesize_consensus(scored: List[ScoredCluster], context: LockedContext, responses: List[ModelResponse]) -> FinalConsensus:
    """Use a Chairman model to synthesize the final consensus."""
    keys = get_api_keys()
    
    high_confidence = [s for s in scored if s.confidence_score >= 0.6]
    uncertain = [s for s in scored if s.confidence_score < 0.6]
    
    synthesis_prompt = f"""You are the Chairman of an LLM Council. Your job is to synthesize a final, authoritative answer.

Original Query: {context.normalized_prompt_data.normalized_prompt}
Constraints: {json.dumps(context.locked_constraints)}

High-confidence topics from the council:
{json.dumps([{"topic": s.canonical_claim, "confidence": s.confidence_score, "supporters": s.supporting_models} for s in high_confidence], indent=2)}

Uncertain/disputed topics:
{json.dumps([{"topic": s.canonical_claim, "confidence": s.confidence_score} for s in uncertain], indent=2)}

Individual model responses:
{chr(10).join([f"- {r.model_id}: {r.response_text[:500]}..." for r in responses])}

Synthesize a comprehensive, balanced answer that:
1. Emphasizes high-confidence conclusions
2. Acknowledges areas of uncertainty
3. Follows all stated constraints
4. Is actionable and practical

Respond with JSON:
{{
  "final_answer": "Your comprehensive synthesis...",
  "key_recommendations": ["rec1", "rec2"],
  "uncertain_areas": ["area1", "area2"]
}}"""

    try:
        if keys["openrouter"]:
            client = get_openrouter_client(keys["openrouter"])
            response = await client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[{"role": "user", "content": synthesis_prompt}],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            
            overall_confidence = sum(s.confidence_score for s in scored) / len(scored) if scored else 0.5
            
            return FinalConsensus(
                final_answer=result.get("final_answer", "Synthesis failed"),
                confidence=round(overall_confidence, 2),
                uncertain_areas=result.get("uncertain_areas", []) + [s.canonical_claim for s in uncertain],
                reasoning_trace=[
                    {"step": "normalization", "details": f"Detected intent: {context.normalized_prompt_data.intent}"},
                    {"step": "execution", "details": f"Queried {len(responses)} models via OpenRouter"},
                    {"step": "claims", "details": f"Extracted claims and formed {len(scored)} clusters"},
                    {"step": "scoring", "details": f"High confidence: {len(high_confidence)}, Uncertain: {len(uncertain)}"},
                    {"step": "synthesis", "details": "Chairman (GPT-4o) synthesized final answer"}
                ]
            )
    except Exception as e:
        print(f"Synthesis error: {e}")
    
    return FinalConsensus(
        final_answer="The council was unable to reach a synthesis. Please review individual model responses.",
        confidence=0.3,
        uncertain_areas=["Synthesis failed - review individual responses"],
        reasoning_trace=[{"step": "error", "details": str(e) if 'e' in dir() else "Unknown error"}]
    )

# ============== CONVERSATION PERSISTENCE ==============
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
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    return conversation_id

def load_conversation(conversation_id: str) -> Optional[dict]:
    """Load conversation from JSON file."""
    filepath = os.path.join(DATA_DIR, f"{conversation_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return None

def list_conversations() -> List[dict]:
    """List all saved conversations."""
    conversations = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    conversations.append({
                        "id": data.get("id"),
                        "timestamp": data.get("timestamp"),
                        "query": data.get("state", {}).get("raw_input", "")[:100]
                    })
            except:
                pass
    return sorted(conversations, key=lambda x: x.get("timestamp", ""), reverse=True)
