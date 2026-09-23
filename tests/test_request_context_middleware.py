import base64
import json
from datetime import UTC, datetime

import pytest
from fastapi import status


class StubProfileManager:
    def __init__(self):
        self.calls = []
        self.profile = {
            "id": 1,
            "user_id": 7,
            "role": "user",
            "first_name": "Ann",
            "last_name": "Smith",
            "phone_number": None,
            "birth_date": None,
            "about_me": None,
            "activities": [],
            "country": None,
            "city": None,
            "citizenship": None,
            "currency": None,
            "created_at": datetime(2024, 1, 1, tzinfo=UTC),
            "updated_at": datetime(2024, 1, 1, tzinfo=UTC),
        }

    async def get_profile_by_user_id(self, user_id):
        self.calls.append(("get_profile_by_user_id", user_id))
        return self.profile


class StubProfileContextManager:
    def __init__(self, db, cache, profile_id=1):
        self.db = db
        self.cache = cache
        self.profile_id = profile_id

    async def get_profile_id(self, user_id: int) -> int | None:
        assert user_id == 7
        return self.profile_id


@pytest.mark.asyncio
async def test_x_user_claims_header_is_restored_into_request_state(
    client, override_manager, monkeypatch
):
    manager = override_manager(StubProfileManager())

    monkeypatch.setattr(
        "app.middlerware.request_context.ProfileManager",
        lambda db, cache: StubProfileContextManager(
            db=db,
            cache=cache,
        ),
    )

    claims = base64.urlsafe_b64encode(json.dumps({"id": "7"}).encode("utf-8")).decode(
        "ascii"
    )

    response = await client.get(
        "/api/profile/me",
        headers={"X-User-Claims": claims},
    )

    assert response.status_code == status.HTTP_200_OK
    assert manager.calls == [("get_profile_by_user_id", 7)]


@pytest.mark.asyncio
async def test_x_user_claims_without_user_id_returns_401(client):
    claims = base64.urlsafe_b64encode(json.dumps({}).encode("utf-8")).decode("ascii")

    response = await client.get(
        "/api/profile/me",
        headers={"X-User-Claims": claims},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "User not identified"}


@pytest.mark.asyncio
async def test_profile_not_found_returns_401(client, monkeypatch):
    monkeypatch.setattr(
        "app.middlerware.request_context.ProfileManager",
        lambda db, cache: StubProfileContextManager(
            db=db,
            cache=cache,
            profile_id=None,
        ),
    )

    claims = base64.urlsafe_b64encode(json.dumps({"id": "7"}).encode("utf-8")).decode(
        "ascii"
    )

    response = await client.get(
        "/api/profile/me",
        headers={"X-User-Claims": claims},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Profile not found"}
