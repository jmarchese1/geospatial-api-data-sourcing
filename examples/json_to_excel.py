"""Convert sweep JSON output into an Excel workbook."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from geoapify_places import export_to_excel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Geoapify sweep JSON output into an Excel file."
    )
    parser.add_argument(
        "input_json",
        type=Path,
        help="Path to the JSON file produced by the sweep script.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Destination .xlsx path (defaults to replacing .json with .xlsx).",
    )
    parser.add_argument(
        "--sheet-name",
        type=str,
        default="Businesses",
        help="Worksheet title inside the Excel workbook.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input_json.exists():
        raise SystemExit(f"Input file not found: {args.input_json}")

    records = json.loads(args.input_json.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise SystemExit("Input JSON must be a list of business records")

    output = args.output or args.input_json.with_suffix(".xlsx")
    export_to_excel(records, output, sheet_name=args.sheet_name)
    print(f"Wrote {len(records)} rows to {output}")


if __name__ == "__main__":
    main()

