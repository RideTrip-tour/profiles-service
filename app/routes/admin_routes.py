from fastapi import APIRouter, Depends, Request, status

from app.dependencies.profiles import get_profile_manager
from app.schemas.admin_schemas import ProfileCreate
from app.schemas.profiles_schemas import ProfileResponse, ProfileUpdate
from app.services.profiles_manager import ProfileManager

router = APIRouter(prefix="/api/admin/profile", tags=["Admin Profile"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProfileResponse)
async def create_new_profile(
    payload: ProfileCreate,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    return await manager.admin_create_profile(payload)


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile_by_id(
    profile_id: int,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    return await manager.get_profile_by_id(profile_id)


@router.get("/by-user/{user_id}", response_model=ProfileResponse)
async def get_profile_by_user_id(
    user_id: int,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    return await manager.get_profile_by_user_id(user_id)


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile_by_id(
    profile_id: int,
    payload: ProfileUpdate,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    return await manager.update_profile_by_id(profile_id, payload)


@router.patch("/by-user/{user_id}", response_model=ProfileResponse)
async def update_profile_by_user_id(
    user_id: int,
    payload: ProfileUpdate,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    return await manager.update_profile_by_user_id(user_id, payload)


@router.delete("/by-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_by_user_id(
    user_id: int,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    await manager.delete_profile_by_user_id(user_id)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_by_id(
    profile_id: int,
    request: Request,
    manager: ProfileManager = Depends(get_profile_manager),
):
    await manager.delete_profile_by_id(profile_id)
