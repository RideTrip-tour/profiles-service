from unittest.mock import AsyncMock, call

import pytest

from app.publishers.connectors import PublishResult


@pytest.mark.asyncio
async def test_soft_delete_account_publishes_task(
    task_publisher,
    celery_connector,
):
    expected_result = PublishResult(message_id="task-123")
    celery_connector.publish = AsyncMock(return_value=expected_result)

    result = await task_publisher.soft_delete_account(user_id=10)

    assert result == expected_result

    celery_connector.publish.assert_awaited_once_with(
        queue="auth",
        task_name="auth.soft_delete_account",
        kwargs={"user_id": 10},
    )


@pytest.mark.asyncio
async def test_soft_delete_profile_publishes_task(
    task_publisher,
    celery_connector,
):
    expected_result = PublishResult(message_id="task-123")
    celery_connector.publish = AsyncMock(return_value=expected_result)

    result = await task_publisher.soft_delete_profile(user_id=10)

    assert result == expected_result

    celery_connector.publish.assert_awaited_once_with(
        queue="profile",
        task_name="profile.soft_delete_profile",
        kwargs={"user_id": 10},
        countdown=None,
    )


@pytest.mark.asyncio
async def test_soft_delete_profile_publishes_task_with_countdown(
    task_publisher,
    celery_connector,
):
    expected_result = PublishResult(message_id="task-123")
    celery_connector.publish = AsyncMock(return_value=expected_result)

    result = await task_publisher.soft_delete_profile(
        user_id=10,
        countdown=30,
    )

    assert result == expected_result

    celery_connector.publish.assert_awaited_once_with(
        queue="profile",
        task_name="profile.soft_delete_profile",
        kwargs={"user_id": 10},
        countdown=30,
    )


@pytest.mark.asyncio
async def test_delete_profile_and_account_publishes_both_tasks(
    task_publisher,
    celery_connector,
):
    celery_connector.publish = AsyncMock(
        side_effect=[
            PublishResult(message_id="profile-123"),
            PublishResult(message_id="account-456"),
        ]
    )
    celery_connector.revoke = AsyncMock()

    await task_publisher.delete_profile_and_account(user_id=10)

    assert celery_connector.publish.await_args_list == [
        call(
            queue="profile",
            task_name="profile.soft_delete_profile",
            kwargs={"user_id": 10},
            countdown=30,
        ),
        call(
            queue="auth",
            task_name="auth.soft_delete_account",
            kwargs={"user_id": 10},
        ),
    ]

    celery_connector.revoke.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_profile_and_account_revokes_profile_task_on_error(
    task_publisher,
    celery_connector,
):
    celery_connector.publish = AsyncMock(
        side_effect=[
            PublishResult(message_id="profile-123"),
            ConnectionError("Redis unavailable"),
        ]
    )
    celery_connector.revoke = AsyncMock()

    with pytest.raises(ConnectionError, match="Redis unavailable"):
        await task_publisher.delete_profile_and_account(user_id=10)

    celery_connector.revoke.assert_awaited_once_with("profile-123")


@pytest.mark.asyncio
async def test_delete_profile_and_account_reraises_original_error_when_revoke_fails(
    task_publisher,
    celery_connector,
):
    celery_connector.publish = AsyncMock(
        side_effect=[
            PublishResult(message_id="profile-123"),
            ConnectionError("Redis unavailable"),
        ]
    )
    celery_connector.revoke = AsyncMock(side_effect=ConnectionError("Revoke failed"))

    with pytest.raises(ConnectionError, match="Redis unavailable"):
        await task_publisher.delete_profile_and_account(user_id=10)

    celery_connector.revoke.assert_awaited_once_with("profile-123")
