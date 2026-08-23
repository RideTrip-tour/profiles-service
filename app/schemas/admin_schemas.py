from pydantic import Field

from app.schemas.profiles_schemas import ProfileBase, ProfileResponse, ProfileUpdate

__all__ = ["ProfileBase", "ProfileCreate", "ProfileResponse", "ProfileUpdate"]


class ProfileCreate(ProfileBase):
    user_id: int = Field(gt=0)
