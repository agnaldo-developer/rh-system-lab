from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Tecnologia"],
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        examples=["Departamento responsável por infraestrutura e sistemas"],
    )


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
