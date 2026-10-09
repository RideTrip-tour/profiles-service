import pytest


@pytest.mark.asyncio
async def test_get_returns_cached_value(redis_client, cache_manager):
    redis_client.data["test:key"] = "value"
    result = await cache_manager.get("test:key")
    assert result == "value"


@pytest.mark.asyncio
async def test_get_returns_none_for_missing_key(cache_manager):
    result = await cache_manager.get("test:key")
    assert result is None


@pytest.mark.asyncio
async def test_set_stores_value(redis_client, cache_manager):
    await cache_manager.set(
        key="test:key",
        value="value",
    )
    assert redis_client.data["test:key"] == "value"


@pytest.mark.asyncio
async def test_delete_removes_value(redis_client, cache_manager):
    redis_client.data["test:key"] = "value"
    await cache_manager.delete("test:key")
    assert "test:key" not in redis_client.data


def test_get_profile_id_key(cache_manager):
    assert (
        cache_manager.profile_keys.get_profile_id(7) == "profile_service:profile_id:7"
    )


def test_get_device_key(cache_manager):
    assert (
        cache_manager.device_keys.get_device(1, "device-123")
        == "profile_service:device:1:device-123"
    )


def test_get_show_profile_key(cache_manager):
    assert (
        cache_manager.profile_keys.get_show_profile(1)
        == "profile_service:show_profile:1"
    )
