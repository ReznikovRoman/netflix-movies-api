from fastapi.testclient import TestClient

from core.config import get_settings


settings = get_settings()


def test_ok(client: TestClient):
    """Ручка /home отдает 200 статус."""
    response = client.get(f"{settings.API_V1_STR}/home")

    assert response.status_code == 200
