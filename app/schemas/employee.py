from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeBase(BaseModel):
    first_name: str = Field(
        min_length=2,
        max_length=100,
        examples=["João"],
    )

    last_name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Silva"],
    )

    email: EmailStr = Field(
        examples=["joao.silva@empresa.com"],
    )

    phone: str | None = Field(
        default=None,
        min_length=8,
        max_length=20,
        examples=["11999999999"],
    )

    document: str = Field(
        min_length=5,
        max_length=20,
        examples=["12345678900"],
    )

    hire_date: date = Field(
        examples=["2026-08-05"],
    )

    salary: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=[5000.00],
    )

    department_id: int = Field(
        gt=0,
        examples=[1],
    )


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        min_length=8,
        max_length=20,
    )

    document: str | None = Field(
        default=None,
        min_length=5,
        max_length=20,
    )

    hire_date: date | None = None

    salary: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    department_id: int | None = Field(
        default=None,
        gt=0,
    )

    is_active: bool | None = None


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime