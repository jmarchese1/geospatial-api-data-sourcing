from unittest.mock import Mock

import pytest
from requests import Response
from requests.exceptions import RequestException

from geoapify_places.client import GeoapifyPlacesClient
from geoapify_places.config import GeoapifySettings
from geoapify_places.exceptions import (
    GeoapifyApiError,
    GeoapifyClientValidationError,
    GeoapifyRequestError,
)


def _make_response(status: int = 200, payload: dict | None = None) -> Response:
    response = Mock(spec=Response)
    response.status_code = status
    response.text = "error"
    response.json.return_value = payload or {"features": []}
    return response


def test_search_businesses_returns_parsed_business(monkeypatch):
    settings = GeoapifySettings(api_key="demo-key")
    session = Mock()
    payload = {
        "features": [
            {
                "properties": {
                    "place_id": "demo",
                    "name": "Shop",
                    "lat": 10,
                    "lon": 20,
                    "categories": ["commercial"],
                },
                "geometry": {"coordinates": [20, 10]},
            }
        ]
    }
    session.get.return_value = _make_response(payload=payload)
    client = GeoapifyPlacesClient(settings=settings, session=session)

    businesses = client.search_businesses(
        latitude=10, longitude=20, radius_m=500, limit=1, categories=["commercial"]
    )

    assert len(businesses) == 1
    assert businesses[0].name == "Shop"
    args, kwargs = session.get.call_args
    assert kwargs["params"]["apiKey"] == "demo-key"
    assert kwargs["params"]["filter"] == "circle:20,10,500"


def test_search_businesses_validates_radius():
    settings = GeoapifySettings(api_key="demo-key")
    client = GeoapifyPlacesClient(settings=settings, session=Mock())
    with pytest.raises(GeoapifyClientValidationError):
        client.search_businesses(latitude=0, longitude=0, radius_m=0)


def test_search_businesses_raises_for_http_error():
    settings = GeoapifySettings(api_key="demo-key")
    session = Mock()
    session.get.return_value = _make_response(status=500, payload={"message": "fail"})
    client = GeoapifyPlacesClient(settings=settings, session=session)

    with pytest.raises(GeoapifyApiError):
        client.search_businesses(latitude=0, longitude=0, radius_m=100)


def test_search_businesses_handles_network_errors():
    settings = GeoapifySettings(api_key="demo-key")
    session = Mock()
    session.get.side_effect = RequestException("boom")
    client = GeoapifyPlacesClient(settings=settings, session=session)

    with pytest.raises(GeoapifyRequestError):
        client.search_businesses(latitude=0, longitude=0, radius_m=100)

