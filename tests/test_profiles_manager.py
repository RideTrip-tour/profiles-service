from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.schemas.admin_schemas import ProfileCreate as AdminProfileCreate
from app.schemas.profiles_schemas import ProfileCreate, ProfileUpdate
from app.services.profiles_manager import ProfileManager


@pytest.mark.asyncio
async def test_create_profile_raises_conflict_when_profile_exists(monkeypatch):
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

    manager = ProfileManager(db=object())

    with pytest.raises(HTTPException) as exc_info:
        await manager.create_profile(7, ProfileCreate(first_name="Ann"))

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Profile already exists"


@pytest.mark.asyncio
async def test_create_profile_calls_crud_when_profile_is_missing(monkeypatch):
    created_profile = SimpleNamespace(id=2, user_id=7, first_name="Ann")

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

    manager = ProfileManager(db=object())

    result = await manager.create_profile(7, ProfileCreate(first_name="Ann"))

    assert result is created_profile


@pytest.mark.asyncio
async def test_admin_create_profile_raises_conflict_when_profile_exists(monkeypatch):
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

    manager = ProfileManager(db=object())

    with pytest.raises(HTTPException) as exc_info:
        await manager.admin_create_profile(
            AdminProfileCreate(user_id=7, first_name="Ann")
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Profile already exists"


@pytest.mark.asyncio
async def test_admin_create_profile_calls_crud_when_profile_is_missing(monkeypatch):
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

    manager = ProfileManager(db=object())

    result = await manager.admin_create_profile(
        AdminProfileCreate(user_id=7, first_name="Ann")
    )

    assert result is created_profile


@pytest.mark.asyncio
async def test_get_profile_by_user_id_raises_not_found(monkeypatch):
    async def fake_get_profile_by_user_id(db, user_id):
        return None

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_by_user_id",
        fake_get_profile_by_user_id,
    )

    manager = ProfileManager(db=object())

    with pytest.raises(HTTPException) as exc_info:
        await manager.get_profile_by_user_id(7)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"


@pytest.mark.asyncio
async def test_get_profile_by_id_raises_not_found(monkeypatch):
    async def fake_get_profile_by_user_id(db, user_id):
        return None

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_get_profile_by_id",
        fake_get_profile_by_user_id,
    )

    manager = ProfileManager(db=object())

    with pytest.raises(HTTPException) as exc_info:
        await manager.get_profile_by_id(7)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"


@pytest.mark.asyncio
async def test_update_profile_passes_payload_to_crud(monkeypatch):
    updated_profile = SimpleNamespace(id=1, user_id=7, first_name="Updated")

    async def fake_update_profile(db, user_id, payload):
        assert user_id == 7
        assert payload.first_name == "Updated"
        return updated_profile

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_update_profile_by_user_id",
        fake_update_profile,
    )

    manager = ProfileManager(db=object())

    result = await manager.update_profile_by_user_id(
        7, ProfileUpdate(first_name="Updated")
    )

    assert result is updated_profile


@pytest.mark.asyncio
async def test_update_profile_raises_not_found_when_crud_returns_none(monkeypatch):
    async def fake_update_profile(db, user_id, payload):
        return None

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_update_profile_by_user_id",
        fake_update_profile,
    )

    manager = ProfileManager(db=object())

    with pytest.raises(HTTPException) as exc_info:
        await manager.update_profile_by_user_id(7, ProfileUpdate(first_name="Updated"))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"


@pytest.mark.asyncio
async def test_delete_profile_by_user_id_raises_not_found_when_nothing_deleted(
    monkeypatch,
):
    async def fake_delete_profile_by_user_id(db, user_id):
        return False

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_delete_profile_by_user_id",
        fake_delete_profile_by_user_id,
    )

    manager = ProfileManager(db=object())

    with pytest.raises(HTTPException) as exc_info:
        await manager.delete_profile_by_user_id(7)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"


@pytest.mark.asyncio
async def test_delete_profile_by_user_id_returns_none_on_success(monkeypatch):
    async def fake_delete_profile_by_user_id(db, user_id):
        assert user_id == 7
        return True

    monkeypatch.setattr(
        "app.services.profiles_manager.crud_delete_profile_by_user_id",
        fake_delete_profile_by_user_id,
    )

    manager = ProfileManager(db=object())

    result = await manager.delete_profile_by_user_id(7)

    assert result is None
