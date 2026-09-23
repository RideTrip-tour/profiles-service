import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.devices_crud import (
    create_or_update_device as crud_create_or_update_device,
)
from app.crud.devices_crud import (
    delete_device as crud_delete_device,
)
from app.crud.devices_crud import (
    get_device as crud_get_device,
)
from app.crud.devices_crud import (
    get_devices as crud_get_devices,
)
from app.db.models import ProfileDevice
from app.services.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class DeviceManager:
    def __init__(self, db: AsyncSession, cache: CacheManager):
        self.db = db
        self.cache = cache

    async def register_device(
        self,
        profile_id: int,
        device_id: str,
        device_name: str | None = None,
        platform: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        Регистрирует устройство пользователя или обновляет last_seen_at.

        Redis используется для ограничения частоты обращений к базе:
        повторная регистрация одного устройства в течение TTL (300 c) не выполняет
        операцию с базой данных.
        """
        key = self.cache.get_device_key(profile_id, device_id)
        cached_device_seen = await self.cache.get(key)
        if cached_device_seen is None:
            logger.debug(
                "Device cache miss: profile_id=%s device_id=%s",
                profile_id,
                device_id,
            )
            await crud_create_or_update_device(
                self.db,
                profile_id,
                device_id,
                device_name,
                platform,
                user_agent,
            )
            logger.info(
                "Device registered or updated: profile_id=%s device_id=%s",
                profile_id,
                device_id,
            )
            await self.cache.set(key=key, value=f"{profile_id}-{device_id}")
            logger.debug(
                "Device cached: profile_id=%s device_id=%s",
                profile_id,
                device_id,
            )
        logger.debug(
            "Device cache hit: profile_id=%s device_id=%s",
            profile_id,
            device_id,
        )

    async def get_device(self, profile_id: int, device_id: str) -> ProfileDevice | None:
        return await crud_get_device(self.db, profile_id, device_id)

    async def get_devices(
        self,
        profile_id: int,
    ) -> list[ProfileDevice]:
        return await crud_get_devices(self.db, profile_id)

    async def delete_device(self, profile_id: int, device_id: str) -> None:
        deleted = await crud_delete_device(self.db, profile_id, device_id)
        if deleted:
            await self.cache.delete(self.cache.get_device_key(profile_id, device_id))
            logger.info(
                "Device deleted: profile_id=%s device_id=%s",
                profile_id,
                device_id,
            )
