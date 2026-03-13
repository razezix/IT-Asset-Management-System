from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, String, Integer, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class PassportStatus(str, enum.Enum):
    active = "active"
    archived = "archived"


class PassportCard(Base):
    __tablename__ = "passport_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passport_uid: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    versions: Mapped[list["PassportVersion"]] = relationship(
        "PassportVersion", back_populates="passport_card", order_by="PassportVersion.version_number"
    )
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])


class PassportVersion(Base):
    __tablename__ = "passport_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passport_card_id: Mapped[int] = mapped_column(ForeignKey("passport_cards.id", ondelete="CASCADE"))
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[PassportStatus] = mapped_column(SAEnum(PassportStatus), default=PassportStatus.active)

    passport_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    employee_fio: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    responsible_fio: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    room: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    fill_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    user_signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tech_signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    passport_card: Mapped["PassportCard"] = relationship("PassportCard", back_populates="versions")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])

    device: Mapped[Optional["DeviceVersion"]] = relationship(
        "DeviceVersion", back_populates="passport_version", uselist=False, cascade="all, delete-orphan"
    )
    storage_devices: Mapped[list["StorageDevice"]] = relationship(
        "StorageDevice", back_populates="passport_version", cascade="all, delete-orphan"
    )
    monitors: Mapped[list["Monitor"]] = relationship(
        "Monitor", back_populates="passport_version", cascade="all, delete-orphan"
    )
    peripherals: Mapped[list["Peripheral"]] = relationship(
        "Peripheral", back_populates="passport_version", cascade="all, delete-orphan"
    )
    software_installations: Mapped[list["SoftwareInstallation"]] = relationship(
        "SoftwareInstallation", back_populates="passport_version", cascade="all, delete-orphan"
    )
