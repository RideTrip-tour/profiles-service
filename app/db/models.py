from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

PROFILE_RELATIONSHIP_CASCADE = "all, delete-orphan"


def bool_setting(default: bool = True) -> Mapped[bool]:
    """Создаёт обязательное булево поле настройки со значением по умолчанию."""
    return mapped_column(Boolean, nullable=False, default=default)


class ProfileIdMixin:
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Profile(Base):
    __tablename__ = "profiles"

    __table_args__ = (
        CheckConstraint("user_id > 0", name="ck_profiles_user_id_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, unique=True
    )

    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True)
    birth_date: Mapped[date | None] = mapped_column(Date)
    about_me: Mapped[str | None] = mapped_column(Text)
    activities: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default=text("'[]'::json"),
    )
    country_id: Mapped[int | None] = mapped_column(Integer)
    city_id: Mapped[int | None] = mapped_column(Integer)
    citizenship: Mapped[str | None] = mapped_column(String(100))
    currency: Mapped[str | None] = mapped_column(String(10))
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'user'"),
    )
    avatar_url: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    favorites: Mapped[list["FavoriteLocation"]] = relationship(
        back_populates="profile", cascade=PROFILE_RELATIONSHIP_CASCADE
    )
    devices: Mapped[list["ProfileDevice"]] = relationship(
        back_populates="profile",
        cascade=PROFILE_RELATIONSHIP_CASCADE,
    )
    settings: Mapped["ProfileSettings"] = relationship(
        back_populates="profile", cascade=PROFILE_RELATIONSHIP_CASCADE, uselist=False
    )

    def __repr__(self):
        return f"<Profile {self.first_name}: {self.last_name}>"


class FavoriteLocation(ProfileIdMixin, Base):
    __tablename__ = "favorite_locations"

    __table_args__ = (
        UniqueConstraint(
            "profile_id", "location_id", name="uq_favorite_locations_profile_location"
        ),
    )

    location_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    profile: Mapped[Profile] = relationship(back_populates="favorites")


class ProfileDevice(ProfileIdMixin, Base):
    __tablename__ = "profile_devices"

    device_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    device_name: Mapped[str | None] = mapped_column(String(100))
    platform: Mapped[str | None] = mapped_column(String(100))
    user_agent: Mapped[str | None] = mapped_column(String(512))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    profile: Mapped[Profile] = relationship(back_populates="devices")

    def __repr__(self):
        return (
            f"<ProfileDevice profile_id={self.profile_id} device_id={self.device_id}>"
        )


class ProfileSettings(ProfileIdMixin, Base):
    __tablename__ = "profile_settings"

    show_profile: Mapped[bool] = bool_setting()
    show_name_in_reviews: Mapped[bool] = bool_setting()
    use_activity_for_recommendations: Mapped[bool] = bool_setting()
    use_profile_for_recommendations: Mapped[bool] = bool_setting()
    use_city_for_tour_matching: Mapped[bool] = bool_setting()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    profile: Mapped["Profile"] = relationship(
        back_populates="settings",
    )

    def __repr__(self):
        return f"<ProfileSettings profile_id={self.profile_id}>"
