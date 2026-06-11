# Shanghai Network Extract Notebook Notes

Source notebook:

```text
shanghai-network-extract.ipynb
```

## What It Does

This notebook appears to be the provenance and experiment notebook for:

```text
data/raw/roads/shanghai-roads-simplified.parquet
```

It extracts a Shanghai road network from an OSM `.pbf` file, simplifies the network, exports the simplified edges to Parquet, and then demonstrates a 15-minute isochrone workflow.

## Main Workflow

1. Load `policosm`.
2. Read a Shanghai OSM PBF file:

```python
roads = policosm.classes.roads.Roads(directed=False, country_iso3="chn")
roads.apply_file("shanghai.pbf", locations=True)
```

3. Convert OSM roads to dataframes and project to a metric CRS:

```python
roads.osm_to_dataframes(project_to_meters=True, project_overwrite_epsg=4576)
```

4. Simplify the road network:

```python
roads.processing_simplify()
```

5. Export simplified road edges:

```python
roads.dfe.to_parquet("shanghai-roads-simplified.parquet")
```

## Useful Fields Created or Used

The notebook calculates:

```python
gdf["length_m"] = gdf.geometry.length
gdf["bicycle_time"] = gdf.geometry.length / 3.05
gdf["foot_time"] = gdf.geometry.length / 1.33
gdf["car_time"] = gdf.geometry.length / 8.3
```

Approximate speeds:

| Mode | Speed | Meaning |
| --- | ---: | --- |
| Walk | 1.33 m/s | about 4.8 km/h |
| Bike | 3.05 m/s | about 11.0 km/h |
| Car | 8.3 m/s | about 29.9 km/h |

Mode-specific network filters:

```python
gdf_car = gdf[gdf["level"] >= 3].copy()
gdf_foot = gdf[gdf["foot"] > 0].copy()
gdf_bike = gdf[gdf["bicycle"] > 0].copy()
```

## Isochrone Logic

The notebook demonstrates a route-network isochrone method:

1. Snap an origin point to the nearest road edge using `cKDTree`.
2. Build a graph from edge list columns `u`, `v`, travel time, and `edge_id`.
3. Run Dijkstra search from the origin node.
4. Stop when travel time exceeds `15 * 60` seconds.
5. Mark reachable edges.
6. Cut partially reachable boundary edges.
7. Build an isochrone polygon from reachable road geometry.

This is more defensible than a simple circular buffer because it follows the road network.

## What To Reuse

Use these ideas in `02_grid_isochrones.ipynb`:

- derive `length_m`
- derive travel time by mode
- filter roads by walk/bike/car fields
- snap grid centroids to nearest network edges
- run Dijkstra to compute 15-minute network reachability
- cache reachable edge results per origin

## What Not To Reuse Directly

The notebook has hard-coded Mac paths and depends on packages that may be difficult to install on Windows:

```text
policosm
graph_tool
geoparquet
```

For this project, we should treat the Parquet file as the reusable output and implement any new network analysis with more accessible tools such as `geopandas`, `networkx`, `scipy`, and `shapely`.

