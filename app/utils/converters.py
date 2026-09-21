import logging
from typing import Any

logger = logging.getLogger(__name__)


def convert_value_to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        logger.exception(f"Значение не удалось преобразовать в int. data: {value}")
        return None
