import pytest


pytestmark = [pytest.mark.asyncio]


async def test_ok(api_client):
    """Эндпоинт /api/v1/healthcheck возвращает 200 статус."""
    response = await api_client.get("/api/v1/healthcheck")

    assert response["status"] == "ok"
