from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserOut


def _to_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        roles=[ur.role.name for ur in user.user_roles],
    )


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def list_users(self) -> list[UserOut]:
        users = await self.repo.get_all()
        return [_to_out(u) for u in users]

    async def create_user(self, body: UserCreate) -> UserOut:
        existing = await self.repo.get_by_username(body.username)
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

        role = await self.repo.get_role_by_name(body.role_name)
        if not role:
            raise HTTPException(status_code=400, detail=f"Role '{body.role_name}' not found")

        user = User(
            username=body.username,
            password_hash=get_password_hash(body.password),
            full_name=body.full_name,
            email=body.email,
        )
        await self.repo.create(user)
        await self.repo.assign_role(user.id, role.id)
        refreshed = await self.repo.get_by_id(user.id)
        return _to_out(refreshed)

    async def update_user(self, user_id: int, body: UserUpdate) -> UserOut:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if body.full_name is not None:
            user.full_name = body.full_name
        if body.email is not None:
            user.email = body.email
        if body.is_active is not None:
            user.is_active = body.is_active

        return _to_out(user)

    async def change_role(self, user_id: int, role_name: str) -> UserOut:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        role = await self.repo.get_role_by_name(role_name)
        if not role:
            raise HTTPException(status_code=400, detail=f"Role '{role_name}' not found")

        await self.repo.replace_role(user, role)
        return _to_out(user)
