from typing import Optional
from pydantic import BaseModel
from app.models.peripheral import PeripheralType


class MonitorCreate(BaseModel):
    model: Optional[str] = None
    diagonal: Optional[str] = None
    serial_number: Optional[str] = None
    inventory_number: Optional[str] = None


class MonitorOut(MonitorCreate):
    id: int
    model_config = {"from_attributes": True}


class PeripheralCreate(BaseModel):
    peripheral_type: PeripheralType
    model: Optional[str] = None
    serial_number: Optional[str] = None
    inventory_number: Optional[str] = None
    notes: Optional[str] = None


class PeripheralOut(PeripheralCreate):
    id: int
    model_config = {"from_attributes": True}
