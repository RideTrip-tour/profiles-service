from sqlalchemy import delete, exists, literal, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FavoriteLocation, Profile


async def _find_favorite_location(
    db: AsyncSession,
    user_id: int,
) -> list[FavoriteLocation]:
    return list(
        (
            await db.execute(
                select(FavoriteLocation)
                .join(Profile, Profile.id == FavoriteLocation.profile_id)
                .where(Profile.user_id == user_id)
                .order_by(FavoriteLocation.created_at)
            )
        )
        .scalars()
        .all()
    )


async def get_or_create_favorite_location(
    db: AsyncSession, user_id: int, location_id: int
):
    profile_id = select(Profile.id).where(Profile.user_id == user_id).scalar_subquery()

    favorite_location = await db.execute(
        insert(FavoriteLocation)
        .from_select(
            ["profile_id", "location_id"],
            select(profile_id, literal(location_id)),
        )
        .on_conflict_do_update(
            index_elements=[
                FavoriteLocation.profile_id,
                FavoriteLocation.location_id,
            ],
            set_={
                "profile_id": FavoriteLocation.profile_id,
            },
        )
        .returning(FavoriteLocation)
    )
    await db.commit()
    return favorite_location.scalar_one_or_none()


async def get_favorite_location(
    db: AsyncSession, user_id: int
) -> list[FavoriteLocation]:
    return await _find_favorite_location(db, user_id)


async def delete_favorite_location(
    db: AsyncSession, user_id: int, location_id: int
) -> None:
    await db.execute(
        delete(FavoriteLocation).where(
            FavoriteLocation.location_id == location_id,
            exists(
                select(Profile.id).where(
                    Profile.id == FavoriteLocation.profile_id,
                    Profile.user_id == user_id,
                )
            ),
        )
    )
    await db.commit()
