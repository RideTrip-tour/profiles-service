import logging

from fastapi import APIRouter, Request, status

from app.dependencies.auth import (
    can_view_profile,
    get_current_profile_id,
    get_current_user_id,
)
from app.dependencies.profiles import LocationIdDep, ProfileManagerDep, UserIdDep
from app.schemas.profiles_schemas import (
    FavoriteLocationCreate,
    FavoriteLocationResponse,
    FavoriteLocationsResponse,
    ProfileHiddenResponse,
    ProfileResponse,
    ProfileSettings,
    ProfileSettingsUpdate,
    ProfileUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["Profiles"])


@router.post(
    "/me/favorite-locations",
    status_code=status.HTTP_201_CREATED,
    response_model=FavoriteLocationResponse,
)
async def add_favorite_location(
    payload: FavoriteLocationCreate,
    request: Request,
    manager: ProfileManagerDep,
):
    return await manager.add_favorite_location(
        get_current_user_id(request),
        payload.location_id,
    )


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    request: Request,
    manager: ProfileManagerDep,
):
    return await manager.get_profile_by_user_id(get_current_user_id(request))


@router.get(
    "/me/favorite-locations",
    response_model=FavoriteLocationsResponse,
)
async def get_favorite_locations(
    request: Request,
    manager: ProfileManagerDep,
):
    return FavoriteLocationsResponse(
        location_ids=[
            FavoriteLocationResponse.model_validate(favorite_location)
            for favorite_location in await manager.get_favorite_location(
                get_current_user_id(request)
            )
        ]
    )


@router.get(
    "/{user_id:int}/favorite-locations",
    response_model=FavoriteLocationsResponse | ProfileHiddenResponse,
)
async def get_favorite_locations_by_user_id(
    user_id: UserIdDep,
    request: Request,
    manager: ProfileManagerDep,
):
    show_profile = await manager.get_show_profile(
        await manager.get_profile_id_or_raise(user_id)
    )
    if not can_view_profile(request, user_id, show_profile):
        return ProfileHiddenResponse(detail="Профиль скрыт")
    profile = await manager.get_profile_by_user_id(user_id)
    return FavoriteLocationsResponse(location_ids=profile.favorites)


@router.get("/{user_id:int}", response_model=ProfileResponse | ProfileHiddenResponse)
async def get_profile_by_id(
    user_id: UserIdDep,
    request: Request,
    manager: ProfileManagerDep,
):
    show_profile = await manager.get_show_profile(
        await manager.get_profile_id_or_raise(user_id)
    )
    if not can_view_profile(request, user_id, show_profile):
        return ProfileHiddenResponse(detail="Профиль скрыт")
    profile = await manager.get_profile_by_user_id(user_id)
    return profile


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    payload: ProfileUpdate,
    request: Request,
    manager: ProfileManagerDep,
):
    return await manager.update_profile_by_user_id(
        get_current_user_id(request), payload
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_by_id(
    request: Request,
    manager: ProfileManagerDep,
):
    await manager.delete_profile_by_user_id(get_current_user_id(request))


@router.delete(
    "/me/favorite-locations/{location_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_favorite_location(
    location_id: LocationIdDep,
    request: Request,
    manager: ProfileManagerDep,
):
    await manager.delete_favorite_location(
        get_current_user_id(request),
        location_id,
    )


@router.get(
    "/me/settings",
    response_model=ProfileSettings,
)
async def get_settings(
    request: Request,
    manager: ProfileManagerDep,
):
    return await manager.get_profile_settings(get_current_profile_id(request))


@router.patch(
    "/me/settings",
    response_model=ProfileSettings,
)
async def update_settings(
    request: Request,
    payload: ProfileSettingsUpdate,
    manager: ProfileManagerDep,
):
    return await manager.update_profile_settings(
        get_current_profile_id(request),
        payload,
    )
