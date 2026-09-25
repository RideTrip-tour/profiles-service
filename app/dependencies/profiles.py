from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.locations_client import LocationClient
from app.db.database import get_async_session
from app.dependencies.auth import get_current_profile_id
from app.services.cache_manager import CacheManager
from app.services.profiles_manager import ProfileManager


def get_location_client() -> LocationClient:
    return LocationClient()


def get_cache_manager(request: Request):
    return CacheManager(request.app.state.redis)


def get_profile_manager(
    session: AsyncSession = Depends(get_async_session),
    cache: CacheManager = Depends(get_cache_manager),
    location_client: LocationClient = Depends(get_location_client),
) -> ProfileManager:
    return ProfileManager(session, cache=cache, location_client=location_client)


async def get_current_profile(
    profile_id: int = Depends(get_current_profile_id),
    profile_manager: ProfileManager = Depends(get_profile_manager),
):
    return await profile_manager.get_profile_by_id(profile_id)
