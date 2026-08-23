from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.profiles_crud import (
    admin_create_profile as crud_admin_create_profile,
)
from app.crud.profiles_crud import (
    create_profile as crud_create_profile,
)
from app.crud.profiles_crud import (
    delete_profile_by_id as crud_delete_profile_by_id,
)
from app.crud.profiles_crud import (
    delete_profile_by_user_id as crud_delete_profile_by_user_id,
)
from app.crud.profiles_crud import (
    get_profile_by_id as crud_get_profile_by_id,
)
from app.crud.profiles_crud import (
    get_profile_by_user_id as crud_get_profile_by_user_id,
)
from app.crud.profiles_crud import (
    update_profile_by_id as crud_update_profile_by_id,
)
from app.crud.profiles_crud import (
    update_profile_by_user_id as crud_update_profile_by_user_id,
)
from app.schemas.admin_schemas import ProfileCreate as AdminProfileCreate
from app.schemas.profiles_schemas import ProfileCreate, ProfileUpdate


class ProfileManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_profile(self, user_id: int, profile_in: ProfileCreate):
        existing_profile = await crud_get_profile_by_user_id(self.db, user_id)
        self._raise_conflict_if_exists(existing_profile)

        return await crud_create_profile(self.db, user_id, profile_in)

    async def admin_create_profile(self, profile_in: AdminProfileCreate):
        existing_profile = await crud_get_profile_by_user_id(
            self.db, profile_in.user_id
        )
        self._raise_conflict_if_exists(existing_profile)

        return await crud_admin_create_profile(self.db, profile_in)

    async def get_profile_by_user_id(self, user_id: int):
        profile = await crud_get_profile_by_user_id(self.db, user_id)
        self._raise_not_found(profile)
        return profile

    async def get_profile_by_id(self, profile_id: int):
        profile = await crud_get_profile_by_id(self.db, profile_id)
        self._raise_not_found(profile)
        return profile

    async def update_profile_by_user_id(self, user_id: int, payload: ProfileUpdate):
        profile = await crud_update_profile_by_user_id(self.db, user_id, payload)
        self._raise_not_found(profile)
        return profile

    async def update_profile_by_id(self, profile_id: int, payload: ProfileUpdate):
        profile = await crud_update_profile_by_id(self.db, profile_id, payload)
        self._raise_not_found(profile)
        return profile

    async def delete_profile_by_user_id(self, user_id: int) -> None:
        deleted = await crud_delete_profile_by_user_id(self.db, user_id)
        self._raise_not_found(deleted)

    async def delete_profile_by_id(self, profile_id: int) -> None:
        deleted = await crud_delete_profile_by_id(self.db, profile_id)
        self._raise_not_found(deleted)

    @staticmethod
    def _raise_not_found(profile):
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )

    @staticmethod
    def _raise_conflict_if_exists(existing_profile):
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profile already exists",
            )
