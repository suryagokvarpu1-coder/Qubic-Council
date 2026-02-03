import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Online"

@pytest.mark.asyncio
async def test_run_consensus_no_prompt():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/run", json={})
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_update_keys():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/settings/keys", json={"openai_api_key": "sk-test-key"})
    assert response.status_code == 200
    assert response.json()["status"] == "Keys updated successfully"

@pytest.mark.asyncio
async def test_conversations_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/conversations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
