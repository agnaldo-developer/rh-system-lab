from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.audit_log import AuditLog
from tests.conftest import TestingSessionLocal


def get_audit_logs() -> list[AuditLog]:
    with TestingSessionLocal() as db:
        statement = select(AuditLog).order_by(AuditLog.id)

        logs = db.scalars(statement).all()

        for log in logs:
            db.expunge(log)

        return list(logs)


def test_create_department_generates_audit_log(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/departments",
        headers={
            **admin_headers,
            "X-Request-ID": "audit-create-department",
        },
        json={
            "name": "Tecnologia",
            "description": "Departamento de tecnologia",
        },
    )

    assert response.status_code == 201

    department = response.json()
    logs = get_audit_logs()

    assert len(logs) == 1

    audit_log = logs[0]

    assert audit_log.action == "CREATE"
    assert audit_log.entity_type == "department"
    assert audit_log.entity_id == department["id"]
    assert audit_log.request_id == "audit-create-department"
    assert audit_log.details["name"] == "Tecnologia"


def test_update_department_generates_audit_log(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/departments",
        headers=admin_headers,
        json={
            "name": "Tecnologia",
            "description": "Departamento de tecnologia",
        },
    )

    assert create_response.status_code == 201

    department = create_response.json()

    update_response = client.patch(
        f"/api/v1/departments/{department['id']}",
        headers={
            **admin_headers,
            "X-Request-ID": "audit-update-department",
        },
        json={
            "name": "Tecnologia e Inovação",
        },
    )

    assert update_response.status_code == 200

    logs = get_audit_logs()

    assert len(logs) == 2

    audit_log = logs[-1]

    assert audit_log.action == "UPDATE"
    assert audit_log.entity_type == "department"
    assert audit_log.entity_id == department["id"]
    assert audit_log.request_id == "audit-update-department"
    assert audit_log.details["changed_fields"] == ["name"]
    assert audit_log.details["previous_values"]["name"] == (
        "Tecnologia"
    )
    assert audit_log.details["new_values"]["name"] == (
        "Tecnologia e Inovação"
    )


def test_delete_department_generates_audit_log(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/departments",
        headers=admin_headers,
        json={
            "name": "Tecnologia",
            "description": "Departamento de tecnologia",
        },
    )

    assert create_response.status_code == 201

    department = create_response.json()

    delete_response = client.delete(
        f"/api/v1/departments/{department['id']}",
        headers={
            **admin_headers,
            "X-Request-ID": "audit-delete-department",
        },
    )

    assert delete_response.status_code == 204

    logs = get_audit_logs()

    assert len(logs) == 2

    audit_log = logs[-1]

    assert audit_log.action == "DELETE"
    assert audit_log.entity_type == "department"
    assert audit_log.entity_id == department["id"]
    assert audit_log.request_id == "audit-delete-department"
    assert audit_log.details["name"] == "Tecnologia"
