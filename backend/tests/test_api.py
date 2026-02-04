import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_root_returns_html():
    """Test that root endpoint returns the loading page HTML"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    # Root now returns HTML (loadingpage.html), not JSON
    assert "text/html" in response.headers.get("content-type", "")

@pytest.mark.asyncio
async def test_api_status():
    """Test the /api/status endpoint returns correct JSON with provider info"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Online"
    assert "features" in data
    assert isinstance(data["features"], list)
    assert "providers_configured" in data
    assert isinstance(data["providers_configured"], list)

@pytest.mark.asyncio
async def test_mainpage_returns_html():
    """Test that /mainpage returns the main page HTML"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/mainpage")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

@pytest.mark.asyncio
async def test_run_consensus_no_prompt():
    """Test that /run returns validation error when prompt is missing"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/run", json={})
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_run_consensus_empty_prompt():
    """Test that /run returns error for empty prompt string"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/run", json={"prompt": ""})
    assert response.status_code == 400  # Bad request for empty prompt

@pytest.mark.asyncio
async def test_run_consensus_valid_prompt():
    """Test that /run accepts a valid prompt (will use fallbacks without API key)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/run", json={"prompt": "Test query", "model_count": 2})
    assert response.status_code == 200
    data = response.json()
    assert "raw_input" in data
    assert data["raw_input"] == "Test query"

@pytest.mark.asyncio
async def test_run_consensus_model_count_validation():
    """Test that model_count is validated correctly"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Test with model_count > 4 (should be clamped to 4)
        response = await ac.post("/run", json={"prompt": "Test", "model_count": 10})
    assert response.status_code == 200

# ===== MULTI-PROVIDER API KEY TESTS =====

@pytest.mark.asyncio
async def test_update_openrouter_key_only():
    """Test updating only OpenRouter API key"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/settings/keys", json={
            "openrouter_api_key": "sk-or-v1-" + "a" * 64
        })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Keys updated successfully"
    assert "openrouter" in data["updated_providers"]
    assert "openrouter" in data["available_providers"]

@pytest.mark.asyncio
async def test_update_groq_key_only():
    """Test updating only Groq API key"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/settings/keys", json={
            "groq_api_key": "gsk_" + "a" * 52
        })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Keys updated successfully"
    assert "groq" in data["updated_providers"]
    assert "groq" in data["available_providers"]

@pytest.mark.asyncio
async def test_update_both_keys():
    """Test updating both OpenRouter and Groq keys at once"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/settings/keys", json={
            "openrouter_api_key": "sk-or-v1-" + "b" * 64,
            "groq_api_key": "gsk_" + "b" * 52
        })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Keys updated successfully"
    assert "openrouter" in data["updated_providers"]
    assert "groq" in data["updated_providers"]
    assert len(data["available_providers"]) == 2

@pytest.mark.asyncio
async def test_legacy_universal_key_openrouter():
    """Test legacy universal_key is correctly detected as OpenRouter"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/settings/keys", json={
            "universal_key": "sk-or-v1-" + "c" * 64
        })
    assert response.status_code == 200
    data = response.json()
    assert "openrouter" in data["updated_providers"]

@pytest.mark.asyncio
async def test_legacy_universal_key_groq():
    """Test legacy universal_key is correctly detected as Groq"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/settings/keys", json={
            "universal_key": "gsk_" + "c" * 52
        })
    assert response.status_code == 200
    data = response.json()
    assert "groq" in data["updated_providers"]

@pytest.mark.asyncio
async def test_keys_status_endpoint():
    """Test the /settings/keys/status endpoint returns provider info"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First set some keys
        await ac.post("/settings/keys", json={
            "openrouter_api_key": "sk-or-v1-" + "d" * 64,
            "groq_api_key": "gsk_" + "d" * 52
        })
        
        # Then check status
        response = await ac.get("/settings/keys/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "providers" in data
    assert "openrouter" in data["providers"]
    assert "groq" in data["providers"]
    assert data["providers"]["openrouter"]["configured"] == True
    assert data["providers"]["groq"]["configured"] == True
    
    # Should have key prefixes but not full keys
    assert "key_prefix" in data["providers"]["openrouter"]
    assert data["providers"]["openrouter"]["key_prefix"].endswith("...")

@pytest.mark.asyncio
async def test_keys_status_no_exposure():
    """Verify that key status doesn't expose full API keys"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Set a key
        test_key = "sk-or-v1-supersecretkey123456789012345678901234567890123456"
        await ac.post("/settings/keys", json={
            "openrouter_api_key": test_key
        })
        
        # Get status
        response = await ac.get("/settings/keys/status")
    
    assert response.status_code == 200
    data = response.json()
    
    # The full key should not appear anywhere in the response
    response_text = str(data)
    assert "supersecretkey" not in response_text
    
    # But we should have a truncated prefix
    assert data["providers"]["openrouter"]["key_prefix"].startswith("sk-or-v1-")
    assert len(data["providers"]["openrouter"]["key_prefix"]) < len(test_key)

@pytest.mark.asyncio
async def test_clear_key_by_empty_string():
    """Test that sending empty string clears a key"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First set a key
        await ac.post("/settings/keys", json={
            "openrouter_api_key": "sk-or-v1-" + "e" * 64
        })
        
        # Check it's set
        status1 = await ac.get("/settings/keys/status")
        assert status1.json()["providers"]["openrouter"]["configured"] == True
        
        # Clear it
        await ac.post("/settings/keys", json={
            "openrouter_api_key": ""
        })
        
        # Check it's cleared
        status2 = await ac.get("/settings/keys/status")
        assert status2.json()["providers"]["openrouter"]["configured"] == False

@pytest.mark.asyncio
async def test_conversations_list():
    """Test listing conversations"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/conversations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_conversation_not_found():
    """Test getting a non-existent conversation"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/conversations/non-existent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
