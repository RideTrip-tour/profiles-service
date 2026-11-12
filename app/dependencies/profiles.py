from typing import Annotated

from fastapi import Depends, HTTPException, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.gateway_client import GatewayClient
from app.db.database import get_async_session
from app.dependencies.auth import get_current_profile_id
from app.schemas.constants import MAX_VALUE_INTEGER, MIN_VALUE_INTEGER
from app.services.cache_manager import CacheManager
from app.services.profiles_manager import ProfileManager


def get_gateway_client() -> GatewayClient:
    return GatewayClient()


def get_cache_manager(request: Request):
    return CacheManager(request.app.state.redis)


def get_profile_manager(
    session: AsyncSession = Depends(get_async_session),
    cache: CacheManager = Depends(get_cache_manager),
    gateway_client: GatewayClient = Depends(get_gateway_client),
) -> ProfileManager:
    return ProfileManager(session, cache=cache, gateway_client=gateway_client)


async def get_current_profile(
    profile_id: int = Depends(get_current_profile_id),
    profile_manager: ProfileManager = Depends(get_profile_manager),
):
    return await profile_manager.get_profile_by_id(profile_id)


def validate_path_id(path_id: str):
    def validate(
        value: int = Path(alias=path_id),
    ) -> int:
        if not MIN_VALUE_INTEGER <= value <= MAX_VALUE_INTEGER:
            raise HTTPException(
                status_code=404,
                detail="Not Found",
            )
        return value

    return validate


UserIdDep = Annotated[int, Depends(validate_path_id("user_id"))]
ProfileIdDep = Annotated[int, Depends(validate_path_id("profile_id"))]
LocationIdDep = Annotated[int, Depends(validate_path_id("location_id"))]
ProfileManagerDep = Annotated[ProfileManager, Depends(get_profile_manager)]
