from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog, AuditActionType
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditLogOut, AuthLogOut, AuditFilterParams


class AuditService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditRepository(db)

    async def log(
        self,
        user_id: int,
        action_type: AuditActionType,
        entity_type: str,
        entity_id: str | None = None,
        entity_version_id: int | None = None,
        old_data: dict | None = None,
        new_data: dict | None = None,
        changed_fields: list | None = None,
        request: Request | None = None,
    ) -> None:
        await self.repo.create_audit_log(AuditLog(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_version_id=entity_version_id,
            old_data_json=old_data,
            new_data_json=new_data,
            changed_fields_json=changed_fields,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
        ))

    async def list_logs(self, params: AuditFilterParams) -> list[AuditLogOut]:
        logs = await self.repo.list_audit_logs(
            action_type=params.action_type,
            entity_type=params.entity_type,
            user_id=params.user_id,
            page=params.page,
            size=params.size,
        )
        return [
            AuditLogOut(
                **{k: v for k, v in log.__dict__.items() if not k.startswith("_")},
                username=log.user.username if log.user else None,
            )
            for log in logs
        ]

    async def list_auth_logs(self, user_id: int | None = None, page: int = 1, size: int = 50) -> list[AuthLogOut]:
        logs = await self.repo.list_auth_logs(user_id=user_id, page=page, size=size)
        return [AuthLogOut.model_validate(log) for log in logs]
