from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.schemas.admin_schemas import ProfileCreate as AdminProfileCreate
from app.schemas.profiles_schemas import (
    ProfileCreate,
    ProfileSettingsUpdate,
    ProfileUpdate,
)


@pytest.mark.asyncio
async def test_create_profile_raises_conflict_when_profile_exists(
    monkeypatch, profile_manager
):
    async def fake_get_profile_by_user_id(db, user_id):
        assert user_id == 7
        return SimpleNamespace(id=1, user_id=user_id)

    async def fake_create_profile(db, user_id, profile_in):
        raise AssertionError("create should not be called when profile exists")

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_by_user_id",
        fake_get_profile_by_user_id,
    )
    monkeypatch.setattr(
        "app.services.profiles_manager.crud_create_profile",
        fake_create_profile,
    )

    with pytest.raises(HTTPException) as exc_info:
        await profile_manager.create_profile(7, ProfileCreate(first_name="Ann"))

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Profile already exists"


@pytest.mark.asyncio
async def test_create_profile_calls_crud_when_profile_is_missing(
    monkeypatch, profile_manager
):
    created_profile = SimpleNamespace(
        id=2, user_id=7, first_name="Ann", settings=SimpleNamespace(show_profile=True)
    )

    async def fake_get_profile_by_user_id(db, user_id):
        return None

    async def fake_create_profile(db, user_id, profile_in):
        assert user_id == 7
        assert profile_in.first_name == "Ann"
        return created_profile

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_by_user_id",
        fake_get_profile_by_user_id,
    )
    monkeypatch.setattr(
        "app.services.profiles_manager.crud_create_profile",
        fake_create_profile,
    )

    result = await profile_manager.create_profile(7, ProfileCreate(first_name="Ann"))

    assert result is created_profile


@pytest.mark.asyncio
async def test_admin_create_profile_raises_conflict_when_profile_exists(
    monkeypatch, profile_manager
):
    async def fake_get_profile_by_user_id(db, user_id):
        assert user_id == 7
        return SimpleNamespace(id=1, user_id=user_id)

    async def fake_create_profile(db, user_id, profile_in):
        raise AssertionError("create should not be called when profile exists")

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_by_user_id",
        fake_get_profile_by_user_id,
    )
    monkeypatch.setattr(
        "app.services.profiles_manager.crud_admin_create_profile",
        fake_create_profile,
    )

    with pytest.raises(HTTPException) as exc_info:
        await profile_manager.admin_create_profile(
            AdminProfileCreate(user_id=7, first_name="Ann")
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Profile already exists"


@pytest.mark.asyncio
async def test_admin_create_profile_calls_crud_when_profile_is_missing(
    monkeypatch, profile_manager
):
    created_profile = SimpleNamespace(id=2, user_id=7, first_name="Ann")

    async def fake_get_profile_by_user_id(db, user_id):
        return None

    async def fake_create_profile(db, profile_in):
        assert profile_in.user_id == 7
        assert profile_in.first_name == "Ann"
        return created_profile

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_by_user_id",
        fake_get_profile_by_user_id,
    )
    monkeypatch.setattr(
        "app.services.profiles_manager.crud_admin_create_profile",
        fake_create_profile,
    )
    result = await profile_manager.admin_create_profile(
        AdminProfileCreate(user_id=7, first_name="Ann")
    )

    assert result is created_profile


@pytest.mark.asyncio
async def test_get_profile_by_user_id_raises_not_found(monkeypatch, profile_manager):
    async def fake_get_profile_by_user_id(db, user_id):
        return None

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_by_user_id",
        fake_get_profile_by_user_id,
    )

    with pytest.raises(HTTPException) as exc_info:
        await profile_manager.get_profile_by_user_id(7)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"


@pytest.mark.asyncio
async def test_get_profile_by_id_raises_not_found(monkeypatch, profile_manager):
    async def fake_get_profile_by_user_id(db, user_id):
        return None

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_by_id",
        fake_get_profile_by_user_id,
    )

    with pytest.raises(HTTPException) as exc_info:
        await profile_manager.get_profile_by_id(7)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"


@pytest.mark.asyncio
async def test_update_profile_passes_payload_to_crud(monkeypatch, profile_manager):
    updated_profile = SimpleNamespace(id=1, user_id=7, first_name="Updated")

    async def fake_update_profile(db, user_id, payload):
        assert user_id == 7
        assert payload.first_name == "Updated"
        return updated_profile

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_update_profile_by_user_id",
        fake_update_profile,
    )

    result = await profile_manager.update_profile_by_user_id(
        7, ProfileUpdate(first_name="Updated")
    )

    assert result is updated_profile


