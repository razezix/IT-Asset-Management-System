from typing import Optional
import enum
from sqlalchemy import Integer, String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PeripheralType(str, enum.Enum):
    printer = "printer"
    scanner = "scanner"
    headphones = "headphones"
    webcam = "webcam"
    speakers = "speakers"
    other = "other"


class Peripheral(Base):
    __tablename__ = "peripherals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passport_version_id: Mapped[int] = mapped_column(ForeignKey("passport_versions.id", ondelete="CASCADE"))
    peripheral_type: Mapped[PeripheralType] = mapped_column(SAEnum(PeripheralType), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    inventory_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    passport_version: Mapped["PassportVersion"] = relationship("PassportVersion", back_populates="peripherals")
