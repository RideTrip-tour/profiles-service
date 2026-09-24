from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload

from app.crud.utils import _update_model
from app.db.models import Profile, ProfileSettings
from app.schemas.profiles_schemas import ProfileCreate, ProfileUpdate


async def _delete_profile(db: AsyncSession, profile: Profile) -> bool:
    if not profile:
        return False

    await db.delete(profile)
    await db.commit()

    return True


async def _update_profile(
    db: AsyncSession, profile: Profile, payload: ProfileUpdate
) -> Profile:
    return await _update_model(db, profile, payload)


async def _create_new_profile(
    db: AsyncSession, profile_data: dict[str, Any]
) -> Profile:
    created_profile = Profile(
        settings=ProfileSettings(
            show_profile=True,
            show_name_in_reviews=True,
            use_activity_for_recommendations=True,
            use_profile_for_recommendations=True,
            use_city_for_tour_matching=True,
        ),
        **profile_data,
    )
    db.add(created_profile)
    await db.commit()

    new_profile = await _find_by_id(db, created_profile.id)
    
    return new_profile


async def _find_by_id(db: AsyncSession, profile_id: int) -> Profile | None:
    return (
        await db.execute(
            select(Profile)
            .options(joinedload(Profile.settings), selectinload(Profile.favorites))
            .where(Profile.id == profile_id)
        )
    ).scalar_one_or_none()


async def _find_by_user_id(db: AsyncSession, user_id: int) -> Profile | None:
    return (
        await db.execute(
            select(Profile)
            .options(joinedload(Profile.settings), selectinload(Profile.favorites))
            .where(Profile.user_id == user_id)
        )
    ).scalar_one_or_none()


async def _find_id_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(Profile.id).where(Profile.user_id == user_id))
    return result.scalar_one_or_none()


async def create_profile(
    db: AsyncSession, user_id: int, profile_in: ProfileCreate
) -> Profile:
    profile_data = profile_in.model_dump(exclude_unset=True)
    profile_data["user_id"] = user_id
    return await _create_new_profile(db, profile_data)


async def admin_create_profile(db: AsyncSession, profile_in: ProfileCreate) -> Profile:
    profile_data = profile_in.model_dump(exclude_unset=True)
    return await _create_new_profile(db, profile_data)


async def get_profile_by_user_id(db: AsyncSession, user_id: int) -> Profile | None:
    return await _find_by_user_id(db, user_id)


async def get_profile_id_by_user_id(db: AsyncSession, user_id: int) -> int | None:
    return await _find_id_by_user_id(db, user_id)


async def get_profile_by_id(db: AsyncSession, profile_id: int) -> Profile | None:
    return await _find_by_id(db, profile_id)


async def delete_profile_by_user_id(db: AsyncSession, user_id: int) -> bool:
    """
    Удаляет профиль по user_id.
    Возвращает True если удален, иначе False.
    """
    profile = await _find_by_user_id(db, user_id)

    return await _delete_profile(db, profile)


async def delete_profile_by_id(db: AsyncSession, profile_id: int) -> bool:
    """
    Удаляет профиль по id.
    Возвращает True если удален, иначе False.
    """
    profile = await _find_by_id(db, profile_id)

    return await _delete_profile(db, profile)


async def update_profile_by_user_id(
    db: AsyncSession, user_id: int, payload: ProfileUpdate
) -> Profile | None:
    profile = await _find_by_user_id(db, user_id)
    if not profile:
        return None
    return await _update_profile(db, profile, payload)


async def update_profile_by_id(
    db: AsyncSession, profile_id: int, payload: ProfileUpdate
) -> Profile | None:
    profile = await _find_by_id(db, profile_id)

    return await _update_profile(db, profile, payload)
