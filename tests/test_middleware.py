from uuid import UUID

from fastapi.testclient import TestClient


def test_request_id_is_generated(
    client: TestClient,
) -> None:
    response = client.get("/health")

    assert response.status_code == 200

    request_id = response.headers.get("X-Request-ID")

    assert request_id is not None

    UUID(request_id)


def test_client_request_id_is_preserved(
    client: TestClient,
) -> None:
    response = client.get(
        "/health",
        headers={
            "X-Request-ID": "teste-request-id-123",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == (
        "teste-request-id-123"
    )


def test_request_id_is_returned_on_authentication_error(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/employees",
        headers={
            "X-Request-ID": "erro-401-teste",
        },
    )

    assert response.status_code == 401
    assert response.headers["X-Request-ID"] == (
        "erro-401-teste"
    )
    assert response.json()["error"]["request_id"] == (
        "erro-401-teste"
    )


def test_generated_request_id_is_in_error_body(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/employees",
    )

    assert response.status_code == 401

    header_request_id = response.headers["X-Request-ID"]
    body_request_id = response.json()["error"]["request_id"]

    assert body_request_id == header_request_id

    UUID(header_request_id)


def test_request_id_is_returned_on_validation_error(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    headers = {
        **viewer_headers,
        "X-Request-ID": "erro-422-teste",
    }

    response = client.get(
        "/api/v1/employees?limit=500",
        headers=headers,
    )

    assert response.status_code == 422
    assert response.headers["X-Request-ID"] == (
        "erro-422-teste"
    )
    assert response.json()["error"]["request_id"] == (
        "erro-422-teste"
    )
