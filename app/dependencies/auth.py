import logging

from fastapi import HTTPException, Request, status

from app.db.models import Profile
from app.utils.converters import convert_value_to_int
from app.utils.validators import require_or_unauthorized

logger = logging.getLogger(__name__)


def _get_current_id_form_state(request: Request, key: str) -> int:
    user = getattr(request.state, "user", None)
    if not isinstance(user, dict):
        logger.warning(
            "Invalid request.state.user type: %s",
            type(user).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    current_id = user.get(key)
    if current_id in (None, ""):
        logger.warning("Missing required field '%s' in request.state.user", key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return require_or_unauthorized(convert_value_to_int(current_id))


def get_current_user_id(request: Request) -> int:
    return _get_current_id_form_state(request, "id")


def get_current_profile_id(request: Request) -> int:
    return _get_current_id_form_state(request, "profile_id")


def can_view_profile(request: Request, profile: Profile) -> bool:
    current_user_id = get_current_user_id(request)

    if current_user_id != profile.user_id and not profile.settings.show_profile:
        logger.info(
            "Profile is hidden: current_user_id=%s requested_user_id=%s",
            current_user_id,
            profile.user_id,
        )
        return False
    return True
