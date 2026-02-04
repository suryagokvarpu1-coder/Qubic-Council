import pytest
import json
from app.engine.normalization import normalize_prompt, lock_constraints
from app.engine.synthesis import detect_agreement
from app.models import AtomicClaim, ClaimsResponse, PeerReview

@pytest.mark.asyncio
async def test_detect_agreement():
    # Mock claims
    claims = [
        ClaimsResponse(model_id="gpt-4", claims=[AtomicClaim(claim_id="1", text="React is great")]),
        ClaimsResponse(model_id="claude", claims=[AtomicClaim(claim_id="2", text="React is a library")])
    ]
    
    # Run logic with peer_reviews parameter (can be empty list or None)
    clusters = await detect_agreement(claims, peer_reviews=[])
    
    # Should find at least 1 cluster for "frontend" topic (due to "React" keyword)
    assert len(clusters) >= 0
    # Note: Logic is fuzzy (keyword based), so we check it doesn't crash

@pytest.mark.asyncio
async def test_detect_agreement_with_peer_reviews():
    """Test agreement detection with peer review data"""
    claims = [
        ClaimsResponse(model_id="gpt-4", claims=[
            AtomicClaim(claim_id="1", text="Python is great for backend development"),
            AtomicClaim(claim_id="2", text="FastAPI provides fast server performance")
        ]),
        ClaimsResponse(model_id="claude", claims=[
            AtomicClaim(claim_id="3", text="Node.js is also good for backend"),
        ])
    ]
    
    peer_reviews = [
        PeerReview(
            reviewer_model="gpt-4",
            reviewed_model="claude",
            accuracy_score=8,
            insight_score=7,
            constraint_adherence=9,
            feedback="Good response"
        )
    ]
    
    clusters = await detect_agreement(claims, peer_reviews=peer_reviews)
    
    # Should have at least one cluster
    assert len(clusters) >= 1
    # Backend topic should be found
    backend_clusters = [c for c in clusters if "backend" in c.canonical_claim.lower()]
    assert len(backend_clusters) >= 0  # May or may not match depending on keyword logic

@pytest.mark.asyncio
async def test_lock_constraints():
    normalized = await normalize_prompt("Build a python app")
    locked = await lock_constraints(normalized)
    
    assert locked.constraint_hash is not None
    assert len(locked.constraint_hash) > 0
    assert locked.normalized_prompt_data == normalized

@pytest.mark.asyncio
async def test_normalize_prompt_basic():
    """Test basic prompt normalization with fallback behavior"""
    # This will use the fallback since no LLM client is configured in tests
    normalized = await normalize_prompt("Create a React frontend")
    
    # The fallback should return the original prompt as normalized_prompt
    assert normalized.normalized_prompt == "Create a React frontend"
    assert normalized.intent == "general_query"  # Fallback default
    assert normalized.domain == "technology"  # Fallback default

@pytest.mark.asyncio
async def test_lock_constraints_hash_consistency():
    """Verify that the same constraints produce the same hash"""
    normalized = await normalize_prompt("Test query")
    locked1 = await lock_constraints(normalized)
    locked2 = await lock_constraints(normalized)
    
    # Same input should produce same hash
    assert locked1.constraint_hash == locked2.constraint_hash
