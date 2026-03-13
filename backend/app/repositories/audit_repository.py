from typing import Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditLog, AuthLog, AuditActionType


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_audit_log(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        return log

    async def create_auth_log(self, log: AuthLog) -> AuthLog:
        self.db.add(log)
        return log

    async def list_audit_logs(
        self,
        action_type: Optional[AuditActionType] = None,
        entity_type: Optional[str] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 50,
    ) -> list[AuditLog]:
        query = (
            select(AuditLog)
            .options(selectinload(AuditLog.user))
            .order_by(desc(AuditLog.created_at))
        )
        if action_type:
            query = query.where(AuditLog.action_type == action_type)
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)

        offset = (page - 1) * size
        result = await self.db.execute(query.offset(offset).limit(size))
        return list(result.scalars().all())

    async def list_auth_logs(
        self,
        user_id: Optional[int] = None,
        page: int = 1,
        size: int = 50,
    ) -> list[AuthLog]:
        query = select(AuthLog).order_by(desc(AuthLog.created_at))
        if user_id:
            query = query.where(AuthLog.user_id == user_id)
        offset = (page - 1) * size
        result = await self.db.execute(query.offset(offset).limit(size))
        return list(result.scalars().all())
