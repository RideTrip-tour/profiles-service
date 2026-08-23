from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Profile
from app.schemas.profiles_schemas import ProfileCreate, ProfileUpdate


async def _delete_profile(db: AsyncSession, profile: Profile) -> bool:
    if not profile:
        return False

    await db.delete(profile)
    await db.commit()

    return True


async def _update_profile(
    db: AsyncSession, profile: Profile, payload: ProfileUpdate
) -> Profile | None:
    if not profile:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)

    return profile


async def _create_new_profie(db: AsyncSession, new_profile: Profile) -> Profile:
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)

    return new_profile


async def _find_by_id(db: AsyncSession, profile_id: int):
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    return result.scalar_one_or_none()


async def _find_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(Profile).where(Profile.user_id == user_id))
    return result.scalar_one_or_none()


async def create_profile(
    db: AsyncSession, user_id: int, profile_in: ProfileCreate
) -> Profile:
    profile_data = profile_in.model_dump(exclude_unset=True)
    new_profile = Profile(user_id=user_id, **profile_data)

    return await _create_new_profie(db, new_profile)


async def admin_create_profile(db: AsyncSession, profile_in: ProfileCreate) -> Profile:
    profile_data = profile_in.model_dump(exclude_unset=True)
    new_profile = Profile(**profile_data)

    return await _create_new_profie(db, new_profile)


async def get_profile_by_user_id(db: AsyncSession, user_id: int) -> Profile | None:
    return await _find_by_user_id(db, user_id)


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

    return await _update_profile(db, profile, payload)


async def update_profile_by_id(
    db: AsyncSession, profile_id: int, payload: ProfileUpdate
) -> Profile | None:
    profile = await _find_by_id(db, profile_id)

    return await _update_profile(db, profile, payload)
