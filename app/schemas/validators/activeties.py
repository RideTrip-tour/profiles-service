from typing import Annotated

from pydantic import Field

from app.schemas.constants import MAX_LEN_ACTIVITY, MIN_LEN_ACTIVITY

Activity = Annotated[
    str, Field(min_length=MIN_LEN_ACTIVITY, max_length=MAX_LEN_ACTIVITY)
]


def normalize_activities(activities: list[Activity]) -> list[str]:
    """Нормализует значения активностей."""
    return [activity.strip().casefold() for activity in activities]


def validate_activities(activities: list[Activity]) -> list[Activity]:
    """Проверяет уникальность активностей без учёта регистра и пробелов."""
    normalized_activities = normalize_activities(activities)
    if len(normalized_activities) != len(set(normalized_activities)):
        raise ValueError("Activities must be unique")
    return activities
