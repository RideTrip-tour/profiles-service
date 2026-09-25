from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi import status

from tests.conftest import INVALID_PROFILE_FIELDS


def expected_payload(**overrides):
    payload = {
        "first_name": None,
        "last_name": None,
        "phone_number": None,
        "birth_date": None,
        "about_me": None,
        "activities": [],
        "country_id": None,
        "city_id": None,
        "citizenship": None,
        "currency": None,
    }
    payload.update(overrides)
    return payload


class StubProfileManager:
    def __init__(self, profile_settings=None):
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
            "country_id": None,
            "city_id": None,
            "citizenship": None,
            "currency": None,
            "created_at": datetime(2024, 1, 1, tzinfo=UTC),
            "updated_at": datetime(2024, 1, 1, tzinfo=UTC),
        }
        self.profile_settings = profile_settings

    async def create_profile(self, user_id, payload):
        self.calls.append(("create_profile", user_id, payload.model_dump()))
        return self.profile

    async def get_profile_by_user_id(self, user_id):
        self.calls.append(("get_profile_by_user_id", user_id))

        profile_data = {
            **self.profile,
            "user_id": user_id,
        }
        return SimpleNamespace(
            **profile_data,
            settings=self.profile_settings,
            favorites=[
                SimpleNamespace(
                    location_id=10,
                    created_at=datetime(2024, 1, 1, tzinfo=UTC),
                ),
                SimpleNamespace(
                    location_id=20,
                    created_at=datetime(2024, 1, 2, tzinfo=UTC),
                ),
            ],
        )

    async def update_profile_by_user_id(self, user_id, payload):
        self.calls.append(("update_profile_by_user_id", user_id, payload.model_dump()))
        return {**self.profile, **payload.model_dump(exclude_unset=True)}

    async def delete_profile_by_user_id(self, user_id):
        self.calls.append(("delete_profile_by_user_id", user_id))

    async def get_favorite_location(self, user_id):
        self.calls.append(("get_favorite_location", user_id))
        return [
            SimpleNamespace(
                location_id=10,
                created_at=datetime(2024, 1, 1, tzinfo=UTC),
            ),
            SimpleNamespace(
                location_id=20,
                created_at=datetime(2024, 1, 2, tzinfo=UTC),
            ),
        ]

    async def add_favorite_location(self, user_id, location_id):
        self.calls.append(("add_favorite_location", user_id, location_id))
        return SimpleNamespace(
            location_id=location_id,
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
        )

    async def delete_favorite_location(self, user_id, location_id):
        self.calls.append(("delete_favorite_location", user_id, location_id))

    async def get_profile_settings(self, profile_id):
        self.calls.append(("get_profile_settings", profile_id))
        return self.profile_settings

    async def update_profile_settings(self, profile_id, payload):
        self.calls.append(
            (
                "update_profile_settings",
                profile_id,
                payload.model_dump(exclude_unset=True),
            )
        )

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(self.profile_settings, field, value)

        return self.profile_settings

    async def get_profile_id_or_raise(self, user_id):
        self.calls.append(("get_profile_id_or_raise", user_id))
        return 8

    async def get_show_profile(self, profile_id):
        self.calls.append(("get_show_profile", profile_id))
        return self.profile_settings.show_profile


@pytest.mark.asyncio
async def test_create_profile_uses_current_user_id(
    client, override_manager, monkeypatch
):
    manager = override_manager(StubProfileManager())
    monkeypatch.setattr("app.routes.profiles_routes.get_current_user_id", lambda _: 7)

    response = await client.post("/api/profile/create", json={"first_name": "Ann"})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["user_id"] == 7
    assert manager.calls == [("create_profile", 7, expected_payload(first_name="Ann"))]


@pytest.mark.asyncio
async def test_get_profile_by_id_returns_forbidden_for_another_user(
    client, override_manager, monkeypatch
):
    manager = override_manager(StubProfileManager(SimpleNamespace(show_profile=False)))
    monkeypatch.setattr("app.dependencies.auth.get_current_user_id", lambda _: 7)

    response = await client.get("/api/profile/8")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "User has hidden their profile information"}
    assert manager.calls == [
        ("get_profile_id_or_raise", 8),
        ("get_show_profile", 8),
    ]


