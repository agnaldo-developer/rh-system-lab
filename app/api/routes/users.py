from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_roles,
)
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.services.audit_service import (
    create_audit_log,
)
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
)
def read_current_user(
    current_user: User = Depends(
        get_current_user
    ),
) -> User:
    return current_user


@router.get(
    "",
    summary="List users",
    description=(
        "Returns all registered users. "
        "Restricted to administrators."
    ),
    response_model=list[UserRead],
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
        "Creates a new application user. "
        "Restricted to administrators."
    ),
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    ),
) -> User:
    existing_user = get_user_by_email(
        db=db,
        email=user_data.email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A user with this email "
                "already exists."
            ),
        )

    try:
        user = create_user(
            db=db,
            user_data=user_data,
            commit=False,
        )

        create_audit_log(
            db,
            user_id=current_user.id,
            action="CREATE",
            entity_type="user",
            entity_id=user.id,
            request_id=getattr(
                request.state,
                "request_id",
                None,
            ),
            details={
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            },
            commit=False,
        )

        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description=(
        "Returns a user by its unique identifier. "
        "Restricted to administrators."
    ),
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


@router.patch(
    "/{user_id}",
    summary="Update user",
    description=(
        "Partially updates a user. "
        "Restricted to administrators."
    ),
    response_model=UserRead,
)
def edit_user(
    request: Request,
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    ),
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
                detail=(
                    "A user with this email "
                    "already exists."
                ),
            )

    update_data = user_data.model_dump(
        exclude_unset=True,
    )

    password_changed = (
        "password" in update_data
    )

    safe_update_data = {
        key: value
        for key, value in update_data.items()
        if key != "password"
    }

    previous_values = {
        field: getattr(user, field)
        for field in safe_update_data
    }

    try:
        user = update_user(
            db=db,
            user=user,
            user_data=user_data,
            commit=False,
        )

        details = {
            "changed_fields": list(
                safe_update_data.keys()
            ),
            "previous_values": previous_values,
            "new_values": safe_update_data,
            "password_changed": password_changed,
        }

        create_audit_log(
            db,
            user_id=current_user.id,
            action="UPDATE",
            entity_type="user",
            entity_id=user.id,
            request_id=getattr(
                request.state,
                "request_id",
                None,
            ),
            details=details,
            commit=False,
        )

        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise


@router.delete(
    "/{user_id}",
    summary="Deactivate user",
    description=(
        "Deactivates a user without permanently "
        "deleting the record. "
        "Restricted to administrators."
    ),
    response_model=UserRead,
)
def disable_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    ),
) -> User:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    previous_status = user.is_active

    try:
        user = deactivate_user(
            db=db,
            user=user,
            commit=False,
        )

        create_audit_log(
            db,
            user_id=current_user.id,
            action="DEACTIVATE",
            entity_type="user",
            entity_id=user.id,
            request_id=getattr(
                request.state,
                "request_id",
                None,
            ),
            details={
                "email": user.email,
                "previous_is_active": (
                    previous_status
                ),
                "new_is_active": user.is_active,
            },
            commit=False,
        )

        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise