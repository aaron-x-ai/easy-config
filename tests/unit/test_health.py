import pytest
from fastapi.testclient import TestClient

from easy_config.server.app import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_config_page(client: TestClient) -> None:
    response = client.get("/config")
    assert response.status_code == 200
    assert "Easy Config" in response.text
