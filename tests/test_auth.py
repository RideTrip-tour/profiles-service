from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.dependencies.auth import get_current_user_id


def make_request(user):
    return SimpleNamespace(state=SimpleNamespace(user=user))


@pytest.mark.parametrize(
    ("user", "expected_user_id"),
    [
        ({"id": 42}, 42),
        ({"id": "42"}, 42),
    ],
)
def test_get_current_user_id_returns_integer_sub(user, expected_user_id):
    assert get_current_user_id(make_request(user)) == expected_user_id


@pytest.mark.parametrize(
    "user",
    [
        None,
        "not-a-dict",
        {},
        {"id": None},
        {"id": ""},
        {"id": "abc"},
    ],
)
def test_get_current_user_id_rejects_invalid_user_payload(user):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(make_request(user))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized"
