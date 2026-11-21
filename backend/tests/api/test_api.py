import httpx
import pytest
import pytest_asyncio

from app.main import app


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as session:
        yield session


@pytest.mark.asyncio
async def test_health_and_crops(client):
    assert (await client.get("/api/v1/health")).status_code == 200
    response = await client.get("/api/v1/crops")
    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == "onion"
    assert {crop["category"] for crop in response.json()["data"]} == {"vegetable", "grain", "fruit"}


@pytest.mark.asyncio
async def test_next_crop_suggestions_use_category_history_and_water(client):
    response = await client.post("/api/v1/insights/next-crops", json={"category": "grain", "crop_history": ["soybean"], "water_availability": "low"})
    assert response.status_code == 200
    suggestions = response.json()["data"]
    assert suggestions
    assert all(item["crop"]["crop_id"] != "soybean" for item in suggestions)
    assert all("water fit" in item["reason"].lower() for item in suggestions)


@pytest.mark.asyncio
async def test_recommend_validation_and_response(client):
    invalid = await client.post("/api/v1/recommend", json={"crop_id": "onion", "quantity_quintal": 0, "farmer_location": {"lat": 18, "lng": 73}})
    assert invalid.status_code == 422
    response = await client.post("/api/v1/recommend", json={"crop_id": "onion", "quantity_quintal": 10, "farmer_location": {"lat": 18.52, "lng": 73.86}, "radius_km": 50})
    assert response.status_code == 200
    assert response.json()["data"]["recommendations"][0]["rank"] == 1


@pytest.mark.asyncio
async def test_admin_authentication(client):
    assert (await client.get("/api/v1/admin/summary")).status_code == 401
    login = await client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "change-me"})
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]
    assert (await client.get("/api/v1/admin/summary", headers={"Authorization": f"Bearer {token}"})).status_code == 200
