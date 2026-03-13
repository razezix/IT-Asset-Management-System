"""
Passport endpoint tests — versioning and RBAC smoke tests.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

# Shared state
_tokens = {}


async def _login(client, username="admin", password="admin123"):
    r = await client.post("/api/v1/auth/login", json={"username": username, "password": password})
    return r.json()["access_token"]


@pytest.mark.anyio
async def test_create_passport():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _login(client)
        resp = await client.post(
            "/api/v1/passports/",
            json={
                "passport_number": "ПК-TEST-001",
                "employee_fio": "Тестов Тест Тестович",
                "department": "ИТ",
                "room": "100",
                "device": {
                    "device_type": "pc",
                    "model": "Test PC",
                    "serial_number": "SN-TEST-001",
                    "cpu": "Intel i5",
                    "ram_gb": 8,
                },
            },
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["passport_uid"].startswith("PP-")
    assert data["current_version"]["version_number"] == 1
    _tokens["uid"] = data["passport_uid"]


@pytest.mark.anyio
async def test_edit_creates_new_version():
    uid = _tokens.get("uid")
    if not uid:
        pytest.skip("No passport created")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await _login(client)
        resp = await client.post(
            f"/api/v1/passports/{uid}/versions",
            json={"employee_fio": "Новый Сотрудник Иванов", "department": "Бухгалтерия"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_version"]["version_number"] == 2
    assert data["current_version"]["employee_fio"] == "Новый Сотрудник Иванов"


@pytest.mark.anyio
async def test_viewer_cannot_create():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create viewer first
        admin_token = await _login(client)
        await client.post(
            "/api/v1/users/",
            json={"username": "viewer_test", "password": "viewer123", "full_name": "Viewer", "role_name": "viewer"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        viewer_token = await _login(client, "viewer_test", "viewer123")
        resp = await client.post(
            "/api/v1/passports/",
            json={"passport_number": "TEST"},
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
    assert resp.status_code == 403
