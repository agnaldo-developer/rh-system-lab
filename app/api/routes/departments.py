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
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
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
    response_model=list[DepartmentResponse],
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
    response_model=DepartmentResponse,
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
    response_model=DepartmentResponse,
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
    status_code=status.HTTP_204_NO_CONTENT,
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