import asyncio

from celery import Task

from app.db.database import AsyncSessionLocalCelery


class AsyncDatabaseTask(Task):
    def __call__(self, *args, **kwargs):
        return asyncio.run(self._execute(*args, **kwargs))

    async def _execute(self, *args, **kwargs):
        async with AsyncSessionLocalCelery() as session:
            self.db = session

            try:
                return await self.run_async(*args, **kwargs)
            finally:
                del self.db

    async def run_async(self, *args, **kwargs):
        raise NotImplementedError
