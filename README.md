# IT Asset Management System (PC Passport)

A REST API backend for managing IT asset passports — digital records for PCs, laptops, and their peripherals within an organization.

## Overview

Each device gets a **passport** — a versioned document that tracks its hardware configuration, assigned employee, department, room, installed software, monitors, and peripherals. Every update creates a new version instead of overwriting the previous one, so the full history is always preserved.

## Features

- **Versioned passports** — insert-only history, nothing is ever deleted
- **Full audit log** — every create/update action is recorded with user and timestamp
- **Role-based access** — `admin`, `tech_support`, `viewer`
- **QR code** per device for quick lookup
- **Printable HTML form** for physical documentation
- **JWT authentication** — access + refresh tokens

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL (async via asyncpg) |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | python-jose + bcrypt |
| Validation | Pydantic v2 |

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Configuration

Copy `.env` and set your values:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/passport_db
SECRET_KEY=your-secret-key
```

### Run

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

### Migrations

```bash
alembic upgrade head
```

## API

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Login, get tokens |
| GET | `/api/v1/passports` | List all passports |
| POST | `/api/v1/passports` | Create passport |
| GET | `/api/v1/passports/{uid}` | Get passport by UID |
| PUT | `/api/v1/passports/{uid}` | Update (creates new version) |
| GET | `/api/v1/audit` | Audit log |
| GET | `/api/v1/users` | User management (admin only) |

## Roles

| Role | Permissions |
|---|---|
| `admin` | Full access, user management |
| `tech_support` | Create, edit, view passports |
| `viewer` | Read-only |

---

# Система учёта IT-активов (Паспорт ПК)

REST API бэкенд для ведения паспортов IT-оборудования — цифровых карточек на компьютеры, ноутбуки и периферию организации.

## Описание

Каждое устройство получает **паспорт** — версионируемый документ с конфигурацией железа, привязанным сотрудником, отделом, кабинетом, установленным ПО, мониторами и периферией. При каждом обновлении создаётся новая версия, а не перезапись — полная история хранится всегда.

## Возможности

- **Версионирование паспортов** — insert-only история, ничего не удаляется
- **Полный журнал аудита** — каждое действие записывается с пользователем и временем
- **Ролевой доступ** — `admin`, `tech_support`, `viewer`
- **QR-код** для каждого устройства
- **Печатная HTML-форма** для бумажной документации
- **JWT-аутентификация** — access + refresh токены

## Стек технологий

| Слой | Технология |
|---|---|
| Фреймворк | FastAPI |
| База данных | PostgreSQL (async через asyncpg) |
| ORM | SQLAlchemy 2.0 |
| Миграции | Alembic |
| Авторизация | python-jose + bcrypt |
| Валидация | Pydantic v2 |

## Запуск

### Требования

- Python 3.11+
- PostgreSQL

### Установка

```bash
cd backend
pip install -r requirements.txt
```

### Конфигурация

Заполните `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/passport_db
SECRET_KEY=your-secret-key
```

### Старт

```bash
uvicorn app.main:app --reload
```

Документация API: `http://localhost:8000/docs`

### Миграции

```bash
alembic upgrade head
```

## Роли

| Роль | Доступ |
|---|---|
| `admin` | Полный доступ, управление пользователями |
| `tech_support` | Создание, редактирование, просмотр паспортов |
| `viewer` | Только просмотр |
