from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from fastapi.encoders import jsonable_encoder

def create_audit_log(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | None,
    request_id: str | None,
    details: dict[str, Any] | None = None,
    commit: bool = False,
) -> AuditLog:
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        request_id=request_id,
        details=(
            jsonable_encoder(details)
            if details is not None
            else None
        ),
    )

    db.add(audit_log)

    if commit:
        db.commit()
        db.refresh(audit_log)

    return audit_log


def list_audit_logs(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
) -> list[AuditLog]:
    statement = select(AuditLog)

    if user_id is not None:
        statement = statement.where(
            AuditLog.user_id == user_id
        )

    if action is not None:
        statement = statement.where(
            AuditLog.action == action
        )

    if entity_type is not None:
        statement = statement.where(
            AuditLog.entity_type == entity_type
        )

    statement = (
        statement
        .order_by(desc(AuditLog.created_at))
        .offset(skip)
        .limit(limit)
    )

    audit_logs = db.scalars(statement).all()

    return list(audit_logs)
