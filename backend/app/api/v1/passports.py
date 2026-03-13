from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_tech_or_admin, require_any
from app.models.user import User
from app.schemas.passport import PassportVersionCreate, PassportCardOut, PassportVersionOut, PassportListItem
from app.services.passport_service import PassportService
from app.services.print_service import generate_print_html
from app.utils.enums import DeviceType

import io
import qrcode

router = APIRouter(prefix="/passports", tags=["passports"])


@router.get("/", response_model=list[PassportListItem])
async def list_passports(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_any)],
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    device_type: Optional[DeviceType] = Query(None),
    is_archived: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    return await PassportService(db).list_passports(search, department, device_type, is_archived, page, size)


@router.post("/", response_model=PassportCardOut, status_code=201)
async def create_passport(
    body: PassportVersionCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_tech_or_admin)],
):
    return await PassportService(db).create_passport(body, current_user.id, request)


@router.get("/{passport_uid}", response_model=PassportCardOut)
async def get_passport(
    passport_uid: str,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_any)],
):
    return await PassportService(db).get_passport(passport_uid, current_user.id, request)


@router.get("/{passport_uid}/versions", response_model=list[PassportVersionOut])
async def get_versions(
    passport_uid: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_any)],
):
    return await PassportService(db).get_versions(passport_uid)


@router.post("/{passport_uid}/versions", response_model=PassportCardOut)
async def edit_passport(
    passport_uid: str,
    body: PassportVersionCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_tech_or_admin)],
):
    return await PassportService(db).edit_passport(passport_uid, body, current_user.id, request)


@router.post("/{passport_uid}/archive", response_model=PassportCardOut)
async def archive_passport(
    passport_uid: str,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_tech_or_admin)],
):
    return await PassportService(db).archive_passport(passport_uid, current_user.id, request)


@router.get("/{passport_uid}/print", response_class=HTMLResponse)
async def print_passport(
    passport_uid: str,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_any)],
):
    svc = PassportService(db)
    passport = await svc.get_passport(passport_uid, current_user.id, request)
    return HTMLResponse(content=generate_print_html(passport))


@router.get("/{passport_uid}/qr")
async def get_qr(
    passport_uid: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_any)],
    base_url: str = Query("http://localhost:3000"),
):
    from sqlalchemy import select
    from app.models.passport import PassportCard
    result = await db.execute(select(PassportCard).where(PassportCard.passport_uid == passport_uid))
    if not result.scalar_one_or_none():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Passport not found")

    url = f"{base_url}/passports/{passport_uid}"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")
