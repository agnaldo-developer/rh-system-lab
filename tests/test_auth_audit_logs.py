from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.audit_log import AuditLog
from tests.conftest import TestingSessionLocal


def get_auth_audit_logs() -> list[AuditLog]:
    with TestingSessionLocal() as db:
        logs = db.scalars(
            select(AuditLog)
            .where(
                AuditLog.entity_type
                == "authentication"
            )
            .order_by(AuditLog.id)
        ).all()

        for log in logs:
            db.expunge(log)

        return list(logs)


def test_successful_login_generates_audit_log(
    client: TestClient,
    admin_user,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        headers={
            "X-Request-ID": "login-success-audit",
        },
        json={
            "email": admin_user.email,
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 200

    logs = get_auth_audit_logs()

    assert len(logs) == 1

    audit = logs[0]

    assert audit.action == "LOGIN_SUCCESS"
    assert audit.entity_type == "authentication"
    assert audit.user_id == admin_user.id
    assert audit.request_id == "login-success-audit"

    assert audit.details["email"] == admin_user.email
    assert audit.details["role"] == admin_user.role
    assert "client_ip" in audit.details


def test_wrong_password_generates_failed_login_audit(
    client: TestClient,
    admin_user,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        headers={
            "X-Request-ID": "login-wrong-password",
        },
        json={
            "email": admin_user.email,
            "password": "senha-errada",
        },
    )

    assert response.status_code == 401

    logs = get_auth_audit_logs()

    assert len(logs) == 1

    audit = logs[0]

    assert audit.action == "LOGIN_FAILED"
    assert audit.user_id == admin_user.id
    assert audit.request_id == "login-wrong-password"

    assert audit.details["reason"] == (
        "invalid_credentials"
    )


def test_unknown_user_generates_failed_login_audit(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        headers={
            "X-Request-ID": "login-unknown-user",
        },
        json={
            "email": "naoexiste@rhsystem.com",
            "password": "SenhaQualquer123",
        },
    )

    assert response.status_code == 401

    logs = get_auth_audit_logs()

    assert len(logs) == 1

    audit = logs[0]

    assert audit.action == "LOGIN_FAILED"
    assert audit.user_id is None
    assert audit.entity_id is None
    assert audit.request_id == "login-unknown-user"

    assert audit.details["email"] == (
        "naoexiste@rhsystem.com"
    )

    assert audit.details["reason"] == (
        "invalid_credentials"
    )


def test_inactive_user_generates_failed_login_audit(
    client: TestClient,
    inactive_user,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        headers={
            "X-Request-ID": "login-inactive-user",
        },
        json={
            "email": inactive_user.email,
            "password": "SenhaInativa123",
},
    )

    assert response.status_code == 403

    logs = get_auth_audit_logs()

    assert len(logs) == 1

    audit = logs[0]

    assert audit.action == "LOGIN_FAILED"
    assert audit.user_id == inactive_user.id
    assert audit.request_id == "login-inactive-user"

    assert audit.details["reason"] == (
        "inactive_user"
    )


def test_login_audit_never_exposes_password(
    client: TestClient,
    admin_user,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email,
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 200

    logs = get_auth_audit_logs()
    audit = logs[0]

    serialized_details = str(audit.details)

    assert "SenhaSegura123" not in serialized_details
    assert "password" not in audit.details
    assert "password_hash" not in audit.details
