from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user_service import get_user_by_email


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    summary="Authenticate user",
    description="""
Authenticates a user using email and password.

Returns a JWT access token that must be sent in the Authorization header.

Example:

Authorization: Bearer <access_token>
""",
    response_model=TokenResponse,
    responses={
        200: {
            "description": "Authentication successful.",
        },
        401: {
            "description": "Invalid email or password.",
        },
        403: {
            "description": "Inactive user.",
        },
        422: {
            "description": "Validation error.",
        },
    },
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = get_user_by_email(
        db=db,
        email=credentials.email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(
        credentials.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )

    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={
            "email": user.email,
            "role": user.role,
        },
    )

    return TokenResponse(
        access_token=access_token,
    )