@pytest.mark.asyncio
async def test_update_profile_raises_not_found_when_crud_returns_none(
    monkeypatch, profile_manager
):
    async def fake_update_profile(db, user_id, payload):
        return None

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_update_profile_by_user_id",
        fake_update_profile,
    )

    with pytest.raises(HTTPException) as exc_info:
        await profile_manager.update_profile_by_user_id(
            7, ProfileUpdate(first_name="Updated")
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"


@pytest.mark.asyncio
async def test_delete_profile_by_user_id_raises_not_found_when_nothing_deleted(
    monkeypatch, profile_manager
):
    async def fake_delete_profile_by_user_id(db, user_id):
        return False

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_delete_profile_by_user_id",
        fake_delete_profile_by_user_id,
    )

    with pytest.raises(HTTPException) as exc_info:
        await profile_manager.delete_profile_by_user_id(7)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"


@pytest.mark.asyncio
async def test_delete_profile_by_user_id_returns_none_on_success(
    monkeypatch, profile_manager
):
    async def fake_delete_profile_by_user_id(db, user_id):
        assert user_id == 7
        return True

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_delete_profile_by_user_id",
        fake_delete_profile_by_user_id,
    )

    result = await profile_manager.delete_profile_by_user_id(7)

    assert result is None


@pytest.mark.asyncio
async def test_add_favorite_location_returns_created_location(
    monkeypatch, profile_manager
):
    favorite_location = SimpleNamespace(
        profile_id=1,
        location_id=10,
    )

    async def fake_get_or_create_favorite_location(
        db,
        user_id,
        location_id,
    ):
        assert user_id == 7
        assert location_id == 10
        return favorite_location

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_or_create_favorite_location",
        fake_get_or_create_favorite_location,
    )

    result = await profile_manager.add_favorite_location(7, 10)
    assert result is favorite_location


@pytest.mark.asyncio
async def test_add_favorite_location_raises_not_found_when_location_missing(
    monkeypatch, profile_manager
):
    async def fake_get_or_create_favorite_location(
        db,
        user_id,
        location_id,
    ):
        return None

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_or_create_favorite_location",
        fake_get_or_create_favorite_location,
    )
    with pytest.raises(HTTPException) as exc_info:
        await profile_manager.add_favorite_location(7, 10)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Not found"


@pytest.mark.asyncio
async def test_get_favorite_location_returns_location(monkeypatch, profile_manager):
    async def fake_get_favorite_location(db, user_id):
        assert user_id == 7
        return [
            {
                "location_id": 10,
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "location_id": 20,
                "created_at": "2024-01-02T00:00:00Z",
            },
        ]

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_favorite_location",
        fake_get_favorite_location,
    )
    result = await profile_manager.get_favorite_location(7)
    assert result == [
        {
            "location_id": 10,
            "created_at": "2024-01-01T00:00:00Z",
        },
        {
            "location_id": 20,
            "created_at": "2024-01-02T00:00:00Z",
        },
    ]


@pytest.mark.asyncio
async def test_get_favorite_location_returns_empty_list_when_no_locations(
    monkeypatch, profile_manager
):
    async def fake_get_favorite_location(db, user_id):
        assert user_id == 7
        return []

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_favorite_location",
        fake_get_favorite_location,
    )

    result = await profile_manager.get_favorite_location(7)
    assert result == []


@pytest.mark.asyncio
async def test_delete_favorite_location_calls_crud(monkeypatch, profile_manager):
    async def fake_delete_favorite_location(db, user_id, location_id):
        assert user_id == 7
        assert location_id == 10

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_delete_favorite_location",
        fake_delete_favorite_location,
    )

    result = await profile_manager.delete_favorite_location(7, 10)
    assert result is None


@pytest.mark.asyncio
async def test_get_profile_settings_returns_settings(
    profile_settings, monkeypatch, profile_manager
):

    async def fake_get_profile_settings(db, profile_id):
        assert profile_id == 1
        return profile_settings

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_settings",
        fake_get_profile_settings,
    )

    result = await profile_manager.get_profile_settings(1)

    assert result is profile_settings


