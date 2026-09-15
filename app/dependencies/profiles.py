from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.dependencies.auth import get_current_profile_id
from app.services.profiles_manager import ProfileManager


async def get_profile_manager(
    session: AsyncSession = Depends(get_async_session),
) -> ProfileManager:
    return ProfileManager(session)


async def get_current_profile(
    profile_id: int = Depends(get_current_profile_id),
    profile_manager: ProfileManager = Depends(get_profile_manager),
):
    return await profile_manager.get_profile_by_id(profile_id)
