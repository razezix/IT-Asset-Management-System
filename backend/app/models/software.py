from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SoftwareInstallation(Base):
    __tablename__ = "software_installations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passport_version_id: Mapped[int] = mapped_column(ForeignKey("passport_versions.id", ondelete="CASCADE"))
    software_name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    install_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    license_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    license_valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    passport_version: Mapped["PassportVersion"] = relationship("PassportVersion", back_populates="software_installations")
