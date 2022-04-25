from fastapi.testclient import TestClient

from core.config import get_settings


settings = get_settings()


def test_ok(client: TestClient):
    """Ручка /healthcheck отдает 200 статус."""
    response = client.get(f"{settings.API_V1_STR}/healthcheck")

    assert response.status_code == 200
