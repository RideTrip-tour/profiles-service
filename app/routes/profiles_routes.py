import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies.auth import get_current_user_id
from app.dependencies.profiles import get_profile_manager
from app.schemas.profiles_schemas import ProfileCreate, ProfileResponse, ProfileUpdate
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
