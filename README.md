Geoapify Places Connector
=========================

This repository contains a lightweight Python connector for the [Geoapify Places API](https://www.geoapify.com/places-api). It ships with environment-aware configuration helpers, an HTTP client that wraps the `/v2/places` endpoint, normalized business models, pytest coverage, and an executable example script.

Repository layout
-----------------

- `src/geoapify_places/config.py` – loads the API key and base URL, optionally parsing a `.env` file.
- `src/geoapify_places/client.py` – wraps HTTP calls, handles auth, validation, and error reporting.
- `src/geoapify_places/models.py` – dataclasses + helpers to normalize business records.
- `examples/query_places.py` – runnable sample that fetches and prints nearby results.
- `examples/sweep_businesses.py` – sweeps multiple latitude/longitude points to merge statewide data.
- `examples/plot_sweep_points.py` – plots the sweep grid so you can visualize coverage.
- `examples/plot_business_density.py` – builds a Folium heatmap/marker map from sweep results.
- `examples/json_to_excel.py` – converts the sweep JSON output into an Excel workbook.
- `examples/json_to_csv.py` – converts the sweep JSON output into a CSV file.
- `tests/` – pytest coverage for the parser and client behavior.
- `.env.example` – template showing how to store `GEOAPIFY_API_KEY` locally (copy it to `.env`).
- `data/points_north_carolina.csv` – coordinate grid + point labels used by the sweep example.
- `data/points_texas.csv` / `data/points_south_carolina.csv` – ready-to-use grids for those states.
- `data/us_states.geojson` – simplified U.S. state boundaries (for plotting backgrounds).

Setup
-----

1. Create your virtual environment (optional but recommended) and install dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

2. Install the package locally so Python can import `geoapify_places` from anywhere:

   ```bash
   pip install -e .
   ```

3. Copy `.env.example` to `.env` and keep the API key inside it (or export `GEOAPIFY_API_KEY` via your shell). The provided key (`2acd4f2ea32f499384767f4067b85d14`) will work for basic experiments.

4. Run the example query to see the connector in action:

   ```bash
   python examples/query_places.py
   ```

5. Import the client in your own modules:

   ```python
   from geoapify_places import GeoapifyPlacesClient

   client = GeoapifyPlacesClient()
   businesses = client.search_businesses(
       latitude=40.7440,
       longitude=-73.9903,
       radius_m=1000,
       categories=["commercial", "service"],
       limit=10,
   )
   for business in businesses:
       print(business.name, business.formatted_address)
   ```

Sweeping a region
-----------------

1. Inspect or edit one of the state CSVs in `data/` (e.g., `points_north_carolina.csv`, `points_texas.csv`, `points_south_carolina.csv`) to tune the latitude/longitude/radius grid. You can add a `label` column per row to describe each point (e.g., city name); the sweep and plotting scripts surface those labels automatically.
2. Execute the sweep helper, which issues one API call per point, merges the responses (by `place_id`), and writes `<state>_businesses.json`. Use `--state` to pick from the built-in grids (optionally repeat for multiple states) or `--points-file` to target a custom CSV:

   ```bash
   python examples/sweep_businesses.py --limit 200 --categories commercial,service,catering
   python examples/sweep_businesses.py --state texas --categories commercial --limit 200
   python examples/sweep_businesses.py --state north_carolina --state south_carolina --limit 200
   python examples/sweep_businesses.py --points-file data/custom_points.csv --limit 200
   ```

3. Pass `--include-raw` if you need Geoapify's original payload for each result. When using `--state`, the script auto-names the output file (`texas_businesses.json`, `north_carolina_south_carolina_businesses.json`, etc.); otherwise use `--output` to set it explicitly.

Visualizing sweep points
------------------------

Create a PNG map of the coordinate grid overlaid on state or nationwide boundaries (circles show each query radius):

```bash
python examples/plot_sweep_points.py --output plots/nc_points.png --title "NC Sweep Grid" --state "North Carolina"
```

Use `--points-file` to plot alternative CSVs, `--state ""` to draw every polygon contained in `--map-geojson`, or `--show` to pop open the interactive window after saving. The default output lives under `plots/north_carolina_sweep.png`.

Exporting sweep JSON to Excel
-----------------------------

After running the sweep script (which produces `north_carolina_businesses.json`), convert the results to Excel with:

```bash
python examples/json_to_excel.py north_carolina_businesses.json --output exports/nc_businesses.xlsx --sheet-name "NC Businesses"
```

The exporter flattens lists (e.g., categories) into comma-separated strings and serializes nested dictionaries as JSON inside the spreadsheet. Change the output path or sheet name as needed.

Exporting sweep JSON to CSV
---------------------------

```bash
python examples/json_to_csv.py north_carolina_businesses.json --output exports/nc_businesses.csv
```

If you omit `--output`, the script writes `north_carolina_businesses.csv` next to the JSON file. CSV export uses the same flattening rules as the Excel helper, turning lists into comma-separated strings and nested objects into JSON blobs.

Business density heatmap
------------------------

Once you have a JSON dataset (from any points file), render an interactive heatmap to see where results cluster:

```bash
python examples/plot_business_density.py north_carolina_businesses.json --output plots/nc_density.html --include-markers --zoom-start 7
```

Open the generated HTML in your browser to explore the hotspots; add `--tiles "Stamen Toner"` or tweak `--heatmap-radius`/`--heatmap-blur` for different looks. Use `--center-lat/--center-lon` if the automatic centering doesn't match your area of interest.

Testing
-------

Run the existing test suite with:

```bash
pytest
```

Next steps
----------

- Expand the client with richer query helpers (text searches, pagination, etc.).
- Add caching or rate-limit guards for production usage.
- Persist normalized business data into the target storage or downstream pipeline.
