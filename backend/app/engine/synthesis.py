import json
import uuid
from typing import List
from app.models import ClaimsResponse, AtomicClaim, ClaimCluster, ScoredCluster, FinalConsensus, ModelResponse, LockedContext, PeerReview
from app.engine.llm import get_active_provider_context
from app.engine.providers import PROVIDER_OPENROUTER, PROVIDER_GROQ
from app.utils.logger import get_logger

logger = get_logger(__name__)

async def detect_agreement(all_claims: List[ClaimsResponse], peer_reviews: List[PeerReview] = None) -> List[ClaimCluster]:
    """Group similar claims and detect agreement/conflict patterns."""
    all_claim_list = []
    for cr in all_claims:
        for claim in cr.claims:
            all_claim_list.append({"model": cr.model_id, "claim": claim})
    
    if not all_claim_list:
        return []
    
    clusters = {}
    for item in all_claim_list:
        text_lower = item["claim"].text.lower()
        
        # Simple clustering - enhanced with more keywords
        topics = []
        keywords = {
            "frontend": ["react", "vue", "angular", "frontend", "ui", "css", "html", "browser"],
            "backend": ["node", "python", "backend", "server", "api", "database", "sql", "fastapi"],
            "deployment": ["deploy", "docker", "kubernetes", "cloud", "aws", "azure", "ci/cd"],
            "security": ["auth", "security", "token", "encryption", "https"],
            "performance": ["fast", "slow", "optimize", "cache", "latency"]
        }
        
        for key, words in keywords.items():
            if any(w in text_lower for w in words):
                topics.append(key)
        
        if not topics:
            topics.append("general")
        
        for topic in topics:
            if topic not in clusters:
                clusters[topic] = {"claims": [], "models": set()}
            clusters[topic]["claims"].append(item["claim"].text)
            clusters[topic]["models"].add(item["model"])
    
    result = []
    # Hardcoded known models for conflict detection
    # This should ideally come from available_models but hardcoding common ones for MVP conflict logic is okay
    known_models = ["gpt-4o", "claude-3.5-sonnet", "gemini-2.0-flash", "llama-3.3-70b-groq"]
    
    for topic, data in clusters.items():
        supporting = list(data["models"])
        conflicting = [m for m in known_models if m not in supporting and any(m in c["model"] for c in all_claim_list)]
        
        result.append(ClaimCluster(
            cluster_id=str(uuid.uuid4())[:8],
            canonical_claim=f"Topic: {topic.replace('_', ' ').title()}",
            supporting_models=supporting,
            conflicting_models=conflicting[:1] if len(conflicting) > 0 else []
        ))
    
    return result

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
                # Fuzzy match model ID if needed, but robust map usually works
                for m_key in model_scores:
                    if model in m_key or m_key in model:
                        relevant_scores.extend(model_scores[m_key])
            
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

async def synthesize_consensus(scored: List[ScoredCluster], context: LockedContext, responses: List[ModelResponse]) -> FinalConsensus:
    """Use a Chairman model to synthesize the final consensus."""
    client, available_models, provider_id = get_active_provider_context()
    
    high_confidence = [s for s in scored if s.confidence_score >= 0.6]
    uncertain = [s for s in scored if s.confidence_score < 0.6]
    
    synthesis_prompt = f"""You are the Chairman of an LLM Council. Your job is to synthesize a final, authoritative answer.

Original Query: {context.normalized_prompt_data.normalized_prompt}
Constraints: {json.dumps(context.locked_constraints)}

High-confidence topics:
{json.dumps([{"topic": s.canonical_claim, "confidence": s.confidence_score} for s in high_confidence], indent=2)}

Uncertain/disputed topics:
{json.dumps([{"topic": s.canonical_claim, "confidence": s.confidence_score} for s in uncertain], indent=2)}

Model responses:
{chr(10).join([f"- {r.model_id}: {r.response_text[:500]}..." for r in responses])}

Synthesize a comprehensive answer that:
1. Emphasizes high-confidence conclusions
2. Acknowledges uncertainty
3. Follows constraints
4. Is actionable

Respond with JSON:
{{
  "final_answer": "...",
  "key_recommendations": ["..."],
  "uncertain_areas": ["..."]
}}"""

    try:
        if client:
            model = "openai/gpt-4o" if provider_id == PROVIDER_OPENROUTER else available_models[0]["id"]
            if provider_id == PROVIDER_GROQ: model = "llama-3.3-70b-versatile" # Prefer strongest 
            
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": synthesis_prompt}],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            
            confidence = sum(s.confidence_score for s in scored) / len(scored) if scored else 0.5
            
            return FinalConsensus(
                final_answer=result.get("final_answer", "Synthesis failed"),
                confidence=round(confidence, 2),
                uncertain_areas=result.get("uncertain_areas", []) + [s.canonical_claim for s in uncertain],
                reasoning_trace=[
                    {"step": "normalization", "details": f"Intent: {context.normalized_prompt_data.intent}"},
                    {"step": "execution", "details": f"Queried {len(responses)} models"},
                    {"step": "synthesis", "details": f"Chairman ({model}) synthesized answer"}
                ]
            )
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
    
    return FinalConsensus(
        final_answer="The council was unable to reach a synthesis. Please review individual model responses.",
        confidence=0.3,
        uncertain_areas=["Synthesis failed"],
        reasoning_trace=[{"step": "error", "details": "Synthesis failed"}]
    )
