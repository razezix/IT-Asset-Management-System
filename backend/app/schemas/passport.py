from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.passport import PassportStatus
from app.schemas.device import DeviceVersionCreate, DeviceVersionOut, StorageDeviceCreate, StorageDeviceOut
from app.schemas.peripheral import MonitorCreate, MonitorOut, PeripheralCreate, PeripheralOut
from app.schemas.software import SoftwareInstallationCreate, SoftwareInstallationOut


class PassportVersionCreate(BaseModel):
    passport_number: Optional[str] = None
    employee_fio: Optional[str] = None
    responsible_fio: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    room: Optional[str] = None
    fill_date: Optional[datetime] = None
    user_signature: Optional[str] = None
    tech_signature: Optional[str] = None

    device: Optional[DeviceVersionCreate] = None
    storage_devices: list[StorageDeviceCreate] = []
    monitors: list[MonitorCreate] = []
    peripherals: list[PeripheralCreate] = []
    software_installations: list[SoftwareInstallationCreate] = []


class PassportVersionOut(BaseModel):
    id: int
    passport_card_id: int
    version_number: int
    is_current: bool
    status: PassportStatus
    passport_number: Optional[str]
    employee_fio: Optional[str]
    responsible_fio: Optional[str]
    position: Optional[str]
    department: Optional[str]
    room: Optional[str]
    fill_date: Optional[datetime]
    user_signature: Optional[str]
    tech_signature: Optional[str]
    created_at: datetime
    created_by: int

    device: Optional[DeviceVersionOut] = None
    storage_devices: list[StorageDeviceOut] = []
    monitors: list[MonitorOut] = []
    peripherals: list[PeripheralOut] = []
    software_installations: list[SoftwareInstallationOut] = []

    model_config = {"from_attributes": True}


class PassportCardOut(BaseModel):
    id: int
    passport_uid: str
    created_at: datetime
    created_by: int
    is_archived: bool
    current_version: Optional[PassportVersionOut] = None

    model_config = {"from_attributes": True}


class PassportListItem(BaseModel):
    id: int
    passport_uid: str
    is_archived: bool
    created_at: datetime
    passport_number: Optional[str]
    employee_fio: Optional[str]
    department: Optional[str]
    room: Optional[str]
    device_type: Optional[str]
    device_model: Optional[str]
    status: Optional[str]
    version_number: Optional[int]

    model_config = {"from_attributes": True}
