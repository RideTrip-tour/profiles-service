from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


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
    age: Mapped[int | None] = mapped_column(Integer)
    about_me: Mapped[str | None] = mapped_column(Text)
    activities: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default=text("'[]'::json"),
    )
    country: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
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

    def __repr__(self):
        return f"<Profile {self.first_name}: {self.last_name}>"
