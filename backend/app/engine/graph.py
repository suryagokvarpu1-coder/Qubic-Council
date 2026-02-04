from app.models import GraphState
import asyncio
import logging

from app.engine.normalization import normalize_prompt, lock_constraints
from app.engine.execution import execute_parallel_models, extract_claims, conduct_peer_review
from app.engine.synthesis import detect_agreement, score_clusters, synthesize_consensus
from app.engine.persistence import save_conversation

class AntigravityEngine:
    """
    Orchestrates the Vibe-Coding Consensus Graph with 8 layers including peer review.
    """
    def __init__(self):
        self.logger = logging.getLogger("AntigravityEngine")
        self.logger.setLevel(logging.INFO)

    async def run(self, raw_input: str, model_count: int = 4) -> GraphState:
        """
        Executes the full graph flow with peer review.
        model_count: Number of models to query (1-4)
        """
        state = GraphState(raw_input=raw_input)
        
        try:
            # Layer 1: Normalization (LLM-powered)
            print("--- Layer 1: Normalization ---")
            state.normalized = await normalize_prompt(state.raw_input)
            print(f"    Intent: {state.normalized.intent}, Domain: {state.normalized.domain}")
            
            # Layer 2: Constraints
            print("--- Layer 2: Locking Constraints ---")
            state.locked_context = await lock_constraints(state.normalized)
            print(f"    Hash: {state.locked_context.constraint_hash}")
            
            # Layer 3: Parallel Execution (with dynamic model count)
            print(f"--- Layer 3: Parallel Execution ({model_count} models) ---")
            state.model_responses = await execute_parallel_models(state.locked_context, model_count=model_count)
            print(f"    Got {len(state.model_responses)} responses")
            
            # Layer 4: Claim Extraction (LLM-powered)
            print("--- Layer 4: Claim Extraction ---")
            state.all_claims = await extract_claims(state.model_responses)
            total_claims = sum(len(c.claims) for c in state.all_claims)
            print(f"    Extracted {total_claims} total claims")
            
            # Layer 4.5: Peer Review (NEW!)
            print("--- Layer 4.5: Peer Review ---")
            state.peer_reviews = await conduct_peer_review(state.model_responses, state.locked_context)
            print(f"    Got {len(state.peer_reviews)} peer reviews")
            
            # Layer 5: Agreement Detection
            print("--- Layer 5: Agreement Detection ---")
            state.agreement_clusters = await detect_agreement(state.all_claims, state.peer_reviews)
            print(f"    Found {len(state.agreement_clusters)} claim clusters")
            
            # Layer 6: Confidence Scoring
            print("--- Layer 6: Confidence Scoring ---")
            state.scored_clusters = await score_clusters(
                state.agreement_clusters, 
                state.locked_context, 
                state.peer_reviews
            )
            high_conf = len([s for s in state.scored_clusters if s.confidence_score >= 0.6])
            print(f"    High confidence: {high_conf}, Low: {len(state.scored_clusters) - high_conf}")
            
            # Layer 7: Consensus Synthesis (Chairman LLM)
            print("--- Layer 7: Final Synthesis ---")
            state.consensus = await synthesize_consensus(
                state.scored_clusters, 
                state.locked_context,
                state.model_responses
            )
            print(f"    Confidence: {state.consensus.confidence}")
            
            # Save conversation
            print("--- Saving Conversation ---")
            state.conversation_id = save_conversation(state.model_dump())
            print(f"    Saved as: {state.conversation_id}")
            
            return state

        except Exception as e:
            self.logger.error(f"Graph execution failed: {e}")
            import traceback
            traceback.print_exc()
            state.errors.append(str(e))
            return state
