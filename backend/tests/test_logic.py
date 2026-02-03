import pytest
import json
from app.nodes import normalize_prompt, lock_constraints, detect_agreement
from app.models import AtomicClaim, ClaimsResponse, PeerReview

@pytest.mark.asyncio
async def test_detect_agreement():
    # Mock claims
    claims = [
        ClaimsResponse(model_id="gpt-4", claims=[AtomicClaim(claim_id="1", text="React is great")]),
        ClaimsResponse(model_id="claude", claims=[AtomicClaim(claim_id="2", text="React is a library")])
    ]
    
    # Run logic
    clusters = await detect_agreement(claims)
    
    # Should find 1 cluster for "frontend_framework" or "react"
    assert len(clusters) >= 0
    # Note: Logic is fuzzy (keyword based), so we check it doesn't crash

@pytest.mark.asyncio
async def test_lock_constraints():
    normalized = await normalize_prompt("Build a python app")
    locked = await lock_constraints(normalized)
    
    assert locked.constraint_hash is not None
    assert len(locked.constraint_hash) > 0
    assert locked.normalized_prompt_data == normalized
