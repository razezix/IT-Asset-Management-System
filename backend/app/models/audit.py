from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditActionType(str, enum.Enum):
    create = "CREATE"
    edit = "EDIT"
    view = "VIEW"
    archive = "ARCHIVE"


class AuthEventType(str, enum.Enum):
    login_success = "LOGIN_SUCCESS"
    login_failed = "LOGIN_FAILED"
    logout = "LOGOUT"
    token_refresh = "TOKEN_REFRESH"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action_type: Mapped[AuditActionType] = mapped_column(SAEnum(AuditActionType))
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    entity_version_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    old_data_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_data_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    changed_fields_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    user: Mapped["User"] = relationship("User", back_populates="audit_logs")


class AuthLog(Base):
    __tablename__ = "auth_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[AuthEventType] = mapped_column(SAEnum(AuthEventType))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="auth_logs")
