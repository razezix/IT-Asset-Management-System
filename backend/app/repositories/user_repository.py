from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.role import Role, UserRole


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .where(User.username == username)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        result = await self.db.execute(
            select(User).options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        return list(result.scalars().all())

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def assign_role(self, user_id: int, role_id: int) -> None:
        self.db.add(UserRole(user_id=user_id, role_id=role_id))
        await self.db.flush()

    async def replace_role(self, user: User, role: Role) -> None:
        for ur in user.user_roles:
            await self.db.delete(ur)
        await self.db.flush()
        self.db.add(UserRole(user_id=user.id, role_id=role.id))
        await self.db.flush()
        await self.db.refresh(user, ["user_roles"])
