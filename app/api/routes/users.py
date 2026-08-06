from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import (
    create_user,
    deactivate_user,
    get_user_by_email,
    get_user_by_id,
    list_users,
    update_user,
)


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)


def get_user_or_404(
    db: Session,
    user_id: int,
) -> User:
    user = get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


@router.get(
    "/me",
    summary="Get authenticated user",
    description=(
        "Returns the authenticated user's profile "
        "based on the JWT token."
    ),
    response_model=UserRead,
    responses={
        200: {
            "description": "Authenticated user returned successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Inactive user.",
        },
    },
)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


@router.get(
    "",
    summary="List users",
    description=(
        "Returns all registered users. "
        "This operation is restricted to administrators."
    ),
    response_model=list[UserRead],
    responses={
        200: {
            "description": "Users returned successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
    },
    dependencies=[
        Depends(require_roles("admin")),
    ],
)
def read_users(
    db: Session = Depends(get_db),
) -> list[User]:
    return list_users(db=db)


@router.post(
    "",
    summary="Create user",
    description=(
        "Creates a user with an application role. "
        "This operation is restricted to administrators."
    ),
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User created successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
        409: {
            "description": "A user with this email already exists.",
        },
        422: {
            "description": "Validation error.",
        },
    },
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles("admin")),
) -> User:
    existing_user = get_user_by_email(
        db=db,
        email=user_data.email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    return create_user(
        db=db,
        user_data=user_data,
    )


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description=(
        "Returns a user using its unique identifier. "
        "This operation is restricted to administrators."
    ),
    response_model=UserRead,
    responses={
        200: {
            "description": "User returned successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
        404: {
            "description": "User not found.",
        },
    },
    dependencies=[
        Depends(require_roles("admin")),
    ],
)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> User:
    return get_user_or_404(
        db=db,
        user_id=user_id,
    )


@router.patch(
    "/{user_id}",
    summary="Update user",
    description=(
        "Partially updates a user. "
        "This operation is restricted to administrators."
    ),
    response_model=UserRead,
    responses={
        200: {
            "description": "User updated successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
        404: {
            "description": "User not found.",
        },
        409: {
            "description": "A user with this email already exists.",
        },
        422: {
            "description": "Validation error.",
        },
    },
)
def edit_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles("admin")),
) -> User:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    if (
        user_data.email is not None
        and user_data.email != user.email
    ):
        existing_user = get_user_by_email(
            db=db,
            email=user_data.email,
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

    return update_user(
        db=db,
        user=user,
        user_data=user_data,
    )


@router.delete(
    "/{user_id}",
    summary="Deactivate user",
    description=(
        "Deactivates a user without permanently deleting its record. "
        "This operation is restricted to administrators."
    ),
    response_model=UserRead,
    responses={
        200: {
            "description": "User deactivated successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
        404: {
            "description": "User not found.",
        },
    },
)
def disable_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles("admin")),
) -> User:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    return deactivate_user(
        db=db,
        user=user,
    )