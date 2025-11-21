"""Data structures for normalized business information."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class Business:
    """Represents a convenient slice of the Geoapify Places response."""

    place_id: str
    name: str | None
    latitude: float
    longitude: float
    categories: Tuple[str, ...]
    address_line1: str | None
    address_line2: str | None
    city: str | None
    state: str | None
    postcode: str | None
    country: str | None
    formatted_address: str | None
    website: str | None
    phone: str | None
    distance_meters: float | None
    raw: Mapping[str, Any] = field(repr=False)

    def to_dict(self, include_raw: bool = False) -> Dict[str, Any]:
        """Serialize the business into a JSON-friendly dict."""

        data: Dict[str, Any] = {
            "place_id": self.place_id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "categories": list(self.categories),
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "city": self.city,
            "state": self.state,
            "postcode": self.postcode,
            "country": self.country,
            "formatted_address": self.formatted_address,
            "website": self.website,
            "phone": self.phone,
            "distance_meters": self.distance_meters,
        }
        if include_raw:
            data["raw"] = self.raw
        return data


def business_from_feature(feature: Mapping[str, Any]) -> Business:
    """Convert a single GeoJSON feature into a :class:`Business`."""

    props = dict(feature.get("properties") or {})
    geometry = feature.get("geometry") or {}
    lon, lat = _extract_coordinates(props, geometry)

    place_id = str(
        props.get("place_id")
        or props.get("datasource", {}).get("raw", {}).get("id")
        or props.get("datasource", {}).get("raw", {}).get("osm_id")
        or props.get("name")
        or f"feature-{hash(str(feature))}"
    )

    categories = _normalize_categories(props)

    return Business(
        place_id=place_id,
        name=props.get("name"),
        latitude=lat,
        longitude=lon,
        categories=categories,
        address_line1=props.get("address_line1"),
        address_line2=props.get("address_line2"),
        city=props.get("city"),
        state=props.get("state"),
        postcode=props.get("postcode"),
        country=props.get("country"),
        formatted_address=props.get("formatted"),
        website=props.get("website"),
        phone=props.get("phone"),
        distance_meters=_normalize_float(props.get("distance")),
        raw=feature,
    )


def businesses_from_feature_collection(payload: Mapping[str, Any]) -> List[Business]:
    """Parse a Geoapify Places response payload into :class:`Business` items."""

    features = payload.get("features") or []
    businesses = []
    for feature in features:
        try:
            businesses.append(business_from_feature(feature))
        except Exception:
            # Skip malformed features but keep the raw payload for debugging later.
            continue
    return businesses


def _extract_coordinates(
    props: Mapping[str, Any], geometry: Mapping[str, Any]
) -> Tuple[float, float]:
    lon = _normalize_float(props.get("lon"))
    lat = _normalize_float(props.get("lat"))
    coords = geometry.get("coordinates")

    if lat is None or lon is None:
        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
            lon = _normalize_float(coords[0])
            lat = _normalize_float(coords[1])

    if lat is None or lon is None:
        raise ValueError("Feature missing coordinates")

    return lon, lat


def _normalize_categories(props: Mapping[str, Any]) -> Tuple[str, ...]:
    categories: Sequence[str] | None = props.get("categories")
    if not categories and props.get("category"):
        categories = [props["category"]]

    return tuple(str(category) for category in categories or ())


def _normalize_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


__all__ = ["Business", "business_from_feature", "businesses_from_feature_collection"]
