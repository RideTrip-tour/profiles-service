from app.publishers.connectors import ProtocolConnector, PublishResult


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
