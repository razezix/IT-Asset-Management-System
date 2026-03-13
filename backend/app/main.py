from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.db.init_db import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_database()
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="""
**PC Passport System** — электронный учёт паспортов ПК и ноутбуков.

### Роли
- `admin` — полный доступ
- `tech_support` — создание, редактирование, просмотр
- `viewer` — только просмотр

### Особенности
- Insert-only версионирование (история изменений сохраняется навсегда)
- Полный журнал аудита
- QR-код для каждого устройства
- Печатная HTML-форма
    """,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
