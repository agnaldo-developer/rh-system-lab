from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentResponse


router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


DatabaseSession = Annotated[Session, Depends(get_db)]


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
