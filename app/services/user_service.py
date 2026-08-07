from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    statement = select(User).where(
        User.email == email
    )

    return db.scalar(statement)


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    return db.get(User, user_id)


def list_users(
    db: Session,
) -> list[User]:
    statement = select(User).order_by(
        User.name
    )

    users = db.scalars(statement).all()

    return list(users)


def create_user(
    db: Session,
    user_data: UserCreate,
    *,
    commit: bool = True,
) -> User:
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        role=user_data.role,
        is_active=user_data.is_active,
    )

    db.add(user)

    if commit:
        db.commit()
        db.refresh(user)
    else:
        db.flush()

    return user


def update_user(
    db: Session,
    user: User,
    user_data: UserUpdate,
    *,
    commit: bool = True,
) -> User:
    update_data = user_data.model_dump(
        exclude_unset=True,
    )

    password = update_data.pop(
        "password",
        None,
    )

    if password is not None:
        user.password_hash = hash_password(
            password
        )

    for field, value in update_data.items():
        setattr(user, field, value)

    if commit:
        db.commit()
        db.refresh(user)
    else:
        db.flush()

    return user


def deactivate_user(
    db: Session,
    user: User,
    *,
    commit: bool = True,
) -> User:
    user.is_active = False

    if commit:
        db.commit()
        db.refresh(user)
    else:
        db.flush()

    return user