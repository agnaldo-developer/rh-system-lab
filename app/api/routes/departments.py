from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_roles,
)
from app.models.department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department_service import (
    create_department as create_department_service,
)
from app.services.department_service import (
    delete_department as delete_department_service,
)
from app.services.department_service import (
    get_department_or_404,
)
from app.services.department_service import (
    list_departments as list_departments_service,
)
from app.services.department_service import (
    update_department as update_department_service,
)


router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    summary="Create department",
    description="""
Creates a new department.

Allowed roles:

- `admin`
- `rh`
""",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Department created successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
        409: {
            "description": "A department with this name already exists.",
        },
        422: {
            "description": "Validation error.",
        },
    },
    dependencies=[
        Depends(require_roles("admin", "rh")),
    ],
)
def create_department(
    department_data: DepartmentCreate,
    db: DatabaseSession,
) -> Department:
    return create_department_service(
        db=db,
        department_data=department_data,
    )


@router.get(
    "",
    summary="List departments",
    description="""
Returns a paginated list of departments.

Supports:

- pagination using `skip` and `limit`;
- partial filtering by name;
- ascending or descending sorting.
""",
    response_model=list[DepartmentResponse],
    responses={
        200: {
            "description": "Departments returned successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        422: {
            "description": "Invalid query parameter.",
        },
    },
    dependencies=[
        Depends(get_current_user),
    ],
)
def list_departments(
    db: DatabaseSession,
    skip: Annotated[
        int,
        Query(
            ge=0,
            description="Quantidade de registros ignorados.",
        ),
    ] = 0,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Quantidade máxima de registros retornados.",
        ),
    ] = 20,
    name: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
            description="Filtro parcial pelo nome do departamento.",
        ),
    ] = None,
    sort_by: Annotated[
        Literal["id", "name", "created_at", "updated_at"],
        Query(
            description="Campo utilizado na ordenação.",
        ),
    ] = "name",
    order: Annotated[
        Literal["asc", "desc"],
        Query(
            description="Direção da ordenação.",
        ),
    ] = "asc",
) -> list[Department]:
    return list_departments_service(
        db=db,
        skip=skip,
        limit=limit,
        name=name,
        sort_by=sort_by,
        order=order,
    )


@router.get(
    "/{department_id}",
    summary="Get department by ID",
    description="Returns a department using its unique identifier.",
    response_model=DepartmentResponse,
    responses={
        200: {
            "description": "Department returned successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        404: {
            "description": "Department not found.",
        },
    },
    dependencies=[
        Depends(get_current_user),
    ],
)
def get_department(
    department_id: int,
    db: DatabaseSession,
) -> Department:
    return get_department_or_404(
        db=db,
        department_id=department_id,
    )


@router.patch(
    "/{department_id}",
    summary="Update department",
    description="""
Partially updates a department.

Allowed roles:

- `admin`
- `rh`
""",
    response_model=DepartmentResponse,
    responses={
        200: {
            "description": "Department updated successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
        404: {
            "description": "Department not found.",
        },
        409: {
            "description": "A department with this name already exists.",
        },
        422: {
            "description": "Validation error.",
        },
    },
    dependencies=[
        Depends(require_roles("admin", "rh")),
    ],
)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: DatabaseSession,
) -> Department:
    department = get_department_or_404(
        db=db,
        department_id=department_id,
    )

    return update_department_service(
        db=db,
        department=department,
        department_data=department_data,
    )


@router.delete(
    "/{department_id}",
    summary="Delete department",
    description="""
Permanently deletes a department.

Allowed roles:

- `admin`
- `rh`
""",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {
            "description": "Department deleted successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
        404: {
            "description": "Department not found.",
        },
    },
    dependencies=[
        Depends(require_roles("admin", "rh")),
    ],
)
def delete_department(
    department_id: int,
    db: DatabaseSession,
) -> Response:
    department = get_department_or_404(
        db=db,
        department_id=department_id,
    )

    delete_department_service(
        db=db,
        department=department,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )