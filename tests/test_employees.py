from fastapi.testclient import TestClient


def create_department(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/departments",
        json={
            "name": "Tecnologia",
            "description": "Departamento de tecnologia",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_employee(
    client: TestClient,
    department_id: int,
) -> dict:
    response = client.post(
        "/api/v1/employees",
        json={
            "first_name": "João",
            "last_name": "Silva",
            "email": "joao.silva@empresa.com",
            "phone": "11999999999",
            "document": "12345678900",
            "hire_date": "2026-08-05",
            "salary": 5000.00,
            "department_id": department_id,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_employee(client: TestClient) -> None:
    department = create_department(client)
    employee = create_employee(client, department["id"])

    assert employee["id"] > 0
    assert employee["first_name"] == "João"
    assert employee["department_id"] == department["id"]
    assert employee["is_active"] is True


def test_list_employees(client: TestClient) -> None:
    department = create_department(client)
    create_employee(client, department["id"])

    response = client.get("/api/v1/employees")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_employee_by_id(client: TestClient) -> None:
    department = create_department(client)
    employee = create_employee(client, department["id"])

    response = client.get(
        f"/api/v1/employees/{employee['id']}"
    )

    assert response.status_code == 200
    assert response.json()["email"] == (
        "joao.silva@empresa.com"
    )


def test_update_employee(client: TestClient) -> None:
    department = create_department(client)
    employee = create_employee(client, department["id"])

    response = client.patch(
        f"/api/v1/employees/{employee['id']}",
        json={
            "salary": 6500.00,
            "phone": "11988888888",
        },
    )

    assert response.status_code == 200
    assert response.json()["phone"] == "11988888888"


def test_disable_employee(client: TestClient) -> None:
    department = create_department(client)
    employee = create_employee(client, department["id"])

    response = client.patch(
        f"/api/v1/employees/{employee['id']}",
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_duplicate_employee_returns_conflict(
    client: TestClient,
) -> None:
    department = create_department(client)
    create_employee(client, department["id"])

    response = client.post(
        "/api/v1/employees",
        json={
            "first_name": "João",
            "last_name": "Souza",
            "email": "joao.silva@empresa.com",
            "phone": "11977777777",
            "document": "99999999999",
            "hire_date": "2026-08-05",
            "salary": 6000.00,
            "department_id": department["id"],
        },
    )

    assert response.status_code == 409


def test_employee_with_invalid_department(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/employees",
        json={
            "first_name": "Maria",
            "last_name": "Souza",
            "email": "maria.souza@empresa.com",
            "document": "98765432100",
            "hire_date": "2026-08-05",
            "salary": 4500.00,
            "department_id": 999,
        },
    )

    assert response.status_code == 404


def test_employee_with_invalid_email(
    client: TestClient,
) -> None:
    department = create_department(client)

    response = client.post(
        "/api/v1/employees",
        json={
            "first_name": "Maria",
            "last_name": "Souza",
            "email": "email-invalido",
            "document": "98765432100",
            "hire_date": "2026-08-05",
            "salary": 4500.00,
            "department_id": department["id"],
        },
    )

    assert response.status_code == 422


def test_employee_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/employees/999")

    assert response.status_code == 404
