import httpx

from config import settings


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
    ) -> None:
        response = await self.client.get(
            path,
            params={"id": reference_id},
        )
        response.raise_for_status()

        if not response.json()["items"]:
            raise ValueError(f"Reference with id={reference_id} not found")

    async def check_city_exists(self, city_id: int) -> None:
        await self._check_reference_exists("/api/locations/references/cities", city_id)

    async def check_country_exists(self, country_id: int) -> None:
        await self._check_reference_exists(
            "/api/locations/references/countries", country_id
        )

    async def check_location_exists(self, location_id: int) -> None:
        response = await self.client.get(f"/api/locations/{location_id}")
        response.raise_for_status()

    async def close(self) -> None:
        await self.client.aclose()