@pytest.mark.asyncio
async def test_get_profile_settings_raises_not_found(monkeypatch, profile_manager):
    async def fake_get_profile_settings(db, profile_id):
        assert profile_id == 1

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_settings",
        fake_get_profile_settings,
    )

    with pytest.raises(HTTPException) as exc_info:
        await profile_manager.get_profile_settings(1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile settings not found"


@pytest.mark.asyncio
async def test_update_profile_settings_passes_payload_to_crud(
    profile_settings, monkeypatch, profile_manager
):
    update_data = {
        "show_profile": False,
    }

    async def fake_get_profile_settings(db, profile_id):
        assert profile_id == 1
        return profile_settings

    async def fake_update_profile_settings(db, settings_arg, payload):
        assert payload.model_dump(exclude_unset=True) == update_data
        settings_arg.show_profile = update_data.get("show_profile")
        return settings_arg

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_settings",
        fake_get_profile_settings,
    )
    monkeypatch.setattr(
        "app.services.profiles_manager.crud_update_profile_settings",
        fake_update_profile_settings,
    )

    payload = ProfileSettingsUpdate(**update_data)
    result = await profile_manager.update_profile_settings(1, payload)
    assert result.show_profile is False


@pytest.mark.asyncio
async def test_get_profile_id_returns_cached_value(
    redis_client,
    profile_manager,
    monkeypatch,
):
    redis_client.data["profile_service:profile_id:7"] = "1"

    async def mock_get_profile_id_by_user_id(*args, **kwargs):
        pytest.fail("Database should not be called")

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_id_by_user_id",
        mock_get_profile_id_by_user_id,
    )

    result = await profile_manager.get_profile_id(user_id=7)
    assert result == 1


@pytest.mark.asyncio
async def test_get_profile_id_loads_from_db_and_caches(
    redis_client,
    profile_manager,
    monkeypatch,
):
    async def mock_get_profile_id_by_user_id(user_id, db):
        assert user_id == 7
        return 1

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_id_by_user_id",
        mock_get_profile_id_by_user_id,
    )

    result = await profile_manager.get_profile_id(user_id=7)

    assert result == 1
    assert redis_client.data["profile_service:profile_id:7"] == 1


@pytest.mark.asyncio
async def test_get_profile_id_returns_none_when_profile_not_found(
    redis_client,
    profile_manager,
    monkeypatch,
):
    async def mock_get_profile_id_by_user_id(user_id, db):
        return None

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_id_by_user_id",
        mock_get_profile_id_by_user_id,
    )

    result = await profile_manager.get_profile_id(user_id=7)

    assert result is None
    assert redis_client.data == {}


@pytest.mark.asyncio
async def test_get_show_profile_returns_cached_value(
    profile_manager,
    redis_client,
    monkeypatch,
):
    key = profile_manager.cache.get_settings_key(profile_id=7)
    redis_client.data[key] = "1"

    async def mock_get_profile_settings(*args, **kwargs):
        pytest.fail("Database should not be called")

    monkeypatch.setattr(
        profile_manager,
        "get_profile_settings",
        mock_get_profile_settings,
    )
    result = await profile_manager.get_show_profile(profile_id=7)
    assert result is True


@pytest.mark.asyncio
async def test_get_show_profile_returns_false_from_cache(
    profile_manager,
    redis_client,
):
    key = profile_manager.cache.get_settings_key(profile_id=7)
    redis_client.data[key] = "0"

    result = await profile_manager.get_show_profile(profile_id=7)
    assert result is False


@pytest.mark.asyncio
async def test_get_show_profile_loads_from_db_and_caches_value(
    profile_manager,
    redis_client,
    monkeypatch,
):
    profile_settings = SimpleNamespace(show_profile=True)

    async def mock_get_profile_settings(*args, **kwargs):
        return profile_settings

    monkeypatch.setattr(
        profile_manager,
        "get_profile_settings",
        mock_get_profile_settings,
    )

    result = await profile_manager.get_show_profile(profile_id=7)
    key = profile_manager.cache.get_settings_key(profile_id=7)

    assert result is True
    assert redis_client.data[key] == "1"


@pytest.mark.asyncio
async def test_get_show_profile_caches_false_value(
    profile_manager,
    redis_client,
    monkeypatch,
):
    profile_settings = SimpleNamespace(show_profile=False)

    async def mock_get_profile_settings(*args, **kwargs):
        return profile_settings

    monkeypatch.setattr(
        profile_manager,
        "get_profile_settings",
        mock_get_profile_settings,
    )

    result = await profile_manager.get_show_profile(profile_id=7)
    key = profile_manager.cache.get_settings_key(profile_id=7)

    assert result is False
    assert redis_client.data[key] == "0"
