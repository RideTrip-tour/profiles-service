import logging

from fastapi import APIRouter, Depends, Request, status

from app.dependencies.auth import check_user_access, get_current_user_id
from app.dependencies.profiles import get_profile_manager
from app.schemas.profiles_schemas import (
    FavoriteLocationCreate,
    FavoriteLocationResponse,
    FavoriteLocationsResponse,
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from app.services.profiles_manager import ProfileManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["Profiles"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProfileResponse)
async def create_new_profile(
    payload: ProfileCreate,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    user_id = get_current_user_id(request)
    return await manager.create_profile(user_id, payload)


@router.post(
    "/me/favorite-locations",
    status_code=status.HTTP_201_CREATED,
    response_model=FavoriteLocationResponse,
)
async def add_favorite_location(
    payload: FavoriteLocationCreate,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    return await manager.add_favorite_location(
        get_current_user_id(request),
        payload.location_id,
    )


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    return await manager.get_profile_by_user_id(get_current_user_id(request))


@router.get(
    "/me/favorite-locations",
    response_model=FavoriteLocationsResponse,
)
async def get_favorite_locations(
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    return FavoriteLocationsResponse(
        location_ids=await manager.get_favorite_location(get_current_user_id(request))
    )


@router.get(
    "/{user_id}/favorite-locations",
    response_model=FavoriteLocationsResponse,
)
async def get_favorite_locations_by_user_id(
    user_id: int,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    check_user_access(request, user_id)
    return FavoriteLocationsResponse(
        location_ids=await manager.get_favorite_location(user_id)
    )


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile_by_id(
    user_id: int,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    check_user_access(request, user_id)
    return await manager.get_profile_by_user_id(user_id)


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    payload: ProfileUpdate,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    return await manager.update_profile_by_user_id(
        get_current_user_id(request), payload
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_by_id(
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    await manager.delete_profile_by_user_id(get_current_user_id(request))


@router.delete(
    "/me/favorite-locations/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_favorite_location(
    location_id: int,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    await manager.delete_favorite_location(
        get_current_user_id(request),
        location_id,
    )
