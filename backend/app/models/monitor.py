from typing import Optional
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passport_version_id: Mapped[int] = mapped_column(ForeignKey("passport_versions.id", ondelete="CASCADE"))
    model: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    diagonal: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    inventory_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    passport_version: Mapped["PassportVersion"] = relationship("PassportVersion", back_populates="monitors")
