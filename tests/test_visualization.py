from geoapify_places.visualization import collect_coordinates


def test_collect_coordinates_filters_invalid_values():
    records = [
        {"latitude": 35.0, "longitude": -80.0},
        {"latitude": "34.5", "longitude": "-82.0"},
        {"latitude": None, "longitude": -81.0},
        {"latitude": 36.0, "longitude": "invalid"},
    ]

    coords = collect_coordinates(records)
    assert coords == [(35.0, -80.0), (34.5, -82.0)]

