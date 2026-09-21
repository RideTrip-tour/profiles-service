from fastapi import HTTPException, status


async def check_location_exists(location_id: int) -> None:
    """
    Проверка существования локации.

    TODO: написать HTTP-запрос.
    """

    if location_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
