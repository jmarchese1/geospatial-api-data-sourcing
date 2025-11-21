"""HTTP client wrapper for the Geoapify Places API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence

import requests
from requests import Response, Session
from requests.exceptions import RequestException

from .config import GeoapifySettings, load_settings
from .exceptions import (
    GeoapifyApiError,
    GeoapifyAuthorizationError,
    GeoapifyClientValidationError,
    GeoapifyRequestError,
)
from .models import Business, businesses_from_feature_collection


DEFAULT_TIMEOUT = 10  # seconds


@dataclass
class PlacesQuery:
    """Represents the immutable parameters for a Places API call."""

    latitude: float
    longitude: float
    radius_m: int
    categories: Sequence[str] | None = None
    limit: int = 20
    language: str | None = None


class GeoapifyPlacesClient:
    """Simple wrapper to perform Geoapify Places lookups."""

    def __init__(
        self,
        settings: GeoapifySettings | None = None,
        *,
        session: Session | None = None,
        timeout: int | float = DEFAULT_TIMEOUT,
    ) -> None:
        self.settings = settings or load_settings()
        self.session = session or requests.Session()
        self.timeout = timeout

    def search_businesses(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_m: int,
        categories: Sequence[str] | None = None,
        limit: int = 20,
        language: str | None = None,
        extra_params: Mapping[str, Any] | None = None,
    ) -> List[Business]:
        """Query the Places API and return normalized :class:`Business` results."""

        query = PlacesQuery(
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
            categories=categories,
            limit=limit,
            language=language,
        )
        params = self._build_params(query, extra_params)
        response = self._perform_request(params)
        payload = self._parse_json_body(response)
        return businesses_from_feature_collection(payload)

    def _build_params(
        self, query: PlacesQuery, extra_params: Mapping[str, Any] | None
    ) -> Dict[str, Any]:
        if query.radius_m <= 0:
            raise GeoapifyClientValidationError("radius_m must be positive")
        if query.limit <= 0:
            raise GeoapifyClientValidationError("limit must be positive")

        params: Dict[str, Any] = {
            "apiKey": self.settings.api_key,
            "limit": query.limit,
            "filter": f"circle:{query.longitude},{query.latitude},{int(query.radius_m)}",
            "bias": f"proximity:{query.longitude},{query.latitude}",
        }
        if query.categories:
            params["categories"] = ",".join(query.categories)
        if query.language:
            params["lang"] = query.language
        if extra_params:
            params.update(extra_params)
        return params

    def _perform_request(self, params: Mapping[str, Any]) -> Response:
        try:
            response = self.session.get(
                self.settings.base_url, params=params, timeout=self.timeout
            )
        except RequestException as exc:
            raise GeoapifyRequestError(str(exc)) from exc

        if response.status_code == 401:
            raise GeoapifyAuthorizationError("API key rejected by Geoapify")

        if response.status_code >= 400:
            message = _extract_error_message(response)
            raise GeoapifyApiError(response.status_code, message)

        return response

    @staticmethod
    def _parse_json_body(response: Response) -> Mapping[str, Any]:
        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise GeoapifyApiError(
                response.status_code, "Geoapify returned invalid JSON"
            ) from exc


def _extract_error_message(response: Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return payload.get("message") or payload.get("error") or str(payload)
    except json.JSONDecodeError:
        pass
    return response.text or f"HTTP {response.status_code}"


__all__ = ["GeoapifyPlacesClient", "PlacesQuery"]
