from unittest.mock import MagicMock

import pytest

from app.crud.favorite_locations_crud import (
    delete_favorite_location,
    get_favorite_location,
    get_or_create_favorite_location,
)
from app.db.models import FavoriteLocation


@pytest.fixture
def favorite_location():
    return MagicMock(spec=FavoriteLocation)


@pytest.mark.asyncio
async def test_get_favorite_location_returns_locations(db, favorite_location, result_mock):
    locations = [favorite_location, MagicMock()]

    result_mock.scalars.return_value.all.return_value = locations
    db.execute.return_value = result_mock

    result = await get_favorite_location(db, 10)

    assert result == locations
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_or_create_favorite_location_returns_location(
    db, favorite_location, result_mock
):
    result_mock.scalar_one_or_none.return_value = favorite_location
    db.execute.return_value = result_mock

    result = await get_or_create_favorite_location(
        db,
        user_id=10,
        location_id=20,
    )

    assert result is favorite_location
    db.execute.assert_awaited_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_or_create_favorite_location_returns_none(db, result_mock):
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    result = await get_or_create_favorite_location(
        db,
        user_id=10,
        location_id=20,
    )

    assert result is None
    db.execute.assert_awaited_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_favorite_location(db):
    await delete_favorite_location(
        db,
        user_id=10,
        location_id=20,
    )

    db.execute.assert_awaited_once()
    db.commit.assert_awaited_once()
