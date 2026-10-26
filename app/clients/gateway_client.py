import logging

from initial_client import InitialClient
from internal_middleware.context import user_claims

from app.middlerware.context import request_id_var
from config import settings

logger = logging.getLogger(__name__)


class GatewayClient(InitialClient):
    def __init__(self):
        super().__init__(
            base_url=settings.gateway_url,
            service_id=settings.service_id,
            service_token=settings.service_token,
            gateway_name=settings.gateway_name,
            access_token_expire_sec=settings.access_token_expire_sec,
            jwt_secret=settings.jwt_secret,
            timeout=10.0,
        )

    def _get_user_context(self) -> str:
        return self._build_user_context(user_claims.get())

    async def _check_reference_exists(
        self,
        path: str,
        reference_id: int,
    ) -> None:
        response = await self.request(
            method="GET",
            path=path,
            user_context=self._get_user_context(),
            params={"id": reference_id},
            request_id=request_id_var.get(),
        )

        items = response.json()["items"]

        if not any(item["id"] == reference_id for item in items):
            logger.warning(
                "Gateway reference not found: path=%s, reference_id=%s",
                path,
                reference_id,
            )
            raise ValueError(f"Reference with id={reference_id} not found")

    async def check_city_exists(
        self,
        city_id: int,
    ) -> None:
        await self._check_reference_exists(
            "/api/locations/references/cities",
            city_id,
        )

    async def check_country_exists(
        self,
        country_id: int,
    ) -> None:
        await self._check_reference_exists(
            "/api/locations/references/countries",
            country_id,
        )

    async def check_location_exists(
        self,
        location_id: int,
    ) -> None:
        await self.request(
            method="GET",
            user_context=self._get_user_context(),
            path=f"/api/locations/{location_id}",
            request_id=request_id_var.get(),
        )

    async def delete_current_user(self) -> None:
        await self.request(
            method="DELETE",
            user_context=self._get_user_context(),
            path="/api/auth/me",
            request_id=request_id_var.get(),
        )
