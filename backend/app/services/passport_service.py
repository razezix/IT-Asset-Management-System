from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.passport import PassportCard, PassportVersion, PassportStatus
from app.models.audit import AuditActionType
from app.repositories.passport_repository import PassportRepository
from app.schemas.passport import PassportVersionCreate, PassportCardOut, PassportVersionOut, PassportListItem
from app.services.versioning_service import VersioningService
from app.services.audit_service import AuditService
from app.utils.helpers import generate_passport_uid, compute_changed_fields


def _version_to_out(v: PassportVersion) -> PassportVersionOut:
    return PassportVersionOut.model_validate(v)


def _card_to_out(card: PassportCard, repo: PassportRepository) -> PassportCardOut:
    current = repo.get_current_version(card)
    return PassportCardOut(
        id=card.id,
        passport_uid=card.passport_uid,
        created_at=card.created_at,
        created_by=card.created_by,
        is_archived=card.is_archived,
        current_version=_version_to_out(current) if current else None,
    )


class PassportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PassportRepository(db)
        self.versioning = VersioningService(db)
        self.audit = AuditService(db)

    async def list_passports(
        self,
        search=None, department=None, device_type=None,
        is_archived=None, page=1, size=20,
    ) -> list[PassportListItem]:
        rows, _ = await self.repo.list_passports(search, department, device_type, is_archived, page, size)
        items = []
        for row in rows:
            card = row[0]
            items.append(PassportListItem(
                id=card.id,
                passport_uid=card.passport_uid,
                is_archived=card.is_archived,
                created_at=card.created_at,
                passport_number=row.passport_number,
                employee_fio=row.employee_fio,
                department=row.department,
                room=row.room,
                device_type=row.device_type,
                device_model=row.device_model,
                status=row.status,
                version_number=row.version_number,
            ))
        return items

    async def create_passport(self, body: PassportVersionCreate, user_id: int, request: Request) -> PassportCardOut:
        card = PassportCard(passport_uid=generate_passport_uid(), created_by=user_id)
        await self.repo.create_card(card)

        fields = body.model_dump(exclude={"device", "storage_devices", "monitors", "peripherals", "software_installations"})
        version = PassportVersion(passport_card_id=card.id, version_number=1, is_current=True, created_by=user_id, **fields)
        await self.repo.create_version(version)
        await self.versioning.attach_children(version, body)

        await self.audit.log(
            user_id, AuditActionType.create, "passport",
            entity_id=card.passport_uid, entity_version_id=version.id,
            new_data=body.model_dump(mode="json"), request=request,
        )

        refreshed = await self.repo.get_by_id(card.id)
        return _card_to_out(refreshed, self.repo)

    async def get_passport(self, passport_uid: str, user_id: int, request: Request) -> PassportCardOut:
        card = await self.repo.get_by_uid(passport_uid)
        if not card:
            raise HTTPException(status_code=404, detail="Passport not found")

        await self.audit.log(user_id, AuditActionType.view, "passport", entity_id=passport_uid, request=request)
        return _card_to_out(card, self.repo)

    async def get_versions(self, passport_uid: str) -> list[PassportVersionOut]:
        card = await self.repo.get_by_uid(passport_uid)
        if not card:
            raise HTTPException(status_code=404, detail="Passport not found")
        return [_version_to_out(v) for v in sorted(card.versions, key=lambda x: x.version_number)]

    async def edit_passport(self, passport_uid: str, body: PassportVersionCreate, user_id: int, request: Request) -> PassportCardOut:
        card = await self.repo.get_by_uid(passport_uid)
        if not card:
            raise HTTPException(status_code=404, detail="Passport not found")
        if card.is_archived:
            raise HTTPException(status_code=400, detail="Cannot edit archived passport")

        old_version = self.repo.get_current_version(card)
        old_data = PassportVersionOut.model_validate(old_version).model_dump(mode="json") if old_version else None

        # Deactivate current version (flag only — no data change)
        if old_version:
            old_version.is_current = False

        # New version
        max_v = self.repo.get_max_version_number(card)
        fields = body.model_dump(exclude={"device", "storage_devices", "monitors", "peripherals", "software_installations"})
        new_version = PassportVersion(
            passport_card_id=card.id, version_number=max_v + 1,
            is_current=True, created_by=user_id, **fields
        )
        await self.repo.create_version(new_version)
        await self.versioning.attach_children(new_version, body)

        new_data = body.model_dump(mode="json")
        changed = compute_changed_fields(old_data or {}, new_data)

        await self.audit.log(
            user_id, AuditActionType.edit, "passport",
            entity_id=passport_uid, entity_version_id=new_version.id,
            old_data=old_data, new_data=new_data, changed_fields=changed, request=request,
        )

        refreshed = await self.repo.get_by_id(card.id)
        return _card_to_out(refreshed, self.repo)

    async def archive_passport(self, passport_uid: str, user_id: int, request: Request) -> PassportCardOut:
        card = await self.repo.get_by_uid(passport_uid)
        if not card:
            raise HTTPException(status_code=404, detail="Passport not found")

        card.is_archived = True
        current = self.repo.get_current_version(card)
        if current:
            current.status = PassportStatus.archived

        await self.audit.log(user_id, AuditActionType.archive, "passport", entity_id=passport_uid, request=request)
        return _card_to_out(card, self.repo)
