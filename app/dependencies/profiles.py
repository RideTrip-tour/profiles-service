from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.services.profiles_manager import ProfileManager


async def get_profile_manager(
    session: AsyncSession = Depends(get_async_session),
) -> ProfileManager:
    return ProfileManager(session)
