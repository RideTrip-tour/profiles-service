import pytest

from app.services.cache_manager import CacheManager


@pytest.mark.asyncio
async def test_get_returns_cached_value(redis_client):
    cache = CacheManager(redis_client)
    redis_client.data["test:key"] = "value"
    result = await cache.get("test:key")
    assert result == "value"


@pytest.mark.asyncio
async def test_get_returns_none_for_missing_key(redis_client):
    cache = CacheManager(redis_client)
    result = await cache.get("test:key")
    assert result is None


@pytest.mark.asyncio
async def test_set_stores_value(redis_client):
    cache = CacheManager(redis_client)
    await cache.set(
        key="test:key",
        value="value",
    )
    assert redis_client.data["test:key"] == "value"


@pytest.mark.asyncio
async def test_delete_removes_value(redis_client):
    cache = CacheManager(redis_client)
    redis_client.data["test:key"] = "value"

    await cache.delete("test:key")
    assert "test:key" not in redis_client.data


def test_get_profile_id_key():
    assert CacheManager.get_profile_id_key(7) == "profile_service:profile_id:7"


def test_get_device_key():
    assert (
        CacheManager.get_device_key(1, "device-123")
        == "profile_service:device:1:device-123"
    )


def test_get_settings_key():
    assert CacheManager.get_settings_key(1) == "profile_service:settings:1"
