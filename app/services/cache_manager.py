from redis.asyncio import Redis

from app.services.cache_keys import DeviceCacheKeys, ProfileCacheKeys
from config import settings


class CacheManager:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.profile_keys = ProfileCacheKeys()
        self.device_keys = DeviceCacheKeys()

    async def get(self, key: str) -> str | None:
        return await self.redis_client.get(key)

    async def set(
        self,
        key: str,
        value: str | int,
        ex: int = settings.redis_ttl,
    ) -> None:
        await self.redis_client.set(key, value, ex=ex)

    async def delete(self, key: str) -> None:
        await self.redis_client.delete(key)
