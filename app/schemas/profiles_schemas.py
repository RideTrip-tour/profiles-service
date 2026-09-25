from datetime import UTC, date, datetime

import pycountry
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .constants import (
    MAX_LEN_ABOUT_ME,
    MAX_LEN_ACTIVITIES,
    MAX_LEN_CITIZENSHIP,
    MAX_LEN_CURRENCY,
    MAX_LEN_NAME,
    MIN_LEN_CITIZENSHIP,
    MIN_LEN_CURRENCY,
    MIN_LEN_NAME,
    MIN_VALUE_CITY,
    MIN_VALUE_COUNTRY,
    PATTERN_NAME,
)
from .validators.phone_number import normalize_phone_number


class ProfileBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(
        default=None,
        min_length=MIN_LEN_NAME,
        max_length=MAX_LEN_NAME,
        pattern=PATTERN_NAME,
    )
    last_name: str | None = Field(
        default=None,
        min_length=MIN_LEN_NAME,
        max_length=MAX_LEN_NAME,
        pattern=PATTERN_NAME,
    )
    phone_number: str | None = None
    birth_date: date | None = Field(default=None, description="")
    about_me: str | None = Field(
        default=None,
        max_length=MAX_LEN_ABOUT_ME,
        description="Произвольная информация о себе.",
    )
    activities: list[str] = Field(
        default_factory=list,
        max_length=MAX_LEN_ACTIVITIES,
        description="External activity identifiers from activities service",
    )
    country_id: int | None = Field(default=None, gt=MIN_VALUE_COUNTRY)
    city_id: int | None = Field(default=None, gt=MIN_VALUE_CITY)
    citizenship: str | None = Field(
        default=None, min_length=MIN_LEN_CITIZENSHIP, max_length=MAX_LEN_CITIZENSHIP
    )
    currency: str | None = Field(
        default=None, min_length=MIN_LEN_CURRENCY, max_length=MAX_LEN_CURRENCY
    )
    # Времено отключено по просьбе тестеров. До подключения бакета
    # avatar_url: Optional[str] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, phone_number: str | None) -> str | None:
        if phone_number is not None:
            return normalize_phone_number(phone_number)
        return None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.upper()
            if not pycountry.currencies.get(alpha_3=value):
                raise ValueError("Invalid currency code")
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: date | None) -> date | None:
        if value is not None:
            age = relativedelta(datetime.now(UTC).date(), value).years
            if age < 18:
                raise ValueError("User must be at least 18 years old")
        return value


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role: str
    created_at: datetime
    updated_at: datetime


class ProfileHiddenResponse(BaseModel):
    detail: str


class FavoriteLocationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location_id: int = Field(gt=0)


class FavoriteLocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_id: int
    created_at: datetime


class FavoriteLocationsResponse(BaseModel):
    location_ids: list[FavoriteLocationResponse]


class ProfileSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    show_profile: bool
    show_name_in_reviews: bool
    use_activity_for_recommendations: bool
    use_profile_for_recommendations: bool
    use_city_for_tour_matching: bool


class ProfileSettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    show_profile: bool | None = None
    show_name_in_reviews: bool | None = None
    use_activity_for_recommendations: bool | None = None
    use_profile_for_recommendations: bool | None = None
    use_city_for_tour_matching: bool | None = None
