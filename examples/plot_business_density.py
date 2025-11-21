"""Create an interactive density map from sweep JSON output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import List, Mapping

import folium
from folium import Map
from folium.plugins import HeatMap, MarkerCluster

from geoapify_places import collect_coordinates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Folium heatmap showing where businesses cluster."
    )
    parser.add_argument(
        "input_json",
        type=Path,
        help="JSON file produced by the sweep script.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("plots/business_density_map.html"),
        help="HTML file to write the interactive map.",
    )
    parser.add_argument(
        "--tiles",
        type=str,
        default="CartoDB positron",
        help="Basemap tiles to use (any Folium-supported tile set).",
    )
    parser.add_argument(
        "--zoom-start",
        type=int,
        default=6,
        help="Initial zoom level for the map.",
    )
    parser.add_argument(
        "--heatmap-radius",
        type=int,
        default=18,
        help="Radius (in pixels) for each point in the heatmap layer.",
    )
    parser.add_argument(
        "--heatmap-blur",
        type=int,
        default=15,
        help="Blur strength for the heatmap layer.",
    )
    parser.add_argument(
        "--include-markers",
        action="store_true",
        help="Overlay marker clusters with popups for each business.",
    )
    parser.add_argument(
        "--center-lat",
        type=float,
        default=None,
        help="Force a specific latitude for map centering (defaults to dataset mean).",
    )
    parser.add_argument(
        "--center-lon",
        type=float,
        default=None,
        help="Force a specific longitude for map centering (defaults to dataset mean).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input_json.exists():
        raise SystemExit(f"Input file not found: {args.input_json}")

    records = json.loads(args.input_json.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise SystemExit("Input JSON must be a list of business records.")

    coordinates = collect_coordinates(records)
    if not coordinates:
        raise SystemExit("No valid latitude/longitude pairs found in the dataset.")

    center_lat = args.center_lat if args.center_lat is not None else mean(lat for lat, _ in coordinates)
    center_lon = args.center_lon if args.center_lon is not None else mean(lon for _, lon in coordinates)

    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=args.zoom_start, tiles=args.tiles)

    heat_data = [[lat, lon] for lat, lon in coordinates]
    HeatMap(
        heat_data,
        radius=args.heatmap_radius,
        blur=args.heatmap_blur,
        max_zoom=18,
    ).add_to(fmap)

    if args.include_markers:
        cluster = MarkerCluster(name="Businesses").add_to(fmap)
        for record in records:
            lat = record.get("latitude")
            lon = record.get("longitude")
            if lat is None or lon is None:
                continue
            popup_text = build_popup(record)
            folium.Marker(
                location=[lat, lon],
                popup=popup_text,
                tooltip=record.get("name") or "Business",
            ).add_to(cluster)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fmap.save(args.output)
    print(f"Wrote interactive density map to {args.output}")


def build_popup(record: Mapping[str, object]) -> str:
    name = record.get("name") or "Unknown business"
    address = record.get("formatted_address") or "Address unavailable"
    categories = record.get("categories") or []
    categories_text = ", ".join(categories) if isinstance(categories, list) else str(categories)
    return f"<b>{name}</b><br/>{address}<br/><i>{categories_text}</i>"


if __name__ == "__main__":
    main()

