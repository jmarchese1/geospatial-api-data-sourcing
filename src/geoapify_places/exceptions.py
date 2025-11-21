"""Custom exception hierarchy for the Geoapify Places client."""

from __future__ import annotations

from typing import Optional


class GeoapifyPlacesError(Exception):
    """Base exception for all client-related failures."""


class GeoapifyAuthorizationError(GeoapifyPlacesError):
    """Raised when the API rejects our credentials."""


class GeoapifyApiError(GeoapifyPlacesError):
    """Raised for non-successful HTTP responses."""

    def __init__(self, status_code: int, message: Optional[str] = None) -> None:
        self.status_code = status_code
        self.message = message or "Geoapify Places API error"
        super().__init__(f"{self.message} (status={status_code})")


class GeoapifyRequestError(GeoapifyPlacesError):
    """Raised for network/transport errors."""


class GeoapifyClientValidationError(GeoapifyPlacesError):
    """Raised when invalid parameters are passed to the client."""

