from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SoftwareInstallationCreate(BaseModel):
    software_name: str
    version: Optional[str] = None
    install_date: Optional[datetime] = None
    license_key: Optional[str] = None
    license_valid_until: Optional[datetime] = None
    notes: Optional[str] = None


class SoftwareInstallationOut(SoftwareInstallationCreate):
    id: int
    model_config = {"from_attributes": True}
