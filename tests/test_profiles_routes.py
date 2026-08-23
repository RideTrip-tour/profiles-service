from datetime import UTC, datetime

import pytest
from fastapi import status


def expected_payload(**overrides):
    payload = {
        "first_name": None,
        "last_name": None,
        "phone_number": None,
        "age": None,
        "about_me": None,
        "activities": [],
        "country": None,
        "city": None,
        "citizenship": None,
        "currency": None,
    }
    payload.update(overrides)
    return payload


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
            "age": None,
            "about_me": None,
            "activities": [],
            "country": None,
            "city": None,
            "citizenship": None,
            "currency": None,
            "created_at": datetime(2024, 1, 1, tzinfo=UTC),
            "updated_at": datetime(2024, 1, 1, tzinfo=UTC),
        }

    async def create_profile(self, user_id, payload):
        self.calls.append(("create_profile", user_id, payload.model_dump()))
        return self.profile

    async def get_profile_by_user_id(self, user_id):
        self.calls.append(("get_profile_by_user_id", user_id))
        return self.profile

    async def update_profile_by_user_id(self, user_id, payload):
        self.calls.append(("update_profile_by_user_id", user_id, payload.model_dump()))
        return {**self.profile, **payload.model_dump(exclude_unset=True)}

    async def delete_profile_by_user_id(self, user_id):
        self.calls.append(("delete_profile_by_user_id", user_id))


@pytest.mark.asyncio
async def test_create_profile_uses_current_user_id(
    client, override_manager, monkeypatch
):
    manager = override_manager(StubProfileManager())
    monkeypatch.setattr("app.routes.profiles_routes.get_current_user_id", lambda _: 7)

    response = await client.post("/api/profile/", json={"first_name": "Ann"})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["user_id"] == 7
    assert manager.calls == [("create_profile", 7, expected_payload(first_name="Ann"))]


@pytest.mark.asyncio
async def test_get_profile_by_id_returns_forbidden_for_another_user(
    client, override_manager, monkeypatch
):
    manager = override_manager(StubProfileManager())
    monkeypatch.setattr("app.routes.profiles_routes.get_current_user_id", lambda _: 7)

    response = await client.get("/api/profile/8")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Forbidden"
    assert manager.calls == []


@pytest.mark.asyncio
async def test_get_my_profile_uses_current_user_id(
    client, override_manager, monkeypatch
):
    manager = override_manager(StubProfileManager())
    monkeypatch.setattr("app.routes.profiles_routes.get_current_user_id", lambda _: 7)

    response = await client.get("/api/profile/me")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert manager.calls == [("get_profile_by_user_id", 7)]


@pytest.mark.asyncio
async def test_update_my_profile_uses_current_user_id(
    client, override_manager, monkeypatch
):
    manager = override_manager(StubProfileManager())
    monkeypatch.setattr("app.routes.profiles_routes.get_current_user_id", lambda _: 7)

    response = await client.patch("/api/profile/me", json={"first_name": "Updated"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == "Updated"
    assert manager.calls == [
        ("update_profile_by_user_id", 7, expected_payload(first_name="Updated"))
    ]


@pytest.mark.asyncio
async def test_delete_profile_by_id_returns_no_content_for_owner(
    client, override_manager, monkeypatch
):
    manager = override_manager(StubProfileManager())
    monkeypatch.setattr("app.routes.profiles_routes.get_current_user_id", lambda _: 7)

    response = await client.delete("/api/profile/me")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    assert manager.calls == [("delete_profile_by_user_id", 7)]
