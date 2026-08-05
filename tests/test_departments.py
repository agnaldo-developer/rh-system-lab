from fastapi.testclient import TestClient


def create_department(
    client: TestClient,
    admin_headers: dict[str, str],
    name: str = "Tecnologia",
) -> dict:
    response = client.post(
        "/api/v1/departments",
        headers=admin_headers,
        json={
            "name": name,
            "description": "Departamento de tecnologia",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_department(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    assert department["id"] > 0
    assert department["name"] == "Tecnologia"
    assert department["description"] == (
        "Departamento de tecnologia"
    )


def test_list_departments(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    create_department(
        client,
        admin_headers,
    )

    response = client.get(
        "/api/v1/departments",
        headers=viewer_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_department_by_id(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    response = client.get(
        f"/api/v1/departments/{department['id']}",
        headers=viewer_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Tecnologia"


def test_update_department(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    response = client.patch(
        f"/api/v1/departments/{department['id']}",
        headers=admin_headers,
        json={
            "description": "Infraestrutura, cloud e sistemas",
        },
    )

    assert response.status_code == 200
    assert response.json()["description"] == (
        "Infraestrutura, cloud e sistemas"
    )


def test_delete_department(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    department = create_department(
        client,
        admin_headers,
    )

    response = client.delete(
        f"/api/v1/departments/{department['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/departments/{department['id']}",
        headers=viewer_headers,
    )

    assert get_response.status_code == 404


def test_duplicate_department_returns_conflict(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    create_department(
        client,
        admin_headers,
    )

    response = client.post(
        "/api/v1/departments",
        headers=admin_headers,
        json={
            "name": "Tecnologia",
            "description": "Outro departamento",
        },
    )

    assert response.status_code == 409


def test_department_not_found(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/departments/999",
        headers=viewer_headers,
    )

    assert response.status_code == 404


def test_departments_require_authentication(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/departments")

    assert response.status_code == 401


def test_viewer_cannot_create_department(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/departments",
        headers=viewer_headers,
        json={
            "name": "Financeiro",
            "description": "Departamento financeiro",
        },
    )

    assert response.status_code == 403


def test_rh_can_create_department(
    client: TestClient,
    rh_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/departments",
        headers=rh_headers,
        json={
            "name": "Recursos Humanos",
            "description": "Departamento de RH",
        },
    )

    assert response.status_code == 201