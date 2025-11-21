"""Small helper script that demonstrates the Geoapify Places client."""

from __future__ import annotations

from geoapify_places import GeoapifyPlacesClient


def main() -> None:
    client = GeoapifyPlacesClient()
    businesses = client.search_businesses(
        latitude=40.7440,
        longitude=-73.9903,
        radius_m=1000,
        categories=["commercial", "service"],
        limit=100,
    )
    for business in businesses:
        print(f"{business.name or 'Unknown'} — {business.formatted_address}")


if __name__ == "__main__":
    main()

