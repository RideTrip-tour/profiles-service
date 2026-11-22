from unittest.mock import AsyncMock, patch

import pytest

from app.tasks.profile_tasks import SoftDeleteProfileTask


@pytest.mark.asyncio
async def test_run_async(db):
    task = SoftDeleteProfileTask()
    task.db = db

    with patch(
        "app.tasks.profile_tasks.delete_profile_by_user_id",
        new_callable=AsyncMock,
    ) as delete_mock:
        result = await task.run_async(user_id=10)

    assert result is None

    delete_mock.assert_awaited_once_with(
        db=db,
        user_id=10,
    )


def test_task_configuration():
    task = SoftDeleteProfileTask()

    assert task.name == "profile.soft_delete_profile"
    assert task.max_retries == 5
    assert task.retry_backoff == 5
    assert task.retry_backoff_max == 300
    assert task.retry_jitter is True
