import httpx
import pytest
import pytest_asyncio

from app.main import app


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as session:
        yield session


@pytest.mark.asyncio
async def test_saathi_chat_session_and_request_id(client):
    response = await client.post(
        "/api/v1/chat",
        headers={"X-Request-ID": "request-test-1"},
        json={
            "message": "nearby mandi for onion",
            "context": {"lat": 18.52, "lng": 73.86, "crop_id": "onion", "quantity_quintal": 10},
            "client": {"platform": "android", "app_version": "1.0.0", "device_id": "test-device"},
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["session_id"]
    assert data["meta"]["request_id"] == "request-test-1"
    assert data["meta"]["grounded"] is True

    follow_up = await client.post(
        "/api/v1/chat",
        json={"session_id": data["session_id"], "message": "Should I sell now?", "client": {"device_id": "test-device"}},
    )
    assert follow_up.status_code == 200
    assert follow_up.json()["data"]["session_id"] == data["session_id"]


@pytest.mark.asyncio
async def test_chat_starters_feedback_and_validation(client):
    starters = await client.get("/api/v1/chat/starters?lang=mr")
    assert starters.status_code == 200
    assert len(starters.json()["data"]) == 4
    feedback = await client.post("/api/v1/chat/feedback", json={"request_id": "request-test-1", "rating": "up"})
    assert feedback.status_code == 200
    invalid = await client.post("/api/v1/chat", json={"message": ""})
    assert invalid.status_code == 422
    assert invalid.json()["code"] == "VALIDATION_ERROR"
