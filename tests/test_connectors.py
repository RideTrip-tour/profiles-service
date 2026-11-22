import logging
from unittest.mock import MagicMock

import pytest

from app.publishers.connectors import PublishResult


@pytest.mark.asyncio
async def test_publish_returns_publish_result(celery_connector, celery_app):
    celery_app.send_task.return_value = MagicMock(id="task-123")

    result = await celery_connector.publish(
        queue="auth",
        task_name="auth.soft_delete_account",
        args=[1],
        kwargs={"user_id": 1},
    )

    assert result == PublishResult(message_id="task-123")

    celery_app.send_task.assert_called_once_with(
        "auth.soft_delete_account",
        args=[1],
        kwargs={"user_id": 1},
        queue="auth",
        countdown=None,
    )


@pytest.mark.asyncio
async def test_publish_uses_empty_args_and_kwargs_by_default(
    celery_connector,
    celery_app,
):
    celery_app.send_task.return_value = MagicMock(id="task-123")

    await celery_connector.publish(
        queue="auth",
        task_name="auth.soft_delete_account",
    )

    celery_app.send_task.assert_called_once_with(
        "auth.soft_delete_account", args=[], kwargs={}, queue="auth", countdown=None
    )


@pytest.mark.asyncio
async def test_publish_logs_and_reraises_exception(
    celery_connector,
    celery_app,
    caplog,
):
    error = ConnectionError("Redis connection failed")
    celery_app.send_task.side_effect = error

    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ConnectionError, match="Redis connection failed"),
    ):
        await celery_connector.publish(
            queue="auth",
            task_name="auth.soft_delete_account",
            kwargs={"user_id": 1},
        )

    celery_app.send_task.assert_called_once()

    assert (
        "Failed to publish Celery task: auth.soft_delete_account to queue: auth"
    ) in caplog.text


@pytest.mark.asyncio
async def test_revoke_calls_celery_control(celery_connector, celery_app):
    await celery_connector.revoke(message_id="task-123")

    celery_app.control.revoke.assert_called_once_with("task-123")


@pytest.mark.asyncio
async def test_revoke_logs_and_reraises_exception(
    celery_connector,
    celery_app,
    caplog,
):
    error = ConnectionError("Redis connection failed")
    celery_app.control.revoke.side_effect = error

    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(ConnectionError, match="Redis connection failed"),
    ):
        await celery_connector.revoke(message_id="task-123")

    celery_app.control.revoke.assert_called_once_with("task-123")

    assert "Failed to revoke Celery task: task-123" in caplog.text
