from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

# --- Layer 1: Normalization ---
class NormalizedPrompt(BaseModel):
    intent: str
    domain: str
    explicit_constraints: Dict[str, Any]
    inferred_constraints: Dict[str, Any]
    normalized_prompt: str

# --- Layer 2: Constraints ---
class LockedContext(BaseModel):
    locked_constraints: Dict[str, Any]
    constraint_hash: str
    normalized_prompt_data: NormalizedPrompt

# --- Layer 3: Execution ---
class ModelResponse(BaseModel):
    model_id: str
    response_text: str
    token_count: int

# --- Layer 4: Claims ---
class AtomicClaim(BaseModel):
    claim_id: str
    text: str

class ClaimsResponse(BaseModel):
    model_id: str
    claims: List[AtomicClaim]

# --- Layer 4.5: Peer Review (NEW!) ---
class PeerReview(BaseModel):
    reviewer_model: str
    reviewed_model: str
    accuracy_score: int  # 1-10
    insight_score: int  # 1-10
    constraint_adherence: int  # 1-10
    feedback: str

# --- Layer 5: Agreement ---
class ClaimCluster(BaseModel):
    cluster_id: str
    canonical_claim: str
    supporting_models: List[str]
    conflicting_models: List[str]

# --- Layer 6: Scoring ---
class ScoredCluster(BaseModel):
    cluster_id: str
    canonical_claim: str
    supporting_models: List[str]
    conflicting_models: List[str]
    confidence_score: float
    reasons: List[str]

# --- Layer 7: Consensus ---
class FinalConsensus(BaseModel):
    final_answer: str
    confidence: float
    uncertain_areas: List[str]
    reasoning_trace: List[Dict[str, Any]]

# --- Graph State ---
class GraphState(BaseModel):
    raw_input: str
    conversation_id: Optional[str] = None
    normalized: Optional[NormalizedPrompt] = None
    locked_context: Optional[LockedContext] = None
    model_responses: List[ModelResponse] = []
    all_claims: List[ClaimsResponse] = []
    peer_reviews: List[PeerReview] = []  # NEW!
    agreement_clusters: List[ClaimCluster] = []
    scored_clusters: List[ScoredCluster] = []
    consensus: Optional[FinalConsensus] = None
    errors: List[str] = []

# --- Conversation List Item ---
class ConversationSummary(BaseModel):
    id: str
    timestamp: str
    query: str
