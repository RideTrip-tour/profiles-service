import logging

from fastapi import APIRouter, status, Depends, Request, HTTPException, Query

from app.schemas.profiles_schemas import ProfileCreate, ProfileResponse, ProfileUpdate
from app.dependencies.auth import get_current_user_id
from app.dependencies.profiles import get_profile_manager
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


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    return await manager.get_profile_by_user_id(get_current_user_id(request))


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile_by_id(
    user_id: int,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    current_user_id = get_current_user_id(request)
    if current_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

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
    return None


@router.get("/me/favorite_locations", response_model=list[int])
async def get_favorite_locations(
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
) -> list[int]:
    user_id = get_current_user_id(request)
    profile = await manager.get_profile_by_user_id(user_id)
    return profile["favorite_location_ids"]


@router.post(
    "/me/favorite_locations",
    status_code=status.HTTP_200_OK,
    response_model=list[int],
)
async def add_favorite_locations(
    payload: list[int],
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
) -> list[int]:
    user_id = get_current_user_id(request)
    profile = await manager.get_profile_by_user_id(user_id)

    existing = set(profile["favorite_location_ids"])
    new_ids = set(payload)
    profile["favorite_location_ids"] = list(existing | new_ids)

    updated = await manager.update_profile_by_user_id(
        user_id,
        ProfileUpdate(favorite_location_ids=profile["favorite_location_ids"]),
    )
    return updated["favorite_location_ids"]


@router.delete(
    "/me/favorite_locations",
    status_code=status.HTTP_200_OK,
    response_model=list[int],
)
async def remove_favorite_locations(
    request: Request,
    ids: list[int] = Query(...),
    manager: ProfileManager = Depends(get_profile_manager),
) -> list[int]:
    user_id = get_current_user_id(request)
    profile = await manager.get_profile_by_user_id(user_id)

    existing = set(profile["favorite_location_ids"])
    to_remove = set(ids)
    profile["favorite_location_ids"] = list(existing - to_remove)

    updated = await manager.update_profile_by_user_id(
        user_id,
        ProfileUpdate(favorite_location_ids=profile["favorite_location_ids"]),
    )
    return updated["favorite_location_ids"]
