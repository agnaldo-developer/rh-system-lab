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
from app.models.employee import Employee
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services.employee_service import (
    create_employee as create_employee_service,
)
from app.services.employee_service import (
    delete_employee as delete_employee_service,
)
from app.services.employee_service import get_employee_or_404
from app.services.employee_service import (
    list_employees as list_employees_service,
)
from app.services.employee_service import (
    update_employee as update_employee_service,
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_roles("admin", "rh")),
    ],
)
def create_employee(
    employee_data: EmployeeCreate,
    db: DatabaseSession,
) -> Employee:
    return create_employee_service(
        db=db,
        employee_data=employee_data,
    )


@router.get(
    "",
    response_model=list[EmployeeResponse],
    dependencies=[
        Depends(get_current_user),
    ],
)
def list_employees(
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
    first_name: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
            description="Filtro parcial pelo primeiro nome.",
        ),
    ] = None,
    last_name: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
            description="Filtro parcial pelo sobrenome.",
        ),
    ] = None,
    email: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=255,
            description="Filtro parcial pelo e-mail.",
        ),
    ] = None,
    department_id: Annotated[
        int | None,
        Query(
            gt=0,
            description="Filtro pelo departamento.",
        ),
    ] = None,
    is_active: Annotated[
        bool | None,
        Query(
            description="Filtro pelo status do funcionário.",
        ),
    ] = None,
    sort_by: Annotated[
        Literal[
            "id",
            "first_name",
            "last_name",
            "email",
            "hire_date",
            "salary",
            "created_at",
            "updated_at",
        ],
        Query(
            description="Campo utilizado na ordenação.",
        ),
    ] = "first_name",
    order: Annotated[
        Literal["asc", "desc"],
        Query(
            description="Direção da ordenação.",
        ),
    ] = "asc",
) -> list[Employee]:
    return list_employees_service(
        db=db,
        skip=skip,
        limit=limit,
        first_name=first_name,
        last_name=last_name,
        email=email,
        department_id=department_id,
        is_active=is_active,
        sort_by=sort_by,
        order=order,
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    dependencies=[
        Depends(get_current_user),
    ],
)
def get_employee(
    employee_id: int,
    db: DatabaseSession,
) -> Employee:
    return get_employee_or_404(
        db=db,
        employee_id=employee_id,
    )


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
    dependencies=[
        Depends(require_roles("admin", "rh")),
    ],
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: DatabaseSession,
) -> Employee:
    employee = get_employee_or_404(
        db=db,
        employee_id=employee_id,
    )

    return update_employee_service(
        db=db,
        employee=employee,
        employee_data=employee_data,
    )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_roles("admin", "rh")),
    ],
)
def delete_employee(
    employee_id: int,
    db: DatabaseSession,
) -> Response:
    employee = get_employee_or_404(
        db=db,
        employee_id=employee_id,
    )

    delete_employee_service(
        db=db,
        employee=employee,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )