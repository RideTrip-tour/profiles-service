import asyncio

from celery import Celery


class CeleryClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, celery_app: Celery) -> None:
        if not hasattr(self, "celery_app"):
            self.celery_app = celery_app

    async def _send_task(
        self,
        queue: str,
        task_name: str,
        args: list | None = None,
        kwargs: dict | None = None,
    ) -> None:
        await asyncio.to_thread(
            self.celery_app.send_task,
            task_name,
            args=args or [],
            kwargs=kwargs or {},
            queue=queue,
        )

    async def soft_delete_account(self, user_id: int) -> None:
        await self._send_task(
            queue="auth",
            task_name="auth.soft_delete_account",
            kwargs={"user_id": user_id},
        )
