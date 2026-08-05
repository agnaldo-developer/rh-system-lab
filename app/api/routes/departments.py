from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)


router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


DatabaseSession = Annotated[Session, Depends(get_db)]


def get_department_or_404(
    department_id: int,
    db: Session,
) -> Department:
    department = db.get(Department, department_id)

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )

    return department


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    department_data: DepartmentCreate,
    db: DatabaseSession,
) -> Department:
    department = Department(
        name=department_data.name,
        description=department_data.description,
    )

    db.add(department)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A department with this name already exists.",
        )

    db.refresh(department)

    return department


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
def list_departments(
    db: DatabaseSession,
) -> list[Department]:
    statement = select(Department).order_by(Department.name)

    departments = db.scalars(statement).all()

    return list(departments)


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: int,
    db: DatabaseSession,
) -> Department:
    return get_department_or_404(department_id, db)


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: DatabaseSession,
) -> Department:
    department = get_department_or_404(department_id, db)

    update_data = department_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(department, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A department with this name already exists.",
        )

    db.refresh(department)

    return department


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_department(
    department_id: int,
    db: DatabaseSession,
) -> Response:
    department = get_department_or_404(department_id, db)

    db.delete(department)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)