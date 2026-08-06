from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.models.user import User
from tests.conftest import TestingSessionLocal


def create_user(
    *,
    name: str = "Usuário Teste",
    email: str = "usuario@test.com",
    password: str = "SenhaSegura123",
    role: str = "viewer",
    is_active: bool = True,
) -> User:
    with TestingSessionLocal() as db:
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)

        return user


def test_login_success(client: TestClient) -> None:
    create_user()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "usuario@test.com",
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 20


def test_login_with_wrong_password(
    client: TestClient,
) -> None:
    create_user()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "usuario@test.com",
            "password": "SenhaIncorreta123",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == (
        "Invalid email or password."
    )


def test_login_with_unknown_user(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inexistente@test.com",
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == (
        "Invalid email or password."
    )


def test_inactive_user_cannot_login(
    client: TestClient,
) -> None:
    create_user(
        is_active=False,
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "usuario@test.com",
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 403
    assert response.json()["error"]["message"] == "Inactive user."


def test_users_me_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_users_me_with_invalid_token(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer token-invalido",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == (
        "Invalid or expired token."
    )


def test_users_me_returns_authenticated_user(
    client: TestClient,
    viewer_headers: dict[str, str],
    viewer_user: User,
) -> None:
    response = client.get(
        "/api/v1/users/me",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == viewer_user.id
    assert body["email"] == viewer_user.email
    assert body["role"] == "viewer"
    assert "password" not in body
    assert "password_hash" not in body
