import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.dependencies.auth import get_current_user_id, require_services
from app.dependencies.profiles import get_profile_manager
from app.schemas.profiles_schemas import ProfileCreate, ProfileResponse
from app.services.profiles_manager import ProfileManager
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/internal/profile", tags=["Internal Profile"])

auth_service_dependency = Depends(require_services(settings.auth_service_id))


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=ProfileResponse,
    dependencies=[auth_service_dependency],
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Access allowed only for auth service",
        },
    },
)
async def create_new_profile(
    payload: ProfileCreate,
    request: Request,
    manager: Annotated[ProfileManager, Depends(get_profile_manager)],
):
    """
    Создание профиля пользователя.

    Ручка предназначена исключительно для внутреннего использования сервисом auth.
    Вызов из пользовательского клиента и других внутренних сервисов запрещён.
    """
    user_id = get_current_user_id(request)
    return await manager.create_profile(user_id, payload)

@router.delete(
    "/me/permanent",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[auth_service_dependency],
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Access allowed only for auth service",
        },
    },
)
async def permanently_delete_profile(
    request: Request,
    manager: Annotated[ProfileManager, Depends(get_profile_manager)],
):
    """
    Полное удаление профиля пользователя.

    Ручка предназначена исключительно для внутреннего использования сервисом auth.
    Вызов из пользовательского клиента и других внутренних сервисов запрещён.
    """
    await manager.delete_profile_permanently_by_user_id(get_current_user_id(request))


@router.post(
    "/me/restore",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[auth_service_dependency],
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Access allowed only for auth service",
        },
    },
)
async def restore_profile(
    request: Request,
    manager: Annotated[ProfileManager, Depends(get_profile_manager)],
):
    """
    Восстановление профиля пользователя.

    Ручка предназначена исключительно для внутреннего использования сервисом auth.
    Вызов из пользовательского клиента и других внутренних сервисов запрещён.
    """
    await manager.restore_profile_by_user_id(get_current_user_id(request))
