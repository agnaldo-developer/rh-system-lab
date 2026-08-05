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
    tags=["users"],
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
    response_model=UserRead,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> UserRead:
    return current_user

@router.get(
    "",
    response_model=list[UserRead],
    dependencies=[
        Depends(require_roles("admin")),
    ],
)
def read_users(
    db: Session = Depends(get_db),
) -> list[User]:
    return list_users(db=db)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> User:
    return get_user_or_404(
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

    return deactivate_user(
        db=db,
        user=user,
    )
@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> UserRead:
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
    response_model=UserRead,
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
@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[
        Depends(require_roles("admin")),
    ],
)
def edit_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
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
    response_model=UserRead,
    dependencies=[
        Depends(require_roles("admin")),
    ],
)
def disable_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> User:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    return deactivate_user(
        db=db,
        user=user,
    )