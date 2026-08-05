from fastapi.testclient import TestClient


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
    department_id: int,
    admin_headers: dict[str, str],
) -> dict:
    response = client.post(
        "/api/v1/employees",
        headers=admin_headers,
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


def test_create_employee(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    employee = create_employee(
        client,
        department["id"],
        admin_headers,
    )

    assert employee["id"] > 0
    assert employee["first_name"] == "João"
    assert employee["department_id"] == department["id"]
    assert employee["is_active"] is True


def test_list_employees(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    create_employee(
        client,
        department["id"],
        admin_headers,
    )

    response = client.get(
        "/api/v1/employees",
        headers=viewer_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_employee_by_id(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    employee = create_employee(
        client,
        department["id"],
        admin_headers,
    )

    response = client.get(
        f"/api/v1/employees/{employee['id']}",
        headers=viewer_headers,
    )

    assert response.status_code == 200
    assert response.json()["email"] == (
        "joao.silva@empresa.com"
    )


def test_update_employee(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    employee = create_employee(
        client,
        department["id"],
        admin_headers,
    )

    response = client.patch(
        f"/api/v1/employees/{employee['id']}",
        headers=admin_headers,
        json={
            "salary": 6500.00,
            "phone": "11988888888",
        },
    )

    assert response.status_code == 200
    assert response.json()["phone"] == "11988888888"


def test_disable_employee(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    employee = create_employee(
        client,
        department["id"],
        admin_headers,
    )

    response = client.patch(
        f"/api/v1/employees/{employee['id']}",
        headers=admin_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_duplicate_employee_returns_conflict(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    create_employee(
        client,
        department["id"],
        admin_headers,
    )

    response = client.post(
        "/api/v1/employees",
        headers=admin_headers,
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
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/employees",
        headers=admin_headers,
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
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    response = client.post(
        "/api/v1/employees",
        headers=admin_headers,
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


def test_employee_not_found(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/employees/999",
        headers=viewer_headers,
    )

    assert response.status_code == 404


def test_employees_require_authentication(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/employees")

    assert response.status_code == 401


def test_viewer_cannot_create_employee(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/employees",
        headers=viewer_headers,
        json={
            "first_name": "Maria",
            "last_name": "Souza",
            "email": "maria.souza@empresa.com",
            "document": "98765432100",
            "hire_date": "2026-08-05",
            "salary": 4500.00,
            "department_id": 1,
        },
    )

    assert response.status_code == 403


def test_rh_can_create_employee(
    client: TestClient,
    rh_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    response = client.post(
        "/api/v1/employees",
        headers=rh_headers,
        json={
            "first_name": "Ana",
            "last_name": "Costa",
            "email": "ana.costa@empresa.com",
            "document": "11122233344",
            "hire_date": "2026-08-05",
            "salary": 4800.00,
            "department_id": department["id"],
        },
    )

    assert response.status_code == 201
def create_custom_employee(
    client: TestClient,
    admin_headers: dict[str, str],
    department_id: int,
    *,
    first_name: str,
    last_name: str,
    email: str,
    document: str,
    salary: float,
    is_active: bool = True,
) -> dict:
    response = client.post(
        "/api/v1/employees",
        headers=admin_headers,
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": "11999999999",
            "document": document,
            "hire_date": "2026-08-05",
            "salary": salary,
            "department_id": department_id,
        },
    )

    assert response.status_code == 201

    employee = response.json()

    if not is_active:
        update_response = client.patch(
            f"/api/v1/employees/{employee['id']}",
            headers=admin_headers,
            json={
                "is_active": False,
            },
        )

        assert update_response.status_code == 200
        employee = update_response.json()

    return employee


def test_employees_pagination_limit(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    employees = [
        ("Ana", "Costa", "ana@example.com", "11111111111", 4000),
        ("Bruno", "Lima", "bruno@example.com", "22222222222", 5000),
        ("Carlos", "Souza", "carlos@example.com", "33333333333", 6000),
    ]

    for first_name, last_name, email, document, salary in employees:
        create_custom_employee(
            client,
            admin_headers,
            department["id"],
            first_name=first_name,
            last_name=last_name,
            email=email,
            document=document,
            salary=salary,
        )

    response = client.get(
        "/api/v1/employees?skip=0&limit=2",
        headers=viewer_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_employees_pagination_skip(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    employees = [
        ("Ana", "Costa", "ana@example.com", "11111111111", 4000),
        ("Bruno", "Lima", "bruno@example.com", "22222222222", 5000),
        ("Carlos", "Souza", "carlos@example.com", "33333333333", 6000),
    ]

    for first_name, last_name, email, document, salary in employees:
        create_custom_employee(
            client,
            admin_headers,
            department["id"],
            first_name=first_name,
            last_name=last_name,
            email=email,
            document=document,
            salary=salary,
        )

    response = client.get(
        "/api/v1/employees"
        "?skip=1&limit=2&sort_by=first_name&order=asc",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    names = [
        employee["first_name"]
        for employee in response.json()
    ]

    assert names == [
        "Bruno",
        "Carlos",
    ]


def test_employees_filter_by_first_name(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    create_custom_employee(
        client,
        admin_headers,
        department["id"],
        first_name="Maria",
        last_name="Souza",
        email="maria@example.com",
        document="11111111111",
        salary=4500,
    )

    create_custom_employee(
        client,
        admin_headers,
        department["id"],
        first_name="Carlos",
        last_name="Silva",
        email="carlos@example.com",
        document="22222222222",
        salary=5000,
    )

    response = client.get(
        "/api/v1/employees?first_name=mar",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    employees = response.json()

    assert len(employees) == 1
    assert employees[0]["first_name"] == "Maria"


def test_employees_filter_by_department(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    technology = create_department(
        client,
        admin_headers,
    )

    finance_response = client.post(
        "/api/v1/departments",
        headers=admin_headers,
        json={
            "name": "Financeiro",
            "description": "Departamento financeiro",
        },
    )

    assert finance_response.status_code == 201
    finance = finance_response.json()

    create_custom_employee(
        client,
        admin_headers,
        technology["id"],
        first_name="Carlos",
        last_name="Silva",
        email="carlos@example.com",
        document="11111111111",
        salary=5000,
    )

    create_custom_employee(
        client,
        admin_headers,
        finance["id"],
        first_name="Maria",
        last_name="Souza",
        email="maria@example.com",
        document="22222222222",
        salary=4500,
    )

    response = client.get(
        f"/api/v1/employees?department_id={finance['id']}",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    employees = response.json()

    assert len(employees) == 1
    assert employees[0]["department_id"] == finance["id"]


def test_employees_filter_by_active_status(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    create_custom_employee(
        client,
        admin_headers,
        department["id"],
        first_name="Ativo",
        last_name="Teste",
        email="ativo@example.com",
        document="11111111111",
        salary=4000,
    )

    create_custom_employee(
        client,
        admin_headers,
        department["id"],
        first_name="Inativo",
        last_name="Teste",
        email="inativo@example.com",
        document="22222222222",
        salary=4500,
        is_active=False,
    )

    response = client.get(
        "/api/v1/employees?is_active=false",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    employees = response.json()

    assert len(employees) == 1
    assert employees[0]["is_active"] is False


def test_employees_sort_by_salary_descending(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    create_custom_employee(
        client,
        admin_headers,
        department["id"],
        first_name="Maria",
        last_name="Souza",
        email="maria@example.com",
        document="11111111111",
        salary=4500,
    )

    create_custom_employee(
        client,
        admin_headers,
        department["id"],
        first_name="Carlos",
        last_name="Silva",
        email="carlos@example.com",
        document="22222222222",
        salary=6000,
    )

    response = client.get(
        "/api/v1/employees?sort_by=salary&order=desc",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    salaries = [
        float(employee["salary"])
        for employee in response.json()
    ]

    assert salaries == [
        6000.00,
        4500.00,
    ]


def test_employees_reject_invalid_limit(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/employees?limit=500",
        headers=viewer_headers,
    )

    assert response.status_code == 422


def test_employees_reject_invalid_sort_field(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/employees?sort_by=invalid_field",
        headers=viewer_headers,
    )

    assert response.status_code == 422