from fastapi.testclient import TestClient

from app.models.user import User


def user_payload(
    *,
    email: str = "new.user@example.com",
    role: str = "viewer",
) -> dict:
    return {
        "name": "Novo Usuário",
        "email": email,
        "password": "SenhaSegura123",
        "role": role,
        "is_active": True,
    }


def test_admin_can_create_user(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json=user_payload(),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == "new.user@example.com"
    assert body["role"] == "viewer"
    assert body["is_active"] is True
    assert "password" not in body
    assert "password_hash" not in body


def test_viewer_cannot_create_user(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/users",
        headers=viewer_headers,
        json=user_payload(),
    )

    assert response.status_code == 403


def test_rh_cannot_create_user(
    client: TestClient,
    rh_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/users",
        headers=rh_headers,
        json=user_payload(),
    )

    assert response.status_code == 403


def test_duplicate_user_returns_conflict(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    payload = user_payload()

    first_response = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json=payload,
    )

    assert second_response.status_code == 409


def test_admin_can_list_users(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_user: User,
) -> None:
    response = client.get(
        "/api/v1/users",
        headers=admin_headers,
    )

    assert response.status_code == 200

    users = response.json()

    assert len(users) >= 2
    assert any(
        user["id"] == viewer_user.id
        for user in users
    )


def test_viewer_cannot_list_users(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/users",
        headers=viewer_headers,
    )

    assert response.status_code == 403


def test_admin_can_get_user_by_id(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_user: User,
) -> None:
    response = client.get(
        f"/api/v1/users/{viewer_user.id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["email"] == viewer_user.email


def test_user_not_found(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/users/999",
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_admin_can_update_user(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_user: User,
) -> None:
    response = client.patch(
        f"/api/v1/users/{viewer_user.id}",
        headers=admin_headers,
        json={
            "name": "Viewer Atualizado",
            "role": "rh",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "Viewer Atualizado"
    assert body["role"] == "rh"


def test_update_user_with_duplicate_email_returns_conflict(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_user: User,
    rh_user: User,
) -> None:
    response = client.patch(
        f"/api/v1/users/{viewer_user.id}",
        headers=admin_headers,
        json={
            "email": rh_user.email,
        },
    )

    assert response.status_code == 409


def test_admin_can_deactivate_user(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_user: User,
) -> None:
    response = client.delete(
        f"/api/v1/users/{viewer_user.id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_deactivated_user_cannot_access_me(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
    viewer_user: User,
) -> None:
    deactivate_response = client.delete(
        f"/api/v1/users/{viewer_user.id}",
        headers=admin_headers,
    )

    assert deactivate_response.status_code == 200

    response = client.get(
        "/api/v1/users/me",
        headers=viewer_headers,
    )

    assert response.status_code == 403
    assert response.json()["error"]["message"] == (
    "Inactive user."
)
