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
def test_departments_pagination_limit(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    for name in [
        "Tecnologia",
        "Financeiro",
        "Compras",
    ]:
        create_department(
            client,
            admin_headers,
            name=name,
        )

    response = client.get(
        "/api/v1/departments?skip=0&limit=2",
        headers=viewer_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_departments_pagination_skip(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    for name in [
        "Compras",
        "Financeiro",
        "Tecnologia",
    ]:
        create_department(
            client,
            admin_headers,
            name=name,
        )

    response = client.get(
        "/api/v1/departments"
        "?skip=1&limit=2&sort_by=name&order=asc",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    names = [
        department["name"]
        for department in response.json()
    ]

    assert names == [
        "Financeiro",
        "Tecnologia",
    ]


def test_departments_filter_by_name(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    create_department(
        client,
        admin_headers,
        name="Tecnologia",
    )
    create_department(
        client,
        admin_headers,
        name="Financeiro",
    )

    response = client.get(
        "/api/v1/departments?name=tec",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    departments = response.json()

    assert len(departments) == 1
    assert departments[0]["name"] == "Tecnologia"


def test_departments_sort_descending(
    client: TestClient,
    admin_headers: dict[str, str],
    viewer_headers: dict[str, str],
) -> None:
    for name in [
        "Compras",
        "Financeiro",
        "Tecnologia",
    ]:
        create_department(
            client,
            admin_headers,
            name=name,
        )

    response = client.get(
        "/api/v1/departments"
        "?sort_by=name&order=desc",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    names = [
        department["name"]
        for department in response.json()
    ]

    assert names == [
        "Tecnologia",
        "Financeiro",
        "Compras",
    ]


def test_departments_reject_invalid_limit(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/departments?limit=500",
        headers=viewer_headers,
    )

    assert response.status_code == 422


def test_departments_reject_invalid_sort_field(
    client: TestClient,
    viewer_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/departments?sort_by=invalid_field",
        headers=viewer_headers,
    )

    assert response.status_code == 422