@pytest.mark.asyncio
async def test_get_profile_by_id_returns_profile_for_visible_profile(
    client,
    override_manager,
    monkeypatch,
):
    manager = override_manager(
        StubProfileManager(
            SimpleNamespace(show_profile=True),
        )
    )
    monkeypatch.setattr(
        "app.dependencies.auth.get_current_user_id",
        lambda _: 7,
    )
    response = await client.get("/api/profile/8")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1
    assert response.json()["user_id"] == 8
    assert manager.calls == [
        ("get_profile_id_or_raise", 8),
        ("get_show_profile", 8),
        ("get_profile_by_user_id", 8),
    ]


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
@pytest.mark.parametrize("field", ["first_name", "last_name"])
async def test_update_my_profile_uses_current_user_id(
    client, override_manager, monkeypatch, field
):
    manager = override_manager(StubProfileManager())
    monkeypatch.setattr("app.routes.profiles_routes.get_current_user_id", lambda _: 7)

    response = await client.patch("/api/profile/me", json={field: "Updated"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[field] == "Updated"
    assert manager.calls == [
        ("update_profile_by_user_id", 7, expected_payload(**{field: "Updated"}))
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["first_name", "last_name"])
async def test_update_my_profile_returns_422_for_invalid_name(
    client, override_manager, monkeypatch, field
):
    manager = override_manager(StubProfileManager())
    monkeypatch.setattr(
        "app.routes.profiles_routes.get_current_user_id",
        lambda _: 7,
    )
    response = await client.patch(
        "/api/profile/me",
        json={field: "Ann123"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert manager.calls == []


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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("url", "patch_target", "expected_call"),
    [
        (
            "/api/profile/me/favorite-locations",
            "app.routes.profiles_routes.get_current_user_id",
            [("get_favorite_location", 7)],
        ),
        (
            "/api/profile/7/favorite-locations",
            "app.dependencies.auth.get_current_user_id",
            [
                ("get_profile_id_or_raise", 7),
                ("get_show_profile", 8),
                ("get_profile_by_user_id", 7),
            ],
        ),
    ],
)
async def test_get_favorite_locations(
    client, override_manager, monkeypatch, url, patch_target, expected_call
):
    manager = override_manager(StubProfileManager(SimpleNamespace(show_profile=True)))
    monkeypatch.setattr(patch_target, lambda _: 7)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "location_ids": [
            {
                "location_id": 10,
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "location_id": 20,
                "created_at": "2024-01-02T00:00:00Z",
            },
        ]
    }
    assert manager.calls == expected_call


@pytest.mark.asyncio
async def test_get_favorite_locations_by_user_id_returns_forbidden(
    client,
    override_manager,
    monkeypatch,
):
    manager = override_manager(StubProfileManager(SimpleNamespace(show_profile=False)))
    monkeypatch.setattr(
        "app.dependencies.auth.get_current_user_id",
        lambda _: 7,
    )
    response = await client.get(
        "/api/profile/8/favorite-locations",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "User has hidden their information"}
    assert manager.calls == [("get_profile_id_or_raise", 8), ("get_show_profile", 8)]


@pytest.mark.asyncio
async def test_get_favorite_locations_by_user_id_returns_locations_for_visible_profile(
    client,
    override_manager,
    monkeypatch,
):
    manager = override_manager(
        StubProfileManager(
            SimpleNamespace(show_profile=True),
        )
    )
    monkeypatch.setattr(
        "app.dependencies.auth.get_current_user_id",
        lambda _: 7,
    )
    response = await client.get(
        "/api/profile/8/favorite-locations",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "location_ids": [
            {
                "location_id": 10,
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "location_id": 20,
                "created_at": "2024-01-02T00:00:00Z",
            },
        ]
    }
    assert manager.calls == [
        ("get_profile_id_or_raise", 8),
        ("get_show_profile", 8),
        ("get_profile_by_user_id", 8),
    ]


@pytest.mark.asyncio
async def test_add_favorite_location(
    client,
    override_manager,
    monkeypatch,
):
    manager = override_manager(StubProfileManager())
    monkeypatch.setattr(
        "app.routes.profiles_routes.get_current_user_id",
        lambda _: 7,
    )
    response = await client.post(
        "/api/profile/me/favorite-locations",
        json={"location_id": 10},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "location_id": 10,
        "created_at": "2024-01-01T00:00:00Z",
    }
    assert manager.calls == [
        ("add_favorite_location", 7, 10),
    ]


@pytest.mark.asyncio
async def test_delete_favorite_location(
    client,
    override_manager,
    monkeypatch,
):
    manager = override_manager(StubProfileManager())
    monkeypatch.setattr(
        "app.routes.profiles_routes.get_current_user_id",
        lambda _: 7,
    )
    response = await client.delete(
        "/api/profile/me/favorite-locations/10",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    assert manager.calls == [
        ("delete_favorite_location", 7, 10),
    ]


@pytest.mark.asyncio
async def test_get_my_favorite_locations_unauthorized(
    client,
    override_manager,
):
    manager = override_manager(StubProfileManager())
    response = await client.get(
        "/api/profile/me/favorite-locations",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Unauthorized"
    assert manager.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("field, value", INVALID_PROFILE_FIELDS)
async def test_update_my_profile_returns_422_for_too_long_field(
    client, override_manager, monkeypatch, field, value
):
    manager = override_manager(StubProfileManager())

    monkeypatch.setattr(
        "app.routes.profiles_routes.get_current_user_id",
        lambda _: 7,
    )

    response = await client.patch(
        "/api/profile/me",
        json={field: value},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert manager.calls == []


@pytest.mark.asyncio
async def test_get_my_profile_settings_uses_current_profile_id(
    client, override_manager, monkeypatch, profile_settings
):
    manager = override_manager(StubProfileManager(profile_settings))
    monkeypatch.setattr(
        "app.routes.profiles_routes.get_current_profile_id",
        lambda _: 1,
    )
    response = await client.get("/api/profile/me/settings")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "show_profile": profile_settings.show_profile,
        "show_name_in_reviews": profile_settings.show_name_in_reviews,
        "use_activity_for_recommendations": (
            profile_settings.use_activity_for_recommendations
        ),
        "use_profile_for_recommendations": (
            profile_settings.use_profile_for_recommendations
        ),
        "use_city_for_tour_matching": profile_settings.use_city_for_tour_matching,
    }
    assert manager.calls == [
        ("get_profile_settings", 1),
    ]


@pytest.mark.asyncio
async def test_get_my_profile_settings_unauthorized(
    client, override_manager, profile_settings
):
    manager = override_manager(StubProfileManager(profile_settings))
    response = await client.get("/api/profile/me/settings")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Unauthorized"
    assert manager.calls == []


@pytest.mark.asyncio
async def test_update_my_profile_settings_uses_current_profile_id(
    client, override_manager, monkeypatch, profile_settings
):
    manager = override_manager(StubProfileManager(profile_settings))

    monkeypatch.setattr(
        "app.routes.profiles_routes.get_current_profile_id",
        lambda _: 1,
    )
    payload = {
        "show_profile": False,
        "use_city_for_tour_matching": False,
    }

    response = await client.patch(
        "/api/profile/me/settings",
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "show_profile": payload.get("show_profile"),
        "show_name_in_reviews": profile_settings.show_name_in_reviews,
        "use_activity_for_recommendations": (
            profile_settings.use_activity_for_recommendations
        ),
        "use_profile_for_recommendations": (
            profile_settings.use_profile_for_recommendations
        ),
        "use_city_for_tour_matching": payload.get("use_city_for_tour_matching"),
    }
    assert manager.calls == [
        (
            "update_profile_settings",
            1,
            {
                "show_profile": False,
                "use_city_for_tour_matching": False,
            },
        )
    ]


@pytest.mark.asyncio
async def test_update_my_profile_settings_unauthorized(
    client, override_manager, profile_settings
):
    manager = override_manager(StubProfileManager(profile_settings))
    response = await client.patch(
        "/api/profile/me/settings",
        json={"show_profile": False},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Unauthorized"
    assert manager.calls == []
