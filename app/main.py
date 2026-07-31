from collections.abc import Generator

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Department, Employee
from app.schemas import (
    DepartmentCreate,
    DepartmentResponse,
    EmployeeCreate,
    EmployeeResponse,
)

app = FastAPI(
    title="RH System API",
    version="1.0.0",
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "RH System API funcionando",
        "environment": "Docker Compose",
    }


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }


@app.get(
    "/departments",
    response_model=list[DepartmentResponse],
)
def list_departments(
    db: Session = Depends(get_db),
) -> list[Department]:
    statement = select(Department).order_by(Department.id)

    return list(db.scalars(statement).all())


@app.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
) -> Department:
    department = Department(name=payload.name.strip())

    if not department.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department name cannot be empty",
        )

    db.add(department)

    try:
        db.commit()
        db.refresh(department)
        return department

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department already exists",
        )

@app.get(
    "/employees",
    response_model=list[EmployeeResponse],
)
def list_employees(
    db: Session = Depends(get_db),
) -> list[Employee]:
    statement = select(Employee).order_by(Employee.id)

    return list(db.scalars(statement).all())


@app.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
) -> Employee:
    employee = Employee(
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        department_id=payload.department_id,
    )

    if not employee.name or not employee.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name and email are required",
        )

    db.add(employee)

    try:
        db.commit()
        db.refresh(employee)
        return employee

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee email already exists",
        )
