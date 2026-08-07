from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.audit_log import AuditLog
from tests.conftest import TestingSessionLocal


def get_user_audit_logs() -> list[AuditLog]:
    with TestingSessionLocal() as db:
        logs = db.scalars(
            select(AuditLog)
            .where(AuditLog.entity_type == "user")
            .order_by(AuditLog.id)
        ).all()

        for log in logs:
            db.expunge(log)

        return list(logs)


def create_target_user(
    client: TestClient,
    admin_headers: dict[str, str],
) -> dict:
    response = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json={
            "name": "Usuário Auditoria",
            "email": "audit.user@rhsystem.com",
            "password": "SenhaSegura123",
            "role": "viewer",
            "is_active": True,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_user_generates_audit_log(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/users",
        headers={
            **admin_headers,
            "X-Request-ID": "user-create-audit",
        },
        json={
            "name": "Usuário Auditoria",
            "email": "audit.user@rhsystem.com",
            "password": "SenhaSegura123",
            "role": "viewer",
            "is_active": True,
        },
    )

    assert response.status_code == 201

    user = response.json()
    logs = get_user_audit_logs()

    assert len(logs) == 1

    audit = logs[0]

    assert audit.action == "CREATE"
    assert audit.entity_type == "user"
    assert audit.entity_id == user["id"]
    assert audit.request_id == "user-create-audit"

    assert audit.details["name"] == "Usuário Auditoria"
    assert audit.details["email"] == "audit.user@rhsystem.com"
    assert audit.details["role"] == "viewer"

    assert "password" not in audit.details
    assert "password_hash" not in audit.details


def test_update_user_generates_audit_log(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    user = create_target_user(
        client,
        admin_headers,
    )

    response = client.patch(
        f"/api/v1/users/{user['id']}",
        headers={
            **admin_headers,
            "X-Request-ID": "user-update-audit",
        },
        json={
            "name": "Usuário Auditoria Atualizado",
            "role": "rh",
        },
    )

    assert response.status_code == 200

    logs = get_user_audit_logs()

    assert len(logs) == 2

    audit = logs[-1]

    assert audit.action == "UPDATE"
    assert audit.entity_type == "user"
    assert audit.entity_id == user["id"]
    assert audit.request_id == "user-update-audit"

    assert "name" in audit.details["changed_fields"]
    assert "role" in audit.details["changed_fields"]

    assert audit.details["previous_values"]["name"] == (
        "Usuário Auditoria"
    )

    assert audit.details["new_values"]["name"] == (
        "Usuário Auditoria Atualizado"
    )

    assert audit.details["new_values"]["role"] == "rh"
    assert audit.details["password_changed"] is False


def test_password_change_does_not_expose_password(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    user = create_target_user(
        client,
        admin_headers,
    )

    response = client.patch(
        f"/api/v1/users/{user['id']}",
        headers={
            **admin_headers,
            "X-Request-ID": "user-password-audit",
        },
        json={
            "password": "NovaSenhaSegura456",
        },
    )

    assert response.status_code == 200

    logs = get_user_audit_logs()

    audit = logs[-1]

    assert audit.action == "UPDATE"
    assert audit.details["password_changed"] is True

    serialized_details = str(audit.details)

    assert "NovaSenhaSegura456" not in serialized_details
    assert "SenhaSegura123" not in serialized_details
    assert "password_hash" not in serialized_details


def test_deactivate_user_generates_audit_log(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    user = create_target_user(
        client,
        admin_headers,
    )

    response = client.delete(
        f"/api/v1/users/{user['id']}",
        headers={
            **admin_headers,
            "X-Request-ID": "user-deactivate-audit",
        },
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    logs = get_user_audit_logs()

    assert len(logs) == 2

    audit = logs[-1]

    assert audit.action == "DEACTIVATE"
    assert audit.entity_type == "user"
    assert audit.entity_id == user["id"]
    assert audit.request_id == "user-deactivate-audit"

    assert audit.details["previous_is_active"] is True
    assert audit.details["new_is_active"] is False
