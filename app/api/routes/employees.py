from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    Response,
    status,
)
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.audit_service import create_audit_log
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
    summary="Create employee",
    description="""
Creates a new employee associated with an existing department.

Allowed roles:

- `admin`
- `rh`
""",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Employee created successfully.",
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
            "description": "Employee email or document already exists.",
        },
        422: {
            "description": "Validation error.",
        },
    },
)
def create_employee(
    request: Request,
    employee_data: EmployeeCreate,
    db: DatabaseSession,
    current_user: User = Depends(
        require_roles("admin", "rh")
    ),
) -> Employee:
    try:
        employee = create_employee_service(
            db=db,
            employee_data=employee_data,
            commit=False,
        )

        create_audit_log(
            db,
            user_id=current_user.id,
            action="CREATE",
            entity_type="employee",
            entity_id=employee.id,
            request_id=getattr(
                request.state,
                "request_id",
                None,
            ),
            details={
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "email": employee.email,
                "document": employee.document,
                "department_id": employee.department_id,
                "hire_date": employee.hire_date,
                "salary": employee.salary,
            },
            commit=False,
        )

        db.commit()
        db.refresh(employee)

        return employee

    except Exception:
        db.rollback()
        raise
@router.get(
    "",
    summary="List employees",
    description="""
Returns a paginated list of employees.

Supports filtering by:

- first name;
- last name;
- email;
- department;
- active status.

Also supports custom sorting.
""",
    response_model=list[EmployeeResponse],
    responses={
        200: {
            "description": "Employees returned successfully.",
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
    summary="Get employee by ID",
    description="Returns an employee using its unique identifier.",
    response_model=EmployeeResponse,
    responses={
        200: {
            "description": "Employee returned successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        404: {
            "description": "Employee not found.",
        },
    },
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
    summary="Update employee",
    description="""
Partially updates an employee.

Allowed roles:

- `admin`
- `rh`
""",
    response_model=EmployeeResponse,
    responses={
        200: {
            "description": "Employee updated successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
        404: {
            "description": "Employee or department not found.",
        },
        409: {
            "description": "Employee email or document already exists.",
        },
        422: {
            "description": "Validation error.",
        },
    },
)
def update_employee(
    request: Request,
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: DatabaseSession,
    current_user: User = Depends(
        require_roles("admin", "rh")
    ),
) -> Employee:
    employee = get_employee_or_404(
        db=db,
        employee_id=employee_id,
    )

    update_data = employee_data.model_dump(
        exclude_unset=True,
    )

    previous_values = {
        field: getattr(employee, field)
        for field in update_data
    }

    try:
        employee = update_employee_service(
            db=db,
            employee=employee,
            employee_data=employee_data,
            commit=False,
        )

        create_audit_log(
            db,
            user_id=current_user.id,
            action="UPDATE",
            entity_type="employee",
            entity_id=employee.id,
            request_id=getattr(
                request.state,
                "request_id",
                None,
            ),
            details={
                "changed_fields": list(update_data.keys()),
                "previous_values": previous_values,
                "new_values": update_data,
            },
            commit=False,
        )

        db.commit()
        db.refresh(employee)

        return employee

    except Exception:
        db.rollback()
        raise
@router.delete(
    "/{employee_id}",
    summary="Delete employee",
    description="""
Permanently deletes an employee.

Allowed roles:

- `admin`
- `rh`
""",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {
            "description": "Employee deleted successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
        404: {
            "description": "Employee not found.",
        },
    },
)
def delete_employee(
    request: Request,
    employee_id: int,
    db: DatabaseSession,
    current_user: User = Depends(
        require_roles("admin", "rh")
    ),
) -> Response:
    employee = get_employee_or_404(
        db=db,
        employee_id=employee_id,
    )

    deleted_employee = {
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "document": employee.document,
        "department_id": employee.department_id,
    }

    try:
        delete_employee_service(
            db=db,
            employee=employee,
            commit=False,
        )

        create_audit_log(
            db,
            user_id=current_user.id,
            action="DELETE",
            entity_type="employee",
            entity_id=employee_id,
            request_id=getattr(
                request.state,
                "request_id",
                None,
            ),
            details=deleted_employee,
            commit=False,
        )

        db.commit()

        return Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )

    except Exception:
        db.rollback()
        raise