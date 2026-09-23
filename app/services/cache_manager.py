from redis.asyncio import Redis

from config import settings


class CacheManager:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

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

    @staticmethod
    def get_profile_id_key(user_id: int) -> str:
        return f"profile_service:profile_id:{user_id}"

    @staticmethod
    def get_device_key(
        profile_id: int,
        device_id: str,
    ) -> str:
        return f"profile_service:device:{profile_id}:{device_id}"

    @staticmethod
    def get_settings_key(profile_id: int) -> str:
        return f"profile_service:settings:{profile_id}"
