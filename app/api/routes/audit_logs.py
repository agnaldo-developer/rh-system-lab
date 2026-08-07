from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.schemas.audit_log import AuditLogRead
from app.services.audit_service import list_audit_logs


router = APIRouter(
    prefix="/api/v1/audit-logs",
    tags=["Audit Logs"],
)


DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    summary="List audit logs",
    description=(
        "Returns application audit records. "
        "This endpoint is restricted to administrators."
    ),
    response_model=list[AuditLogRead],
    dependencies=[
        Depends(require_roles("admin")),
    ],
    responses={
        200: {
            "description": "Audit logs returned successfully.",
        },
        401: {
            "description": "Authentication required.",
        },
        403: {
            "description": "Insufficient permissions.",
        },
        422: {
            "description": "Invalid query parameter.",
        },
    },
)
def read_audit_logs(
    db: DatabaseSession,
    skip: Annotated[
        int,
        Query(
            ge=0,
            description="Quantidade de registros ignorados.",
        ),
    ] = 0,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Quantidade máxima de registros retornados.",
        ),
    ] = 50,
    user_id: Annotated[
        int | None,
        Query(
            gt=0,
            description="Filtra pelo usuário responsável.",
        ),
    ] = None,
    action: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=30,
            description="Filtra pelo tipo da ação.",
        ),
    ] = None,
    entity_type: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=50,
            description="Filtra pelo tipo da entidade.",
        ),
    ] = None,
) -> list[AuditLogRead]:
    return list_audit_logs(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
    )
