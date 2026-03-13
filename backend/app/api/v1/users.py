from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    from app.services.user_service import _to_out
    return _to_out(current_user)


@router.get("/", response_model=list[UserOut], dependencies=[Depends(require_admin)])
async def list_users(db: Annotated[AsyncSession, Depends(get_db)]):
    return await UserService(db).list_users()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_user(body: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await UserService(db).create_user(body)


@router.patch("/{user_id}", response_model=UserOut, dependencies=[Depends(require_admin)])
async def update_user(user_id: int, body: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await UserService(db).update_user(user_id, body)


@router.patch("/{user_id}/role", response_model=UserOut, dependencies=[Depends(require_admin)])
async def change_role(user_id: int, role_name: str, db: Annotated[AsyncSession, Depends(get_db)]):
    return await UserService(db).change_role(user_id, role_name)
