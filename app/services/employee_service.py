from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


EmployeeSortField = Literal[
    "id",
    "first_name",
    "last_name",
    "email",
    "hire_date",
    "salary",
    "created_at",
    "updated_at",
]

SortOrder = Literal["asc", "desc"]


def get_employee_by_id(
    db: Session,
    employee_id: int,
) -> Employee | None:
    return db.get(Employee, employee_id)


def get_employee_or_404(
    db: Session,
    employee_id: int,
) -> Employee:
    employee = get_employee_by_id(
        db=db,
        employee_id=employee_id,
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return employee


def validate_department(
    db: Session,
    department_id: int,
) -> None:
    department = db.get(Department, department_id)

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )


def list_employees(
    db: Session,
    *,
    skip: int,
    limit: int,
    first_name: str | None,
    last_name: str | None,
    email: str | None,
    department_id: int | None,
    is_active: bool | None,
    sort_by: EmployeeSortField,
    order: SortOrder,
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
        statement = statement.order_by(
            desc(sort_column)
        )
    else:
        statement = statement.order_by(
            asc(sort_column)
        )

    statement = statement.offset(skip).limit(limit)

    employees = db.scalars(statement).all()

    return list(employees)


def create_employee(
    db: Session,
    employee_data: EmployeeCreate,
    *,
    commit: bool = True,
) -> Employee:
    validate_department(
        db=db,
        department_id=employee_data.department_id,
    )

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
        if commit:
            db.commit()
            db.refresh(employee)
        else:
            db.flush()

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An employee with this email or document "
                "already exists."
            ),
        ) from exc

    return employee


def update_employee(
    db: Session,
    employee: Employee,
    employee_data: EmployeeUpdate,
    *,
    commit: bool = True,
) -> Employee:
    update_data = employee_data.model_dump(
        exclude_unset=True,
    )

    if "department_id" in update_data:
        validate_department(
            db=db,
            department_id=update_data["department_id"],
        )

    for field, value in update_data.items():
        setattr(employee, field, value)

    try:
        if commit:
            db.commit()
            db.refresh(employee)
        else:
            db.flush()

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An employee with this email or document "
                "already exists."
            ),
        ) from exc

    return employee


def delete_employee(
    db: Session,
    employee: Employee,
    *,
    commit: bool = True,
) -> None:
    db.delete(employee)

    if commit:
        db.commit()
    else:
        db.flush()