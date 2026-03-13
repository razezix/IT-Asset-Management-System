from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin, require_tech_or_admin
from app.models.audit import AuditActionType
from app.schemas.audit import AuditLogOut, AuthLogOut, AuditFilterParams
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/actions", response_model=list[AuditLogOut], dependencies=[Depends(require_tech_or_admin)])
async def list_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    action_type: Optional[AuditActionType] = Query(None),
    entity_type: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
):
    params = AuditFilterParams(action_type=action_type, entity_type=entity_type, user_id=user_id, page=page, size=size)
    return await AuditService(db).list_logs(params)


@router.get("/auth", response_model=list[AuthLogOut], dependencies=[Depends(require_admin)])
async def list_auth_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
):
    return await AuditService(db).list_auth_logs(user_id=user_id, page=page, size=size)
