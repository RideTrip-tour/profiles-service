import logging
import time

import httpx

from config import settings

logger = logging.getLogger(__name__)


class LocationClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "client"):
            self.client = httpx.AsyncClient(
                base_url=settings.gateway_url,
                timeout=10.0,
            )

    async def _check_reference_exists(
        self,
        path: str,
        reference_id: int,
        user_context: str | None
    ) -> None:
        response = await self._request(
            method="GET",
            path=path,
            params={"id": reference_id},
            user_context=user_context
        )

        if not response.json()["items"]:
            raise ValueError(f"Reference with id={reference_id} not found")

    async def check_city_exists(self, city_id: int, user_context: str | None) -> None:
        await self._check_reference_exists("/api/locations/references/cities", city_id, user_context=user_context)

    async def check_country_exists(self, country_id: int, user_context:str) -> None:
        await self._check_reference_exists(
            "/api/locations/references/countries", country_id, user_context=user_context
        )

    async def check_location_exists(self, location_id: int, user_context: str | None) -> None:
        await self._request(
            method="GET",
            path=f"/api/locations/{location_id}",
            user_context=user_context
        )

    def _get_headers(self, user_context: str | None) -> dict[str, str]:
        if user_context is None:
            raise ValueError("User context is required")
        return {
            "X-Service-ID": settings.service_id,
            "X-Service-Token": settings.service_token,
            "X-User-Context": user_context
        }

    async def _request(
        self,
        method: str,
        path: str,
        user_context: str | None,
        params: dict[str, int] | None = None,
    ) -> httpx.Response:
        started_at = time.monotonic()

        logger.info(
            "Gateway request started: %s: %s",
            method,
            path,
        )

        try:
            response = await self.client.request(
                method,
                path,
                headers=self._get_headers(user_context),
                params=params,
            )
            elapsed = time.monotonic() - started_at
            logger.info(
                "Gateway request completed: %s: %s -> %s in %s s",
                method,
                path,
                response.status_code,
                elapsed,
            )
            response.raise_for_status()
            return response
        except Exception:
            elapsed = time.monotonic() - started_at

            logger.exception(
                "Gateway request failed: %s: %s in %s s",
                method,
                path,
                elapsed,
            )
            raise

    async def close(self) -> None:
        await self.client.aclose()
