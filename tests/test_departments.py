from fastapi.testclient import TestClient


def create_department(
    client: TestClient,
    name: str = "Tecnologia",
) -> dict:
    response = client.post(
        "/api/v1/departments",
        json={
            "name": name,
            "description": "Departamento de tecnologia",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_department(client: TestClient) -> None:
    department = create_department(client)

    assert department["id"] > 0
    assert department["name"] == "Tecnologia"
    assert department["description"] == "Departamento de tecnologia"


def test_list_departments(client: TestClient) -> None:
    create_department(client)

    response = client.get("/api/v1/departments")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_department_by_id(client: TestClient) -> None:
    department = create_department(client)

    response = client.get(
        f"/api/v1/departments/{department['id']}"
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Tecnologia"


def test_update_department(client: TestClient) -> None:
    department = create_department(client)

    response = client.patch(
        f"/api/v1/departments/{department['id']}",
        json={
            "description": "Infraestrutura, cloud e sistemas",
        },
    )

    assert response.status_code == 200
    assert response.json()["description"] == (
        "Infraestrutura, cloud e sistemas"
    )


def test_delete_department(client: TestClient) -> None:
    department = create_department(client)

    response = client.delete(
        f"/api/v1/departments/{department['id']}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/departments/{department['id']}"
    )

    assert get_response.status_code == 404


def test_duplicate_department_returns_conflict(
    client: TestClient,
) -> None:
    create_department(client)

    response = client.post(
        "/api/v1/departments",
        json={
            "name": "Tecnologia",
            "description": "Outro departamento",
        },
    )

    assert response.status_code == 409


def test_department_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/departments/999")

    assert response.status_code == 404
