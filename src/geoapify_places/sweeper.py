"""Helpers for sweeping multiple locations and merging Geoapify responses."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Mapping, MutableMapping, Sequence

from .client import GeoapifyPlacesClient
from .models import Business


@dataclass(frozen=True)
class SweepPoint:
    """Coordinates + radius for one Geoapify Places query."""

    latitude: float
    longitude: float
    radius_m: int
    label: str | None = None


def read_sweep_points(path: str | Path) -> List[SweepPoint]:
    """
    Parse a CSV file containing latitude/longitude/radius entries.

    Required columns: latitude, longitude, radius_m.
    Optional columns: label (human-friendly name for the point).
    """

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Sweep file not found: {file_path}")

    points: List[SweepPoint] = []
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        required = {"latitude", "longitude", "radius_m"}
        if not required.issubset(fieldnames):
            raise ValueError(
                f"Sweep file {file_path} missing columns: {required - fieldnames}"
            )
        for row in reader:
            try:
                label = row.get("label") if "label" in fieldnames else None
                points.append(
                    SweepPoint(
                        latitude=float(row["latitude"]),
                        longitude=float(row["longitude"]),
                        radius_m=int(float(row["radius_m"])),
                        label=label.strip() if label else None,
                    )
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid sweep row: {row}") from exc

    if not points:
        raise ValueError(f"Sweep file {file_path} did not contain any points")

    return points


def sweep_businesses(
    client: GeoapifyPlacesClient,
    points: Sequence[SweepPoint],
    *,
    categories: Sequence[str] | None = None,
    limit: int = 100,
    language: str | None = None,
    extra_params: Mapping[str, object] | None = None,
) -> List[Business]:
    """Run multiple Geoapify queries and merge the unique businesses."""

    dedup: MutableMapping[str, Business] = {}
    for point in points:
        businesses = client.search_businesses(
            latitude=point.latitude,
            longitude=point.longitude,
            radius_m=point.radius_m,
            categories=categories,
            limit=limit,
            language=language,
            extra_params=extra_params,
        )
        for business in businesses:
            dedup.setdefault(business.place_id, business)

    return list(dedup.values())


__all__ = ["SweepPoint", "read_sweep_points", "sweep_businesses"]
