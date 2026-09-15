from fastapi import HTTPException, status


def require_or_unauthorized(value: int | None) -> int:
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return value
