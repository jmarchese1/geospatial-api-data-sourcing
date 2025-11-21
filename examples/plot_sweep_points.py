"""Plot sweep latitude/longitude points for quick visualization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt

from geoapify_places import read_sweep_points


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize the sweep points used for Geoapify Places queries."
    )
    parser.add_argument(
        "--points-file",
        type=Path,
        default=Path("data/points_north_carolina.csv"),
        help="CSV file containing latitude, longitude, radius_m columns.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("plots/north_carolina_sweep.png"),
        help="PNG path to save the plotted points.",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Geoapify Sweep Points",
        help="Custom title for the figure.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the plot interactively after saving.",
    )
    parser.add_argument(
        "--map-geojson",
        type=Path,
        default=Path("data/us_states.geojson"),
        help="GeoJSON file containing polygon outlines (default: US states).",
    )
    parser.add_argument(
        "--state",
        type=str,
        default="North Carolina",
        help="State name to highlight; leave blank to draw all polygons in the file.",
    )
    return parser.parse_args()


def radius_to_degrees(radius_m: int) -> float:
    # Rough conversion; 1 degree ≈ 111 km
    return radius_m / 111_000


def main() -> None:
    args = parse_args()
    sweep_points = read_sweep_points(args.points_file)
    if not sweep_points:
        raise SystemExit("No sweep points to plot.")

    polygons = load_polygons(args.map_geojson, args.state)

    longitudes = [point.longitude for point in sweep_points]
    latitudes = [point.latitude for point in sweep_points]
    colors = range(len(sweep_points))

    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(8, 8))

    if polygons:
        draw_polygons(ax, polygons, highlight_only=bool(args.state))

    sc = ax.scatter(
        longitudes,
        latitudes,
        c=colors,
        cmap="viridis",
        s=140,
        edgecolor="black",
        linewidth=0.8,
        zorder=3,
    )

    for idx, point in enumerate(sweep_points, start=1):
        label_text = point.label or f"Point {idx}"
        label = f"{idx}. {label_text}"
        ax.annotate(
            label,
            (point.longitude, point.latitude),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=8,
            color="#1f1f1f",
            zorder=4,
        )

        radius_deg = radius_to_degrees(point.radius_m)
        circle = plt.Circle(
            (point.longitude, point.latitude),
            radius_deg,
            color="black",
            fill=False,
            alpha=0.25,
            linestyle="--",
            linewidth=0.8,
        )
        ax.add_patch(circle)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(args.title)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_aspect("equal", adjustable="box")

    cbar = fig.colorbar(sc, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label("Point index")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=200, bbox_inches="tight")
    print(f"Saved sweep plot to {args.output}")

    if args.show:
        plt.show()


def load_polygons(path: Path, state_name: str | None) -> List[Tuple[str, List]]:
    if not path.exists():
        print(f"Warning: map file {path} not found; skipping base map.")
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    features = data.get("features", [])
    polygons: List[Tuple[str, List]] = []
    target = state_name.lower().strip() if state_name else None

    for feature in features:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates")
        name = (
            str(feature.get("properties", {}).get("name", "")).lower().strip()
        )
        if target and name != target:
            continue
        polygons.append((geom_type, coords))

    if target and not polygons:
        raise SystemExit(f"State '{state_name}' not found in {path}")

    if not target:
        return polygons

    return polygons


def draw_polygons(ax: plt.Axes, polygons: List[Tuple[str, List]], highlight_only: bool) -> None:
    outline_color = "#8c8c8c"
    highlight_color = "#004c6d"
    for geom_type, coords in polygons:
        rings = []
        if geom_type == "Polygon":
            rings = coords
        elif geom_type == "MultiPolygon":
            for poly in coords:
                rings.extend(poly)
        else:
            continue

        for ring in rings:
            if not ring:
                continue
            xs = [point[0] for point in ring]
            ys = [point[1] for point in ring]
            ax.plot(
                xs,
                ys,
                color=highlight_color if highlight_only else outline_color,
                linewidth=1.0 if highlight_only else 0.6,
                alpha=0.8 if highlight_only else 0.5,
                zorder=1,
            )


if __name__ == "__main__":
    main()
