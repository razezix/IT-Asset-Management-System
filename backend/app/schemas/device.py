from typing import Optional
from pydantic import BaseModel
from app.models.device import DeviceType, GpuType, StorageKind


class DeviceVersionCreate(BaseModel):
    device_type: DeviceType
    model: Optional[str] = None
    serial_number: Optional[str] = None
    inventory_number: Optional[str] = None
    cpu: Optional[str] = None
    ram_gb: Optional[int] = None
    gpu_model: Optional[str] = None
    gpu_memory_gb: Optional[float] = None
    gpu_bus_type: Optional[str] = None
    gpu_type: Optional[GpuType] = None
    notes: Optional[str] = None


class DeviceVersionOut(DeviceVersionCreate):
    id: int
    model_config = {"from_attributes": True}


class StorageDeviceCreate(BaseModel):
    storage_kind: StorageKind
    controller_type: Optional[str] = None
    capacity_gb: Optional[int] = None
    quantity: int = 1


class StorageDeviceOut(StorageDeviceCreate):
    id: int
    model_config = {"from_attributes": True}
