from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import asc, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
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
    dependencies=[
    Depends(require_roles("admin", "rh")),
],
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
    return get_department_or_404(department_id, db)


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
    dependencies=[
    Depends(require_roles("admin", "rh")),
],
)
def delete_department(
    department_id: int,
    db: DatabaseSession,
) -> Response:
    department = get_department_or_404(department_id, db)

    db.delete(department)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)