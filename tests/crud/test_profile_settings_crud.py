from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.crud.profile_settings_crud import (
    get_profile_settings,
    update_profile_settings,
)
from app.db.models import ProfileSettings


@pytest.fixture
def settings():
    return MagicMock(spec=ProfileSettings)


@pytest.mark.asyncio
async def test_get_profile_settings_returns_settings(db, settings, result_mock):
    result_mock.scalar_one_or_none.return_value = settings
    db.execute.return_value = result_mock

    result = await get_profile_settings(db, profile_id=10)

    assert result is settings

    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_profile_settings_returns_none_when_not_found(db, result_mock):
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock
    result = await get_profile_settings(db, profile_id=10)

    assert result is None

    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_profile_settings_returns_updated_settings(
    db, settings, payload, expected
):

    with patch(
        "app.crud.profile_settings_crud._update_model",
        new=AsyncMock(return_value=expected),
    ) as update_model:
        result = await update_profile_settings(db, settings, payload)

    assert result is expected
    update_model.assert_awaited_once_with(db, settings, payload)
