from app.celery.app import app as celery_app
from app.celery.base_task import AsyncDatabaseTask
from app.crud.profiles_crud import delete_profile_by_user_id


class SoftDeleteProfileTask(AsyncDatabaseTask):
    name = "profile.soft_delete_profile"

    max_retries = 5
    retry_backoff = 5
    retry_backoff_max = 300
    retry_jitter = True

    async def run_async(self, user_id: int) -> None:
        await delete_profile_by_user_id(
            db=self.db,
            user_id=user_id,
        )


celery_app.register_task(SoftDeleteProfileTask())
