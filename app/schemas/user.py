from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=150,
    )

    email: EmailStr

    role: str = Field(
        default="viewer",
        pattern="^(admin|rh|viewer)$",
    )

    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    email: EmailStr | None = None

    role: str | None = Field(
        default=None,
        pattern="^(admin|rh|viewer)$",
    )

    is_active: bool | None = None

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
