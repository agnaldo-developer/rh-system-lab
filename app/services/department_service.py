from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
)


DepartmentSortField = Literal[
    "id",
    "name",
    "created_at",
    "updated_at",
]

SortOrder = Literal["asc", "desc"]


def get_department_by_id(
    db: Session,
    department_id: int,
) -> Department | None:
    return db.get(Department, department_id)


def get_department_or_404(
    db: Session,
    department_id: int,
) -> Department:
    department = get_department_by_id(
        db=db,
        department_id=department_id,
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )

    return department


def list_departments(
    db: Session,
    *,
    skip: int,
    limit: int,
    name: str | None,
    sort_by: DepartmentSortField,
    order: SortOrder,
) -> list[Department]:
    statement = select(Department)

    if name is not None:
        statement = statement.where(
            Department.name.ilike(f"%{name}%")
        )

    sort_columns = {
        "id": Department.id,
        "name": Department.name,
        "created_at": Department.created_at,
        "updated_at": Department.updated_at,
    }

    sort_column = sort_columns[sort_by]

    if order == "desc":
        statement = statement.order_by(desc(sort_column))
    else:
        statement = statement.order_by(asc(sort_column))

    statement = statement.offset(skip).limit(limit)

    departments = db.scalars(statement).all()

    return list(departments)


def create_department(
    db: Session,
    department_data: DepartmentCreate,
) -> Department:
    department = Department(
        name=department_data.name,
        description=department_data.description,
    )

    db.add(department)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A department with this name already exists.",
        ) from exc

    db.refresh(department)

    return department


def update_department(
    db: Session,
    department: Department,
    department_data: DepartmentUpdate,
) -> Department:
    update_data = department_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(department, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A department with this name already exists.",
        ) from exc

    db.refresh(department)

    return department


def delete_department(
    db: Session,
    department: Department,
) -> None:
    db.delete(department)
    db.commit()
