from geoapify_places.models import (
    Business,
    business_from_feature,
    businesses_from_feature_collection,
)


def sample_feature() -> dict:
    return {
        "properties": {
            "place_id": "demo",
            "name": "Coffee Shop",
            "lat": 40.0,
            "lon": -70.0,
            "categories": ["commercial", "catering", "cafe"],
            "address_line1": "123 Main St",
            "address_line2": "Suite 5",
            "city": "Townsville",
            "state": "TS",
            "postcode": "12345",
            "country": "Wonderland",
            "formatted": "123 Main St, Townsville",
            "website": "https://example.com",
            "phone": "+1 555-0100",
            "distance": 25,
        },
        "geometry": {"type": "Point", "coordinates": [-70.0, 40.0]},
    }


def test_business_from_feature_extracts_expected_fields():
    business = business_from_feature(sample_feature())
    assert isinstance(business, Business)
    assert business.place_id == "demo"
    assert business.name == "Coffee Shop"
    assert business.latitude == 40.0 and business.longitude == -70.0
    assert "cafe" in business.categories
    assert business.formatted_address == "123 Main St, Townsville"
    assert business.website == "https://example.com"
    assert business.distance_meters == 25


def test_businesses_from_feature_collection_skips_invalid_entries():
    data = {"features": [sample_feature(), {"properties": {}, "geometry": {}}]}
    businesses = businesses_from_feature_collection(data)
    assert len(businesses) == 1
    assert businesses[0].place_id == "demo"


def test_business_to_dict_serializes_and_optionally_includes_raw():
    business = business_from_feature(sample_feature())
    data = business.to_dict()
    assert "raw" not in data
    assert data["place_id"] == "demo"

    data_with_raw = business.to_dict(include_raw=True)
    assert "raw" in data_with_raw
    assert data_with_raw["raw"]["properties"]["name"] == "Coffee Shop"
