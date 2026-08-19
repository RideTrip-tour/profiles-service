from datetime import datetime
from sqlalchemy import CheckConstraint, func, Integer, JSON, String, text, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from typing import Optional


class Profile(Base):
    __tablename__ = "profiles"

    __table_args__ = (
        CheckConstraint("user_id > 0", name="ck_profiles_user_id_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, unique=True
    )

    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    about_me: Mapped[Optional[str]] = mapped_column(Text)
    activities: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default=text("'[]'::json"),
    )
    country: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    citizenship: Mapped[Optional[str]] = mapped_column(String(100))
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'user'"),
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(String)
    favorite_location_ids: Mapped[list[int]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default=text("'[]'::json"),
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Profile {self.first_name}: {self.last_name}>"
