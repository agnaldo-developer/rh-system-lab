from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.core.dependencies import get_current_user, require_roles
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
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
    "",
    response_model=list[EmployeeResponse],
    dependencies=[
        Depends(get_current_user),
    ],
)
def list_employees(
    db: DatabaseSession,
) -> list[Employee]:
    statement = select(Employee).order_by(
        Employee.first_name,
        Employee.last_name,
    )

    employees = db.scalars(statement).all()

    return list(employees)


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


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
    dependencies=[
        Depends(require_roles("admin", "rh")),
    ]
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