from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import asc, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.department import Department
from app.models.employee import Employee
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


DatabaseSession = Annotated[Session, Depends(get_db)]


def get_employee_or_404(
    employee_id: int,
    db: Session,
) -> Employee:
    employee = db.get(Employee, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return employee


def validate_department(
    department_id: int,
    db: Session,
) -> None:
    department = db.get(Department, department_id)

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )


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
    validate_department(employee_data.department_id, db)

    employee = Employee(
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        email=employee_data.email,
        phone=employee_data.phone,
        document=employee_data.document,
        hire_date=employee_data.hire_date,
        salary=employee_data.salary,
        department_id=employee_data.department_id,
    )

    db.add(employee)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this email or document already exists.",
        )

    db.refresh(employee)

    return employee



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
    return get_employee_or_404(employee_id, db)
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
    statement = select(Employee)

    if first_name is not None:
        statement = statement.where(
            Employee.first_name.ilike(f"%{first_name}%")
        )

    if last_name is not None:
        statement = statement.where(
            Employee.last_name.ilike(f"%{last_name}%")
        )

    if email is not None:
        statement = statement.where(
            Employee.email.ilike(f"%{email}%")
        )

    if department_id is not None:
        statement = statement.where(
            Employee.department_id == department_id
        )

    if is_active is not None:
        statement = statement.where(
            Employee.is_active == is_active
        )

    sort_columns = {
        "id": Employee.id,
        "first_name": Employee.first_name,
        "last_name": Employee.last_name,
        "email": Employee.email,
        "hire_date": Employee.hire_date,
        "salary": Employee.salary,
        "created_at": Employee.created_at,
        "updated_at": Employee.updated_at,
    }

    sort_column = sort_columns[sort_by]

    if order == "desc":
        statement = statement.order_by(desc(sort_column))
    else:
        statement = statement.order_by(asc(sort_column))

    statement = statement.offset(skip).limit(limit)

    employees = db.scalars(statement).all()

    return list(employees)

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
    employee = get_employee_or_404(employee_id, db)

    update_data = employee_data.model_dump(exclude_unset=True)

    if "department_id" in update_data:
        validate_department(update_data["department_id"], db)

    for field, value in update_data.items():
        setattr(employee, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this email or document already exists.",
        )

    db.refresh(employee)

    return employee


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
    employee = get_employee_or_404(employee_id, db)

    db.delete(employee)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)