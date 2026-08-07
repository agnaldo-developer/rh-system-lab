from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    verify_password,
)
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.audit_service import create_audit_log
from app.services.user_service import get_user_by_email


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


def get_request_context(
    request: Request,
) -> tuple[str | None, str | None]:
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    client_ip = (
        request.client.host
        if request.client is not None
        else None
    )

    return request_id, client_ip


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
    request: Request,
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    request_id, client_ip = get_request_context(
        request
    )

    user = get_user_by_email(
        db=db,
        email=credentials.email,
    )

    if user is None:
        create_audit_log(
            db,
            user_id=None,
            action="LOGIN_FAILED",
            entity_type="authentication",
            entity_id=None,
            request_id=request_id,
            details={
                "email": str(credentials.email),
                "client_ip": client_ip,
                "reason": "invalid_credentials",
            },
            commit=True,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(
        credentials.password,
        user.password_hash,
    ):
        create_audit_log(
            db,
            user_id=user.id,
            action="LOGIN_FAILED",
            entity_type="authentication",
            entity_id=user.id,
            request_id=request_id,
            details={
                "email": user.email,
                "client_ip": client_ip,
                "reason": "invalid_credentials",
            },
            commit=True,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        create_audit_log(
            db,
            user_id=user.id,
            action="LOGIN_FAILED",
            entity_type="authentication",
            entity_id=user.id,
            request_id=request_id,
            details={
                "email": user.email,
                "client_ip": client_ip,
                "reason": "inactive_user",
            },
            commit=True,
        )

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

    create_audit_log(
        db,
        user_id=user.id,
        action="LOGIN_SUCCESS",
        entity_type="authentication",
        entity_id=user.id,
        request_id=request_id,
        details={
            "email": user.email,
            "client_ip": client_ip,
            "role": user.role,
        },
        commit=True,
    )

    return TokenResponse(
        access_token=access_token,
    )