from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.role import Role, UserRole
from app.models.user import User


async def seed_database():
    async with AsyncSessionLocal() as db:
        try:
            roles = {}
            for name in ["admin", "tech_support", "viewer"]:
                r = (await db.execute(select(Role).where(Role.name == name))).scalar_one_or_none()
                if not r:
                    r = Role(name=name)
                    db.add(r)
                    await db.flush()
                roles[name] = r

            admin = (await db.execute(select(User).where(User.username == "admin"))).scalar_one_or_none()
            if not admin:
                admin = User(
                    username="admin",
                    password_hash=get_password_hash("admin123"),
                    full_name="Системный администратор",
                    email="admin@passport.local",
                )
                db.add(admin)
                await db.flush()
                db.add(UserRole(user_id=admin.id, role_id=roles["admin"].id))

            await db.commit()
            print("✅ DB seeded")
        except Exception as e:
            await db.rollback()
            print(f"❌ Seed error: {e}")
