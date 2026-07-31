from pydantic import BaseModel, ConfigDict


class DepartmentCreate(BaseModel):
    name: str


class DepartmentResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class EmployeeCreate(BaseModel):
    name: str
    email: str
    department_id: int


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    department_id: int

    model_config = ConfigDict(from_attributes=True)
