"""Sweep Geoapify Places queries across predefined coordinate grids."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Sequence

from geoapify_places import GeoapifyPlacesClient, read_sweep_points, sweep_businesses

STATE_POINT_FILES = {
    "north_carolina": Path("data/points_north_carolina.csv"),
    "texas": Path("data/points_texas.csv"),
    "south_carolina": Path("data/points_south_carolina.csv"),
}
DEFAULT_STATE = "north_carolina"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query Geoapify Places across one or more coordinate grids."
    )
    parser.add_argument(
        "--points-file",
        type=Path,
        default=None,
        help="CSV containing latitude,longitude,radius_m[,label] columns. "
        "Leave unset to use a predefined state grid (see --state).",
    )
    parser.add_argument(
        "--state",
        dest="states",
        choices=sorted(STATE_POINT_FILES.keys()),
        action="append",
        help="Choose one of the predefined coordinate grids. "
        "Use multiple times to combine states in a single run.",
    )
    parser.add_argument(
        "--categories",
        type=str,
        default="commercial,service",
        help="Comma-separated Geoapify category filters.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of rows per API call (Geoapify max 500).",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Optional Geoapify language code.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Where to write the merged JSON results (defaults to <state>_businesses.json).",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Include the raw Geoapify payload in the output file.",
    )
    return parser.parse_args()


def parse_categories(value: str | None) -> Sequence[str] | None:
    if not value:
        return None
    categories = [item.strip() for item in value.split(",") if item.strip()]
    return categories or None


def main() -> None:
    args = parse_args()
    validate_args(args)
    client = GeoapifyPlacesClient()
    point_files = resolve_point_files(args)
    points: List = []
    for file_path in point_files:
        points.extend(read_sweep_points(file_path))
    categories = parse_categories(args.categories)

    businesses = sweep_businesses(
        client,
        points,
        categories=categories,
        limit=args.limit,
        language=args.language,
    )

    serialized = [business.to_dict(include_raw=args.include_raw) for business in businesses]
    output_path = determine_output_path(args)
    output_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")

    print(
        f"Collected {len(serialized)} unique businesses from {len(points)} points "
        f"and wrote them to {output_path}"
    )


def validate_args(args: argparse.Namespace) -> None:
    if args.states and args.points_file:
        raise SystemExit("Use either --state or --points-file, not both.")


def resolve_point_files(args: argparse.Namespace) -> List[Path]:
    if args.states:
        return [STATE_POINT_FILES[state] for state in args.states]
    if args.points_file:
        return [args.points_file]
    return [STATE_POINT_FILES[DEFAULT_STATE]]


def determine_output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return args.output
    if args.states:
        if len(args.states) == 1:
            base = args.states[0]
        else:
            base = "_".join(args.states)
        return Path(f"{base}_businesses.json")
    if args.points_file:
        return Path(f"{args.points_file.stem}_businesses.json")
    return Path(f"{DEFAULT_STATE}_businesses.json")


if __name__ == "__main__":
    main()
