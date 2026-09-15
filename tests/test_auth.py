from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status

from app.dependencies.auth import get_current_profile_id, get_current_user_id


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


@pytest.mark.parametrize(
    "user, expected_profile_id",
    [
        ({"id": 42, "profile_id": 100}, 100),
        ({"id": "42", "profile_id": "100"}, 100),
    ],
)
def test_get_current_profile_id_returns_integer_profile_id(
    user,
    expected_profile_id,
):
    request = make_request(user)
    assert get_current_profile_id(request) == expected_profile_id


def test_get_current_profile_id_raises_if_profile_id_missing():
    request = SimpleNamespace(
        state=SimpleNamespace(
            user={"id": 42},
        ),
    )
    with pytest.raises(HTTPException) as exc_info:
        get_current_profile_id(request)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "profile_id",
    [
        None,
        "",
        "abc",
        "12.5",
        [],
        {},
    ],
)
def test_get_current_profile_id_raises_for_invalid_profile_id(profile_id):
    request = make_request(
        {
            "id": 42,
            "profile_id": profile_id,
        }
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_profile_id(request)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
