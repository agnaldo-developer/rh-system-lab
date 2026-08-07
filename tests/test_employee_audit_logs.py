from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.audit_log import AuditLog
from tests.conftest import TestingSessionLocal


def get_audit_logs() -> list[AuditLog]:
    with TestingSessionLocal() as db:
        logs = db.scalars(
            select(AuditLog).order_by(AuditLog.id)
        ).all()

        for log in logs:
            db.expunge(log)

        return list(logs)


def create_department(
    client: TestClient,
    admin_headers: dict[str, str],
) -> dict:
    response = client.post(
        "/api/v1/departments",
        headers=admin_headers,
        json={
            "name": "Tecnologia",
            "description": "Departamento de tecnologia",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_employee(
    client: TestClient,
    admin_headers: dict[str, str],
    department_id: int,
) -> dict:
    response = client.post(
        "/api/v1/employees",
        headers=admin_headers,
        json={
            "first_name": "Carlos",
            "last_name": "Silva",
            "email": "carlos.audit@empresa.com",
            "phone": "11999999999",
            "document": "99911122233",
            "hire_date": "2026-08-06",
            "salary": 5000,
            "department_id": department_id,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_employee_generates_audit_log(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    response = client.post(
        "/api/v1/employees",
        headers={
            **admin_headers,
            "X-Request-ID": "employee-create",
        },
        json={
            "first_name": "Carlos",
            "last_name": "Silva",
            "email": "carlos.audit@empresa.com",
            "phone": "11999999999",
            "document": "99911122233",
            "hire_date": "2026-08-06",
            "salary": 5000,
            "department_id": department["id"],
        },
    )

    assert response.status_code == 201

    employee = response.json()

    logs = get_audit_logs()

    employee_logs = [
        log
        for log in logs
        if log.entity_type == "employee"
    ]

    assert len(employee_logs) == 1

    audit = employee_logs[0]

    assert audit.action == "CREATE"
    assert audit.entity_id == employee["id"]
    assert audit.request_id == "employee-create"


def test_update_employee_generates_audit_log(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    employee = create_employee(
        client,
        admin_headers,
        department["id"],
    )

    response = client.patch(
        f"/api/v1/employees/{employee['id']}",
        headers={
            **admin_headers,
            "X-Request-ID": "employee-update",
        },
        json={
            "salary": 7500,
        },
    )

    assert response.status_code == 200

    logs = get_audit_logs()

    employee_logs = [
        log
        for log in logs
        if log.entity_type == "employee"
    ]

    assert len(employee_logs) == 2

    audit = employee_logs[-1]

    assert audit.action == "UPDATE"
    assert audit.entity_id == employee["id"]
    assert audit.request_id == "employee-update"
    assert audit.details["changed_fields"] == ["salary"]
    assert audit.details["new_values"]["salary"] == 7500


def test_delete_employee_generates_audit_log(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    employee = create_employee(
        client,
        admin_headers,
        department["id"],
    )

    response = client.delete(
        f"/api/v1/employees/{employee['id']}",
        headers={
            **admin_headers,
            "X-Request-ID": "employee-delete",
        },
    )

    assert response.status_code == 204

    logs = get_audit_logs()

    employee_logs = [
        log
        for log in logs
        if log.entity_type == "employee"
    ]

    assert len(employee_logs) == 2

    audit = employee_logs[-1]

    assert audit.action == "DELETE"
    assert audit.entity_id == employee["id"]
    assert audit.request_id == "employee-delete"
    assert audit.details["email"] == (
        "carlos.audit@empresa.com"
    )