import logging

from app.publishers.connectors import ProtocolConnector, PublishResult

logger = logging.getLogger(__name__)


class TaskPublisher:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, connector: ProtocolConnector) -> None:
        self._connector = connector

    async def soft_delete_account(self, user_id: int) -> PublishResult:
        return await self._connector.publish(
            queue="auth",
            task_name="auth.soft_delete_account",
            kwargs={"user_id": user_id},
        )

    async def soft_delete_profile(
        self,
        user_id: int,
        countdown: int | None = None,
    ) -> PublishResult:
        return await self._connector.publish(
            queue="profile",
            task_name="profile.soft_delete_profile",
            kwargs={"user_id": user_id},
            countdown=countdown,
        )

    async def delete_profile_and_account(self, user_id: int) -> None:
        profile_task = await self.soft_delete_profile(
            user_id=user_id,
            countdown=30,
        )

        try:
            account_task = await self.soft_delete_account(user_id)
            logger.info(
                "Profile and account deletion tasks published: "
                "user_id=%s profile_task_id=%s account_task_id=%s",
                user_id,
                profile_task.message_id,
                account_task.message_id,
            )
        except Exception:
            try:
                await self._connector.revoke(profile_task.message_id)
            except Exception:
                logger.exception(
                    "Failed to cancel profile deletion task: %s",
                    profile_task.message_id,
                )
            raise
