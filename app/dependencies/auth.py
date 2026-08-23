import logging

from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


def get_current_user_id(request: Request) -> int:
    user = getattr(request.state, "user", None)
    if not isinstance(user, dict):
        logger.warning(
            f"request.state.user Не является словарем. Type: {type(user)}. data: {user}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    user_id = user.get("id")
    logger.info("ID пользователя %s", user_id)
    if user_id in (None, ""):
        logger.warning(f"sub отсутствует в user_data. Type {type(user)}. data: {user}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    try:
        return int(user_id)
    except (TypeError, ValueError) as exc:
        logger.exception(
            f"Значение user_id не удалось преобразовать в int. data: {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        ) from exc
