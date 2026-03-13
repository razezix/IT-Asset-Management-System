"""
Versioning Service — Insert-Only pattern.

Every edit creates a NEW PassportVersion; old versions are preserved with is_current=False.
This ensures complete audit trail without any UPDATE on existing version rows.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.passport import PassportVersion
from app.models.device import DeviceVersion, StorageDevice
from app.models.monitor import Monitor
from app.models.peripheral import Peripheral
from app.models.software import SoftwareInstallation
from app.schemas.passport import PassportVersionCreate


class VersioningService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def attach_children(self, version: PassportVersion, data: PassportVersionCreate) -> None:
        """Create all child records linked to the given version."""
        if data.device:
            self.db.add(DeviceVersion(
                passport_version_id=version.id,
                **data.device.model_dump()
            ))

        for s in data.storage_devices:
            self.db.add(StorageDevice(passport_version_id=version.id, **s.model_dump()))

        for m in data.monitors:
            self.db.add(Monitor(passport_version_id=version.id, **m.model_dump()))

        for p in data.peripherals:
            self.db.add(Peripheral(passport_version_id=version.id, **p.model_dump()))

        for sw in data.software_installations:
            self.db.add(SoftwareInstallation(passport_version_id=version.id, **sw.model_dump()))

        await self.db.flush()
