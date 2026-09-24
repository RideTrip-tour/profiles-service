class ProfileCacheKeys:
    """Формирует ключи кэша, связанные с профилем."""

    @staticmethod
    def get_profile_id(user_id: int) -> str:
        return f"profile_service:profile_id:{user_id}"

    @staticmethod
    def get_show_profile(profile_id: int) -> str:
        return f"profile_service:show_profile:{profile_id}"


class DeviceCacheKeys:
    """ "Формирует ключи кэша, связанные с устройствами профиля."""

    @staticmethod
    def get_device(profile_id: int, device_id: str) -> str:
        return f"profile_service:device:{profile_id}:{device_id}"
