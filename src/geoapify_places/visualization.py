"""Visualization helpers for Geoapify business datasets."""

from __future__ import annotations

from typing import Iterable, List, Mapping, Sequence, Tuple


def collect_coordinates(
    records: Sequence[Mapping[str, object]],
    *,
    lat_key: str = "latitude",
    lon_key: str = "longitude",
) -> List[Tuple[float, float]]:
    """
    Extract `(lat, lon)` pairs from JSON-like records.

    Entries missing coordinates (or containing invalid values) are skipped so
    visualization layers (heatmaps, scatter plots, etc.) can consume the data
    without extra validation code.
    """

    coordinates: List[Tuple[float, float]] = []
    for record in records:
        lat = _to_float(record.get(lat_key))
        lon = _to_float(record.get(lon_key))
        if lat is None or lon is None:
            continue
        coordinates.append((lat, lon))
    return coordinates


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


__all__ = ["collect_coordinates"]

