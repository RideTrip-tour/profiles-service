from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


async def _update_model[T](
    db: AsyncSession,
    obj: T,
    payload: BaseModel,
) -> T:

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(obj, key, value)

    await db.commit()
    await db.refresh(obj)

    return obj
