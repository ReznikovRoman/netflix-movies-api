from fastapi.testclient import TestClient


def test_ok(client: TestClient):
    """Ручка /healthcheck отдает 200 статус."""
    response = client.get("/api/v1/healthcheck")

    assert response.status_code == 200
