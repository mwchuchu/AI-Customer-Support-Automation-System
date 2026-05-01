#!/usr/bin/env python3
"""
Seed script — inserts demo users and sample tickets for development.
Run from backend/: python scripts/seed.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.chdir(os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal, engine, Base
from app.models.models import User, UserRole
from app.core.security import hash_password


DEMO_USERS = [
    {"email": "admin@demo.com",    "full_name": "Admin User",    "password": "admin123",  "role": UserRole.ADMIN},
    {"email": "customer@demo.com", "full_name": "John Customer", "password": "customer123","role": UserRole.CUSTOMER},
]


async def seed():
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        for u in DEMO_USERS:
            from sqlalchemy import select
            existing = (await db.execute(select(User).where(User.email == u["email"]))).scalar_one_or_none()
            if not existing:
                user = User(
                    email=u["email"],
                    full_name=u["full_name"],
                    hashed_password=hash_password(u["password"]),
                    role=u["role"],
                )
                db.add(user)
                print(f"✅ Created user: {u['email']} ({u['role']})")
            else:
                print(f"⏭️  Skipped (exists): {u['email']}")
        await db.commit()

    print("\n🎉 Seed complete!")
    print("─" * 40)
    for u in DEMO_USERS:
        print(f"  {u['role'].value:<10} {u['email']} / {u['password']}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
