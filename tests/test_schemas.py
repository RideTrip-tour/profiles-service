from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.admin_schemas import ProfileCreate as AdminProfileCreate
from app.schemas.admin_schemas import ProfileUpdate as AdminProfileUpdate
from app.schemas.profiles_schemas import ProfileResponse


def make_profile(**overrides):
    profile = {
        "id": 1,
        "user_id": 7,
        "role": "user",
        "first_name": "Ann",
        "last_name": None,
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
    profile.update(overrides)
    return profile


def test_profile_response_accepts_orm_attributes():
    profile = SimpleNamespace(**make_profile(first_name="Ann"))

    response = ProfileResponse.model_validate(profile)

    assert response.id == 1
    assert response.user_id == 7
    assert response.first_name == "Ann"


def test_admin_profile_create_requires_positive_user_id():
    with pytest.raises(ValidationError):
        AdminProfileCreate(first_name="Ann")

    with pytest.raises(ValidationError):
        AdminProfileCreate(user_id=0, first_name="Ann")

    assert AdminProfileCreate(user_id=7, first_name="Ann").user_id == 7


def test_admin_profile_update_rejects_user_id():
    with pytest.raises(ValidationError):
        AdminProfileUpdate(user_id=8, first_name="Ann")
