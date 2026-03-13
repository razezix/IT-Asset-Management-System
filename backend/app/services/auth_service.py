from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.models.audit import AuthLog, AuthEventType
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    async def login(self, username: str, password: str, request: Request) -> TokenResponse:
        user = await self.user_repo.get_by_username(username)
        ip = request.client.host if request else None
        ua = request.headers.get("user-agent") if request else None

        if not user or not verify_password(password, user.password_hash) or not user.is_active:
            await self.audit_repo.create_auth_log(AuthLog(event_type=AuthEventType.login_failed, ip_address=ip, user_agent=ua))
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        await self.audit_repo.create_auth_log(
            AuthLog(user_id=user.id, event_type=AuthEventType.login_success, ip_address=ip, user_agent=ua)
        )
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user = await self.user_repo.get_by_id(int(payload["sub"]))
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        await self.audit_repo.create_auth_log(
            AuthLog(user_id=user.id, event_type=AuthEventType.token_refresh)
        )
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
