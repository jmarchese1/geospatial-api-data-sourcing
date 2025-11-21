from pathlib import Path
from typing import List

import pytest

from geoapify_places.models import Business
from geoapify_places.sweeper import SweepPoint, read_sweep_points, sweep_businesses


class DummyClient:
    def __init__(self, responses: List[List[Business]]) -> None:
        self.responses = responses
        self.calls = 0

    def search_businesses(self, **kwargs):
        response = self.responses[self.calls]
        self.calls += 1
        return response


def build_business(place_id: str, *, lat: float = 0.0, lon: float = 0.0) -> Business:
    return Business(
        place_id=place_id,
        name=f"Place {place_id}",
        latitude=lat,
        longitude=lon,
        categories=("commercial",),
        address_line1=None,
        address_line2=None,
        city=None,
        state=None,
        postcode=None,
        country=None,
        formatted_address=None,
        website=None,
        phone=None,
        distance_meters=None,
        raw={"properties": {"place_id": place_id}},
    )


def test_read_sweep_points_parses_csv(tmp_path: Path):
    csv_content = "latitude,longitude,radius_m\n35.0,-80.0,5000\n"
    path = tmp_path / "points.csv"
    path.write_text(csv_content, encoding="utf-8")

    points = read_sweep_points(path)
    assert points == [
        SweepPoint(latitude=35.0, longitude=-80.0, radius_m=5000, label=None)
    ]


def test_read_sweep_points_with_labels(tmp_path: Path):
    csv_content = "latitude,longitude,radius_m,label\n35.0,-80.0,5000,Test City\n"
    path = tmp_path / "points.csv"
    path.write_text(csv_content, encoding="utf-8")

    points = read_sweep_points(path)
    assert points[0].label == "Test City"


def test_sweep_businesses_deduplicates_overlapping_results():
    point = SweepPoint(latitude=35.0, longitude=-80.0, radius_m=5000)
    duplicate_business = build_business("dup")
    client = DummyClient(
        responses=[
            [duplicate_business, build_business("unique")],
            [duplicate_business],
        ]
    )

    businesses = sweep_businesses(client, [point, point])
    assert len(businesses) == 2
    ids = {business.place_id for business in businesses}
    assert ids == {"dup", "unique"}
