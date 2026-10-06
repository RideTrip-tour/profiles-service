from unittest.mock import MagicMock

import pytest

from app.crud.devices_crud import (
    create_or_update_device,
    delete_device,
    get_device,
    get_devices,
)


@pytest.mark.asyncio
async def test_get_device_returns_device(db, device, result_mock):
    result_mock.scalar_one_or_none.return_value = device
    db.execute.return_value = result_mock
    result = await get_device(db, 10, "device-1")

    assert result is device


@pytest.mark.asyncio
async def test_create_or_update_device_creates_new_device(db, result_mock):
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock
    result = await create_or_update_device(
        db=db,
        profile_id=10,
        device_id="device-1",
        device_name="iPhone",
        platform="iOS",
        user_agent="test-agent",
    )

    assert result.profile_id == 10
    assert result.device_id == "device-1"
    assert result.device_name == "iPhone"
    assert result.platform == "iOS"
    assert result.user_agent == "test-agent"

    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_or_update_device_updates_existing_device(
    db, device, result_mock
):
    result_mock.scalar_one_or_none.return_value = device
    db.execute.return_value = result_mock
    result = await create_or_update_device(
        db=db,
        profile_id=10,
        device_id="device-1",
    )

    assert result is device
    assert result.last_seen_at is not None

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_devices_returns_devices(db, result_mock):
    devices = [MagicMock(), MagicMock()]
    result_mock.scalars.return_value.all.return_value = devices
    db.execute.return_value = result_mock
    result = await get_devices(db, 10)

    assert result == devices


@pytest.mark.asyncio
async def test_delete_device_deletes_existing_device(db, device, result_mock):
    result_mock.scalar_one_or_none.return_value = device
    db.execute.return_value = result_mock
    result = await delete_device(db, 10, "device-1")

    assert result is True

    db.delete.assert_awaited_once_with(device)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_device_returns_false_when_device_not_found(db, result_mock):
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    result = await delete_device(db, 10, "device-1")

    assert result is False
    db.delete.assert_not_called()
    db.commit.assert_not_awaited()
