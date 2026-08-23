from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfileBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    age: int | None = None
    about_me: str | None = None
    activities: list[str] = Field(
        default_factory=list,
        description="External activity identifiers from activities service",
    )
    country: str | None = None
    city: str | None = None
    citizenship: str | None = None
    currency: str | None = None
    # Времено отключено по просьбе тестеров. До подключения бакета
    # avatar_url: Optional[str] = None


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
