from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.crud.profiles_crud import (
    _create_new_profile,
    admin_create_profile,
    create_profile,
    delete_profile_by_id,
    delete_profile_by_user_id,
    get_profile_by_id,
    get_profile_by_user_id,
    get_profile_id_by_user_id,
    update_profile_by_id,
    update_profile_by_user_id,
)
from app.db.models import Profile


@pytest.fixture
def profile():
    return MagicMock(spec=Profile)


@pytest.mark.asyncio
async def test_create_new_profile_creates_profile(db):
    created_profile = MagicMock()
    created_profile.id = 10
    found_profile = MagicMock()

    with (
        patch(
            "app.crud.profiles_crud.Profile",
            return_value=created_profile,
        ) as profile_class,
        patch(
            "app.crud.profiles_crud.ProfileSettings",
        ) as settings_class,
        patch(
            "app.crud.profiles_crud._find_by_id",
            new=AsyncMock(return_value=found_profile),
        ) as find_by_id,
    ):
        result = await _create_new_profile(
            db,
            {"first_name": "Ann"},
        )

    profile_class.assert_called_once()
    settings_class.assert_called_once_with(
        show_profile=True,
        show_name_in_reviews=True,
        use_activity_for_recommendations=True,
        use_profile_for_recommendations=True,
        use_city_for_tour_matching=True,
    )
    db.add.assert_called_once_with(created_profile)
    db.commit.assert_awaited_once()
    find_by_id.assert_awaited_once_with(db, 10)

    assert result is found_profile


@pytest.mark.asyncio
async def test_create_new_profile_raises_when_profile_not_found(db):
    created_profile = MagicMock()
    created_profile.id = 10

    with (
        patch(
            "app.crud.profiles_crud.Profile",
            return_value=created_profile,
        ),
        patch("app.crud.profiles_crud.ProfileSettings"),
        patch(
            "app.crud.profiles_crud._find_by_id",
            new=AsyncMock(return_value=None),
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="Created profile was not found",
        ):
            await _create_new_profile(
                db,
                {"first_name": "Ann"},
            )


@pytest.mark.asyncio
async def test_create_profile_adds_user_id(db, expected):
    profile_in = MagicMock()
    profile_in.model_dump.return_value = {"first_name": "Ann"}

    with patch(
        "app.crud.profiles_crud._create_new_profile",
        new=AsyncMock(return_value=expected),
    ) as create_new:
        result = await create_profile(db, 7, profile_in)

    assert result is expected
    create_new.assert_awaited_once_with(
        db,
        {
            "first_name": "Ann",
            "user_id": 7,
        },
    )


@pytest.mark.asyncio
async def test_admin_create_profile(db, expected):
    profile_in = MagicMock()
    profile_in.model_dump.return_value = {"first_name": "Ann"}

    with patch(
        "app.crud.profiles_crud._create_new_profile",
        new=AsyncMock(return_value=expected),
    ) as create_new:
        result = await admin_create_profile(db, profile_in)

    assert result is expected
    create_new.assert_awaited_once_with(
        db,
        {"first_name": "Ann"},
    )


@pytest.mark.asyncio
async def test_get_profile_by_user_id(db, expected, result_mock):
    result_mock.scalar_one_or_none.return_value = expected
    db.execute.return_value = result_mock

    result = await get_profile_by_user_id(db, 7)

    assert result is expected
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_profile_by_id(db, expected, result_mock):
    result_mock.scalar_one_or_none.return_value = expected
    db.execute.return_value = result_mock

    result = await get_profile_by_id(db, 10)

    assert result is expected
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_profile_by_user_id_returns_none(db, result_mock):
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    result = await get_profile_by_user_id(db, 7)

    assert result is None
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_profile_by_id_returns_none(db, result_mock):
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    result = await get_profile_by_id(db, 10)

    assert result is None
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_profile_id_by_user_id(db, result_mock):
    result_mock.scalar_one_or_none.return_value = 10
    db.execute.return_value = result_mock

    result = await get_profile_id_by_user_id(db, 7)

    assert result == 10
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_profile_id_by_user_id_returns_none(db, result_mock):
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    result = await get_profile_id_by_user_id(db, 7)

    assert result is None
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function", "identifier"),
    [
        (delete_profile_by_user_id, 7),
        (delete_profile_by_id, 10),
    ],
)
async def test_delete_profile_by_identifier(
    db, profile, function, identifier, result_mock
):
    result_mock.scalar_one_or_none.return_value = profile
    db.execute.return_value = result_mock

    result = await function(db, identifier)

    assert result is True
    db.delete.assert_awaited_once_with(profile)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_profile_returns_false_when_not_found(db, result_mock):
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock
    result = await delete_profile_by_id(db, 10)

    assert result is False

    db.delete.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function", "identifier"),
    [
        (update_profile_by_user_id, 7),
        (update_profile_by_id, 10),
    ],
)
async def test_update_profile_returns_none_when_not_found(
    db, payload, function, identifier, result_mock
):
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    result = await function(db, identifier, payload)

    assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function", "identifier"),
    [
        (update_profile_by_user_id, 7),
        (update_profile_by_id, 10),
    ],
)
async def test_update_profile(
    db, profile, payload, expected, function, identifier,
):
    with patch(
        "app.crud.profiles_crud._find_by_user_id"
        if function is update_profile_by_user_id
        else "app.crud.profiles_crud._find_by_id",
        new=AsyncMock(return_value=profile),
    ), patch(
        "app.crud.profiles_crud._update_profile",
        new=AsyncMock(return_value=expected),
    ) as update:
        result = await function(db, identifier, payload)

    assert result is expected
    update.assert_awaited_once_with(db, profile, payload)
