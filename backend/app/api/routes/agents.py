from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.models import User, UserRole
from app.schemas.schemas import UserOut
from app.core.security import get_current_user
from typing import List

router = APIRouter()


@router.get("/", response_model=List[UserOut])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(User).where(User.role.in_([UserRole.AGENT, UserRole.ADMIN]), User.is_active == True)
    )
    return result.scalars().all()
