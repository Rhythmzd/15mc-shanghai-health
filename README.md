# 15MC Shanghai Health

This repository supports the graduate project "The 15-Minute Shanghai Project" with Track A: Healthy Lifestyle and Sport.

The project asks a practical urban question:

> Where in Shanghai can residents reach everyday services, sport facilities, green space, healthy food, and supportive active-travel environments within 15 minutes?

## Project Scope

The brief does not provide the six universal baseline indicators. This project therefore defines a transparent baseline from the 15-minute city literature, Shanghai 15-minute community life circle studies, and data availability.

Baseline indicators:

1. Food and daily retail
2. Primary healthcare
3. Education and childcare
4. Public open space
5. Public transport access
6. Civic and community services

Track A indicators:

1. Sport and leisure facility access
2. Green/outdoor access
3. Cycling environment
4. Healthy food access
5. Environmental quality proxy

## Deliverables

- `notebooks/01_data_collection.ipynb`: source inventory, validation, provenance, and 829-word literature review.
- `notebooks/02_grid_isochrones.ipynb`: 2020 built-up-area 500 m grid, four-mode 15-minute accessibility, spatial joins, and cached grid output.
- `notebooks/03_scoring_h3.ipynb`: baseline scoring, Track A scoring, H3 resolution 8 aggregation, and GeoJSON export.
- `scripts/build_outputs.py`: reproducible raw-data-to-H3 pipeline used by the notebooks and web app.
- `scripts/poi_2024.py`: chunked loader and category filter for the `POI 2024` Shanghai CSV package.
- `app/`: static web application source code.
- `docs/`: methodology, data source log, and Trello sprint plan.

Generated outputs:

- `data/processed/shanghai_500m_health_grid.parquet`: 18,653 grid cells.
- `data/output/shanghai_health_h3_r8.geojson`: full H3 analysis layer, 8,664 H3 cells.
- `app/data/shanghai_health_h3_r8.geojson`: lightweight web layer.
- `data/output/summary.json`: run metadata, source counts, and limitations.

## POI Sources

The project now prefers the classified CSV package in:

```text
data/raw/POI 2024/csv格式/已分类
```

when it is available. This source is used to build the main amenity groups for:

- sport and leisure
- healthy food
- scenic/open-space support
- transit-supporting POIs
- healthcare
- education
- civic/public services

The old `SHANGHAI_POI_SHP_DIR` shapefile workflow remains as a fallback only.

## Run

Build outputs from raw data:

```powershell
python scripts/build_outputs.py
```

Run the web app locally:

```powershell
python -m http.server 5173 -d app
```

Open `http://localhost:5173`.

## Default Scoring

The official composite score gives priority to walking and cycling, because the 15-minute city concept is not car-oriented.

- Baseline score: six universal indicators with mode-specific 15-minute catchments.
- Track A score: healthy lifestyle and sport indicators.
- Composite score: `0.60 * baseline_score + 0.40 * health_score`.

Mode catchments are modelled as walking 1.2 km, cycling 3.5 km, transit 2.5 km, and car 5 km. The supplied road parquet is used for cycling environment and major-road environmental context.

## Repository Hygiene

Do not commit:

- API keys
- `.env` files
- private tokens
- large raw datasets
- cached route responses if the data license does not allow redistribution

Use `data/raw/` for original data, `data/processed/` for cleaned intermediate files, and `data/output/` for final web-ready GeoJSON.
