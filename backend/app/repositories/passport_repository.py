from typing import Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.passport import PassportCard, PassportVersion
from app.models.device import DeviceVersion


# Options for eager-loading full passport with all relations
FULL_LOAD = [
    selectinload(PassportCard.versions).options(
        selectinload(PassportVersion.device),
        selectinload(PassportVersion.storage_devices),
        selectinload(PassportVersion.monitors),
        selectinload(PassportVersion.peripherals),
        selectinload(PassportVersion.software_installations),
    )
]


class PassportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_uid(self, passport_uid: str) -> Optional[PassportCard]:
        result = await self.db.execute(
            select(PassportCard)
            .where(PassportCard.passport_uid == passport_uid)
            .options(*FULL_LOAD)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, card_id: int) -> Optional[PassportCard]:
        result = await self.db.execute(
            select(PassportCard).where(PassportCard.id == card_id).options(*FULL_LOAD)
        )
        return result.scalar_one_or_none()

    async def list_passports(
        self,
        search: Optional[str] = None,
        department: Optional[str] = None,
        device_type: Optional[str] = None,
        is_archived: Optional[bool] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list, int]:
        query = (
            select(
                PassportCard,
                PassportVersion.passport_number,
                PassportVersion.employee_fio,
                PassportVersion.department,
                PassportVersion.room,
                PassportVersion.status,
                PassportVersion.version_number,
                DeviceVersion.device_type,
                DeviceVersion.model.label("device_model"),
            )
            .join(PassportVersion, and_(
                PassportVersion.passport_card_id == PassportCard.id,
                PassportVersion.is_current == True
            ), isouter=True)
            .join(DeviceVersion, DeviceVersion.passport_version_id == PassportVersion.id, isouter=True)
        )

        if is_archived is not None:
            query = query.where(PassportCard.is_archived == is_archived)
        if department:
            query = query.where(PassportVersion.department.ilike(f"%{department}%"))
        if device_type:
            query = query.where(DeviceVersion.device_type == device_type)
        if search:
            term = f"%{search}%"
            query = query.where(
                PassportVersion.employee_fio.ilike(term)
                | PassportVersion.passport_number.ilike(term)
                | PassportVersion.department.ilike(term)
                | PassportVersion.room.ilike(term)
                | DeviceVersion.model.ilike(term)
                | DeviceVersion.serial_number.ilike(term)
                | PassportCard.passport_uid.ilike(term)
            )

        total = (await self.db.execute(select(func.count()).select_from(query.subquery()))).scalar()
        offset = (page - 1) * size
        rows = (await self.db.execute(query.offset(offset).limit(size))).all()
        return rows, total

    async def create_card(self, card: PassportCard) -> PassportCard:
        self.db.add(card)
        await self.db.flush()
        return card

    async def create_version(self, version: PassportVersion) -> PassportVersion:
        self.db.add(version)
        await self.db.flush()
        return version

    def get_current_version(self, card: PassportCard) -> Optional[PassportVersion]:
        for v in card.versions:
            if v.is_current:
                return v
        return None

    def get_max_version_number(self, card: PassportCard) -> int:
        return max((v.version_number for v in card.versions), default=0)
