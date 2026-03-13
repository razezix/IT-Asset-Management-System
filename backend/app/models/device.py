from typing import Optional
import enum
from sqlalchemy import Integer, String, Float, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DeviceType(str, enum.Enum):
    pc = "pc"
    laptop = "laptop"


class GpuType(str, enum.Enum):
    integrated = "integrated"
    discrete = "discrete"


class StorageKind(str, enum.Enum):
    hdd = "HDD"
    ssd = "SSD"


class DeviceVersion(Base):
    __tablename__ = "device_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passport_version_id: Mapped[int] = mapped_column(ForeignKey("passport_versions.id", ondelete="CASCADE"), unique=True)
    device_type: Mapped[DeviceType] = mapped_column(SAEnum(DeviceType), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    inventory_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    cpu: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    ram_gb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gpu_model: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    gpu_memory_gb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gpu_bus_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gpu_type: Mapped[Optional[GpuType]] = mapped_column(SAEnum(GpuType), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    passport_version: Mapped["PassportVersion"] = relationship("PassportVersion", back_populates="device")


class StorageDevice(Base):
    __tablename__ = "storage_devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passport_version_id: Mapped[int] = mapped_column(ForeignKey("passport_versions.id", ondelete="CASCADE"))
    storage_kind: Mapped[StorageKind] = mapped_column(SAEnum(StorageKind), nullable=False)
    controller_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    capacity_gb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    passport_version: Mapped["PassportVersion"] = relationship("PassportVersion", back_populates="storage_devices")
