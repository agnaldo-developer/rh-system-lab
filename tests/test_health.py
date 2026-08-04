from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app, get_db


class FakeDatabaseSession:
    def execute(self, _statement) -> None:
        return None


def override_get_db() -> Generator[Session, None, None]:
    yield FakeDatabaseSession()  # type: ignore[misc]


def test_health_endpoint() -> None:
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    try:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "database": "connected",
        }
    finally:
        app.dependency_overrides.clear()
