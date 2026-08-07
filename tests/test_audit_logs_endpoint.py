from fastapi.testclient import TestClient

from app.core.database import get_db
from app.services.audit_service import create_audit_log


def seed_audit_logs(client: TestClient) -> None:
    app = client.app

    override = app.dependency_overrides[get_db]

    db = next(override())

    try:
        create_audit_log(
            db,
            user_id=None,
            action="LOGIN_FAILED",
            entity_type="authentication",
            entity_id=None,
            request_id="audit-login-failed",
            details={
                "email": "teste@rhsystem.com",
            },
            commit=True,
        )

        create_audit_log(
            db,
            user_id=None,
            action="CREATE",
            entity_type="employee",
            entity_id=10,
            request_id="audit-employee-create",
            details={
                "name": "Carlos",
            },
            commit=True,
        )
    finally:
        db.close()


def test_audit_logs_require_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/audit-logs"
    )

    assert response.status_code == 401


def test_viewer_cannot_list_audit_logs(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/audit-logs",
        headers=viewer_headers,
    )

    assert response.status_code == 403


def test_admin_can_list_audit_logs(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit-logs",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_audit_logs_by_action(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit-logs?action=LOGIN_FAILED",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["action"] == (
        "LOGIN_FAILED"
    )


def test_filter_audit_logs_by_entity_type(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit-logs?entity_type=employee",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["entity_type"] == (
        "employee"
    )


def test_audit_logs_reject_invalid_limit(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/audit-logs?limit=500",
        headers=admin_headers,
    )

    assert response.status_code == 422
