# Roads Parquet Notes

File:

```text
data/raw/roads/shanghai-roads-simplified.parquet
```

## What It Is

This is a simplified Shanghai road network stored in Apache Parquet format. Parquet is a compact columnar table format, often used because it reads faster and stores large geospatial tables more efficiently than CSV.

The file appears to contain OSM-style road-edge attributes. Metadata inspection found these fields:

```text
osm_id
highway
level
lanes
width
bicycle
bicycle_safety
foot
foot_safety
max_speed
motorcar
geometry
edge_id
```

## Why It Matters

This file is likely the most useful road-network input for the 15-minute accessibility part of the project. It can support:

- walking network filtering using `foot` and `foot_safety`
- cycling network filtering using `bicycle` and `bicycle_safety`
- car comparison using `motorcar` and `max_speed`
- network distance or travel-time calculations using `geometry`
- edge-based caching through `edge_id`

## How To Read It

Install Parquet support first:

```bash
pip install pyarrow
```

Then in Python:

```python
import geopandas as gpd

roads = gpd.read_parquet("data/raw/roads/shanghai-roads-simplified.parquet")
roads.head()
```

If the geometry is not automatically recognized, inspect the `geometry` column and convert it with Shapely/WKB helpers.

## Project Role

Use this as the preferred local fallback road network when API-based routing is unavailable. It should feed `02_grid_isochrones.ipynb`, especially for walk/bike network accessibility.

## Provenance Notebook

The source workflow is documented in `shanghai-network-extract.ipynb`. That notebook reads a Shanghai OSM PBF with `policosm`, projects the network to EPSG:4576, simplifies the road edges, and exports `shanghai-roads-simplified.parquet`.

It also demonstrates a network-based 15-minute isochrone method:

- compute edge travel times from geometry length
- filter networks by mode
- snap origins to nearest edges
- run Dijkstra search with a 900-second threshold
- convert reachable road edges into an isochrone polygon

See `docs/network_extract_notebook_notes.md` for the detailed summary.
