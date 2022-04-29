import pytest


pytestmark = [pytest.mark.asyncio]


async def test_ok(make_get_request):
    """Эндпоинт /api/v1/healthcheck возвращает 200 статус."""
    response = await make_get_request("/api/v1/healthcheck")

    assert response.status == 200
