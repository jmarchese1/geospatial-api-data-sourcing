from pathlib import Path

import pytest

from geoapify_places.exporters import export_to_csv, export_to_excel, flatten_records


def test_flatten_records_handles_lists_and_dicts():
    records = [
        {"place_id": "1", "categories": ["a", "b"], "raw": {"foo": "bar"}},
        {"place_id": "2", "city": "Raleigh"},
    ]
    headers, rows = flatten_records(records)
    assert "place_id" in headers
    assert "categories" in headers
    assert rows[0][headers.index("categories")] == "a, b"
    raw_value = rows[0][headers.index("raw")]
    assert isinstance(raw_value, str) and '"foo": "bar"' in raw_value


def test_export_to_excel_writes_file(tmp_path: Path):
    records = [
        {"place_id": "1", "name": "Business 1"},
        {"place_id": "2", "name": "Business 2"},
    ]
    output = tmp_path / "businesses.xlsx"
    result_path = export_to_excel(records, output)
    assert result_path == output
    assert output.exists()


def test_export_to_excel_requires_records():
    with pytest.raises(ValueError):
        export_to_excel([], "out.xlsx")


def test_export_to_csv_writes_file(tmp_path: Path):
    records = [
        {"place_id": "1", "name": "Business 1"},
        {"place_id": "2", "name": "Business 2"},
    ]
    output = tmp_path / "businesses.csv"
    result_path = export_to_csv(records, output)
    assert result_path == output
    assert output.exists()


def test_export_to_csv_requires_records():
    with pytest.raises(ValueError):
        export_to_csv([], "out.csv")
