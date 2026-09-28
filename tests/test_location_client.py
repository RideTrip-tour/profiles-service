import httpx
import pytest


@pytest.mark.asyncio
async def test_check_city_exists_does_not_raise_for_existing_city(
    location_client,
    monkeypatch,
):

    async def fake_request(method, path, params, headers):
        request = httpx.Request(
            method,
            f"http://test{path}",
        )
        return httpx.Response(
            200,
            json={"items": [{"id": 10}]},
            request=request,
        )

    monkeypatch.setattr(location_client.client, "request", fake_request)

    await location_client.check_city_exists(10)


@pytest.mark.asyncio
async def test_check_city_exists_raises_value_error_for_missing_city(
    location_client,
    monkeypatch,
):
    async def fake_request(method, path, params, headers):
        request = httpx.Request(
            method,
            f"http://test{path}",
        )
        return httpx.Response(
            200,
            json={"items": []},
            request=request,
        )

    monkeypatch.setattr(location_client.client, "request", fake_request)

    with pytest.raises(
        ValueError,
        match="Reference with id=10 not found",
    ):
        await location_client.check_city_exists(10)


@pytest.mark.asyncio
async def test_check_location_exists_raises_http_error_for_missing_location(
    location_client,
    monkeypatch,
):
    async def fake_request(method, path, params, headers):
        request = httpx.Request(
            method,
            f"http://test{path}",
        )
        return httpx.Response(
            404,
            request=request,
        )

    monkeypatch.setattr(location_client.client, "request", fake_request)

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await location_client.check_location_exists(10)

    assert exc_info.value.response.status_code == 404
