from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.dependencies.auth import get_current_profile_id
from app.services.cache_manager import CacheManager
from app.services.profiles_manager import ProfileManager


def get_profile_manager(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> ProfileManager:
    return ProfileManager(session, CacheManager(request.app.state.redis))


async def get_current_profile(
    profile_id: int = Depends(get_current_profile_id),
    profile_manager: ProfileManager = Depends(get_profile_manager),
):
    return await profile_manager.get_profile_by_id(profile_id)
