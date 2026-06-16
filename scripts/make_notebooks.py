from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip() + "\n"}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip() + "\n",
    }


def notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


LIT_REVIEW = """
# 01 Data Collection - Literature Review and Source Validation

The 15-minute city is a compact way to ask a much older planning question: can everyday life be organized so that essential needs are reachable without depending on long motorized trips? Moreno and colleagues popularized the contemporary formulation around proximity, diversity, density, and digitalization, but the idea also connects to neighborhood-unit planning, mixed-use urbanism, transit-oriented development, and public-health research on walkability. For a Shanghai project, the concept is useful because it translates a broad quality-of-life claim into a measurable accessibility problem: from a residential location or grid cell, which daily services can be reached within a plausible 15-minute travel budget, and how evenly is that accessibility distributed across the metropolis?

The most important lesson from recent work is that a 15-minute city should not be treated as a simple count of amenities inside a circle. Accessibility depends on the transport mode, the street network, the quality of the destination, and the social meaning of the trip. A nearby park with a locked gate, a sports venue that charges high fees, or a supermarket across a hostile arterial road should not be interpreted in the same way as a welcoming public facility on a safe walking route. Studies of walkability and active travel therefore emphasize network distance, street connectivity, perceived safety, shade, cycling infrastructure, and the mix of land uses. Public-health research adds another layer: routine physical activity is more likely when sport and recreation opportunities are close, pleasant, affordable, and embedded in daily routes rather than isolated as special-purpose destinations.

The Paris heterogeneity paper supplied for this project is especially relevant because it warns against a one-size-fits-all 15-minute metric. It shows that urban areas with similar average accessibility may still differ strongly by neighborhood structure and local distribution of services. In other words, the citywide mean can hide the lived experience of peripheral towns, industrial edges, new towns, and dense central districts. That argument matters for Shanghai because the municipality contains very different urban forms: the historic core, Pudong's development corridors, suburban districts such as Qingpu and Fengxian, island and waterfront landscapes, and large patches of logistics or manufacturing land. A credible analysis should therefore keep the spatial unit small enough to reveal heterogeneity and should report scores by local cells rather than only by district averages.

For this Track A project, the baseline 15-minute city is defined as access to daily retail and food, primary healthcare, education or childcare, open space, public transport, and civic/community services. The health and sport track then asks whether a place supports a healthy lifestyle beyond minimum daily convenience. I operationalize that track with five components: sport facilities, green/outdoor access, cycling environment, healthy food access, and environmental quality. This follows the public-health logic that exercise is shaped by both formal facilities and informal environments. Gyms, courts, swimming pools, parks, green corridors, safe bikeable roads, and fresh-food retailers all contribute to the opportunity structure for healthy routines.

The data strategy reflects these concepts. Gaode POI shapefiles provide rich point-level amenities for sport, food, healthcare, education, civic services, and transport-related facilities. The Baidu AOI layer adds polygonal places, including parks, residential compounds, and a housing-price proxy used only in the web detail panel. The 2024 administrative boundary layer provides the outer city clip and district labels, while the analysis mask is built from land and urban-activity evidence so coastal districts, Changxing Island, and Chongming Island remain visible without filling open sea. The 2020 built-up area layer is retained as a source reference rather than as the final web-map mask. Traffic shapefiles supply bus stops, metro stations, metro exits, and related transit features. AI-interpreted green-space shapefiles and land-use polygons strengthen the open-space and environmental components. Finally, the simplified Shanghai road parquet derived from OSM-style network extraction contributes cycling and major-road indicators.

The project uses a 500 m grid as the working analysis surface and H3 resolution 8 as the web display layer. The 500 m grid is intuitive for urban planning because it approximates a fine neighborhood block scale while remaining computationally manageable. H3 hexagons are useful for the final application because they create equal-index spatial units that aggregate well, render efficiently, and avoid some visual bias of square grids. The notebooks model 15-minute access with mode-specific catchments: walking at about 1.2 km, cycling at about 3.5 km, transit as a local public-transport catchment, and car at 5 km. This is an accessibility proxy rather than a full routing model. The road network is used for cycling and environmental context, and the supplied network-extract notebook documents how a future extension could replace straight-line catchments with Dijkstra network isochrones.

The final score is deliberately transparent. For each grid cell, distance and nearby counts are combined into category scores from 0 to 100. The baseline score is a weighted average of six everyday-service categories. The Track A score is a weighted average of sport, green/outdoor, cycling, healthy food, and environmental quality. The composite score is 60% baseline and 40% Track A, reflecting that healthy lifestyle opportunities should build on, rather than replace, everyday urban accessibility. The resulting H3 GeoJSON is not a definitive judgment of neighborhoods; it is a reproducible analytical layer designed for comparison, critique, and interactive exploration.
"""


def build_01() -> dict:
    return notebook(
        [
            md(LIT_REVIEW),
            md(
                """
---

# Setup steps

This notebook follows the style of the supplied urban-analytics examples: small cells, explicit setup, then repeated validation tables before any scoring. The raw data are intentionally not hidden behind one black-box function. Later notebooks use helper functions for reproducibility, but this first notebook opens the data catalogue and shows what each source contributes.
"""
            ),
            code(
                r"""
from pathlib import Path
import os
import sys
import json
import textwrap
import pandas as pd

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / ".deps"))
sys.path.insert(0, str(ROOT))

ROOT
"""
            ),
            code(
                r"""
import geopandas as gpd
import pyogrio
import pyarrow.parquet as pq

from scripts.build_outputs import (
    RAW,
    PROJECT_CRS,
    WGS84,
    BASELINE_WEIGHTS,
    TRACK_WEIGHTS,
    MODE_RADII_M,
    load_env,
    locate_paths,
)
from scripts.poi_2024 import load_poi_2024_points

load_env()
paths = locate_paths()
"""
            ),
            md(
                """
## Data sources used in this project

The table below is the conceptual source log. The following cells then validate the files on disk, including feature counts, geometry type, CRS, and selected fields.
"""
            ),
            code(
                r"""
source_log = pd.DataFrame([
    {"family": "Administrative", "dataset": "2024 Shanghai city/district boundaries", "use": "outer city clip and district labels"},
    {"family": "Built area", "dataset": "2020 built-up area", "use": "one component of the land and activity mask"},
    {"family": "POI", "dataset": "Gaode WGS84 POI shapefiles", "use": "food, health, education, sport, civic, transit proxy"},
    {"family": "POI", "dataset": "POI 2024 classified CSVs", "use": "preferred Shanghai POI source for Track A sport, food, scenic, transit, and baseline education/health"},
    {"family": "Traffic", "dataset": "bus stops, metro stations, metro exits", "use": "public transport access"},
    {"family": "AOI", "dataset": "Baidu AOI polygons", "use": "supplement amenities, parks, housing-price proxy"},
    {"family": "Green space", "dataset": "AI interpreted green-space polygons", "use": "green/outdoor and environmental quality"},
    {"family": "Land use", "dataset": "OSM/AOI landuse parks", "use": "open space supplement"},
    {"family": "Road network", "dataset": "shanghai-roads-simplified.parquet", "use": "cycling environment and road context"},
])
source_log
"""
            ),
            md("# I. Inspect raw vector layers"),
            code(
                r"""
def vector_info(label, path):
    info = pyogrio.read_info(path)
    return {
        "label": label,
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "features": info.get("features"),
        "geometry_type": info.get("geometry_type"),
        "crs": str(info.get("crs")),
        "fields": ", ".join(list(info.get("fields"))[:14]),
    }

inventory = []
for label, path in paths.items():
    if str(path).lower().endswith(".shp"):
        inventory.append(vector_info(label, path))
    else:
        inventory.append({
            "label": label,
            "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            "features": None,
            "geometry_type": "parquet",
            "crs": "",
            "fields": "",
        })

inventory_df = pd.DataFrame(inventory)
inventory_df
"""
            ),
            code(
                r"""
inventory_df[["label", "features", "geometry_type", "crs"]].style.format({"features": "{:,.0f}"})
"""
            ),
            md("## I.1. Boundary and built-area validation"),
            code(
                r"""
city = gpd.read_file(paths["city_boundary"], encoding="utf-8")
districts = gpd.read_file(paths["district_boundary"], encoding="utf-8")
built = gpd.read_file(paths["built_area_2020"], encoding="utf-8")

pd.DataFrame([
    {"layer": "city", "rows": len(city), "crs": str(city.crs), "geom": city.geom_type.iloc[0], "bounds": tuple(round(x, 4) for x in city.total_bounds)},
    {"layer": "districts", "rows": len(districts), "crs": str(districts.crs), "geom": districts.geom_type.iloc[0], "bounds": tuple(round(x, 4) for x in districts.total_bounds)},
    {"layer": "built_2020", "rows": len(built), "crs": str(built.crs), "geom": built.geom_type.iloc[0], "bounds": tuple(round(x, 4) for x in built.total_bounds)},
])
"""
            ),
            code(
                r"""
district_name_col = next(c for c in ["县级", "县", "NAME", "name"] if c in districts.columns)
districts[[district_name_col, "面积", "人口"]].head(10)
"""
            ),
            md("# II. Inspect POI files"),
            code(
                r"""
poi_dir = Path(os.environ.get("SHANGHAI_POI_SHP_DIR", ""))
print("POI directory:", poi_dir)
print("Exists:", poi_dir.exists())
"""
            ),
            code(
                r"""
poi_2024_groups, poi_2024_meta = load_poi_2024_points(RAW, PROJECT_CRS)
poi_2024_meta
"""
            ),
            code(
                r"""
pd.Series(poi_2024_meta.get("group_row_counts", {})).sort_values(ascending=False).to_frame("rows")
"""
            ),
            code(
                r"""
sport = poi_2024_groups["sport"][0] if poi_2024_groups["sport"] else None
healthy_food = poi_2024_groups["healthy_food"][0] if poi_2024_groups["healthy_food"] else None
education = poi_2024_groups["education"][0] if poi_2024_groups["education"] else None

if sport is not None:
    display(sport[[c for c in ["name", "bigType", "midType", "smallType", "typecode", "adname"] if c in sport.columns]].head(8))
if healthy_food is not None:
    display(healthy_food[[c for c in ["name", "bigType", "midType", "smallType", "typecode", "adname"] if c in healthy_food.columns]].head(8))
if education is not None:
    display(education[[c for c in ["name", "bigType", "midType", "smallType", "typecode", "adname"] if c in education.columns]].head(8))
"""
            ),
            code(
                r"""
poi_rows = []
if poi_dir.exists():
    for shp in sorted(poi_dir.glob("*.shp")):
        info = pyogrio.read_info(shp)
        parts = shp.stem.split("_")
        major = parts[1] if len(parts) >= 2 else shp.stem
        poi_rows.append({
            "major_category": major,
            "file": shp.name,
            "features": info.get("features"),
            "geometry_type": info.get("geometry_type"),
            "crs": str(info.get("crs")),
            "fields": ", ".join(list(info.get("fields"))[:10]),
        })

poi_inventory = pd.DataFrame(poi_rows).sort_values("features", ascending=False)
poi_inventory
"""
            ),
            code(
                r"""
selected_poi = [
    "交通设施服务", "体育休闲服务", "公共设施", "医疗保健服务", "政府机构及社会团体",
    "生活服务", "科教文化服务", "购物服务", "风景名胜", "餐饮服务",
]
poi_inventory.assign(
    selected_for_model=poi_inventory["major_category"].isin(selected_poi)
).groupby("selected_for_model")["features"].sum().rename("features").to_frame()
"""
            ),
            code(
                r"""
def read_poi_sample(major_category, n=5):
    match = poi_inventory.loc[poi_inventory["major_category"].eq(major_category), "file"].iloc[0]
    gdf = gpd.read_file(poi_dir / match, rows=n, encoding="utf-8")
    cols = [c for c in ["name", "type", "address", "经度", "纬度", "adname", "行业大", "行业中", "行业小"] if c in gdf.columns]
    return gdf[cols]

read_poi_sample("体育休闲服务", n=8)
"""
            ),
            code(
                r"""
read_poi_sample("医疗保健服务", n=8)
"""
            ),
            md("# III. Inspect traffic, AOI, green, and land-use layers"),
            code(
                r"""
traffic_layers = {
    "bus_stops": paths["bus_stops"],
    "metro_stations": paths["metro_stations"],
    "metro_exits": paths["metro_exits"],
}

traffic_inventory = pd.DataFrame([vector_info(label, path) for label, path in traffic_layers.items()])
traffic_inventory[["label", "features", "geometry_type", "crs", "fields"]]
"""
            ),
            code(
                r"""
aoi = gpd.read_file(paths["aoi"], rows=8, encoding="utf-8")
landuse = gpd.read_file(paths["landuse_webmap"], rows=8, encoding="utf-8")

display(aoi[[c for c in ["name", "type", "type1", "type2", "type3", "价格"] if c in aoi.columns]])
display(landuse[[c for c in ["name", "fclass", "code"] if c in landuse.columns]])
"""
            ),
            code(
                r"""
green_layers = []
for shp in sorted((RAW / "ai_interpreted").rglob("*绿地.shp")):
    info = pyogrio.read_info(shp)
    green_layers.append({
        "file": str(shp.relative_to(ROOT)),
        "features": info.get("features"),
        "geometry_type": info.get("geometry_type"),
        "crs": str(info.get("crs")),
    })

green_inventory = pd.DataFrame(green_layers)
green_inventory.assign(features=lambda d: d["features"].map(lambda x: f"{x:,.0f}"))
"""
            ),
            md("# IV. Inspect road parquet, following the network-extract notebook"),
            code(
                r"""
roads_path = paths["roads"]
pq_file = pq.ParquetFile(roads_path)
roads_schema = pd.DataFrame({
    "field": pq_file.schema.names,
    "type": [str(pq_file.schema_arrow.field(i).type) for i in range(len(pq_file.schema.names))],
})
roads_schema
"""
            ),
            code(
                r"""
roads = gpd.read_parquet(roads_path)
roads = roads.set_crs(PROJECT_CRS, allow_override=True) if roads.crs is None else roads.to_crs(PROJECT_CRS)
roads["length_m"] = roads.geometry.length

road_summary = pd.Series({
    "rows": len(roads),
    "total_km": roads["length_m"].sum() / 1000,
    "median_edge_m": roads["length_m"].median(),
    "bike_edges": (pd.to_numeric(roads.get("bicycle", 0), errors="coerce").fillna(0) > 0).sum(),
    "foot_edges": (pd.to_numeric(roads.get("foot", 0), errors="coerce").fillna(0) > 0).sum(),
}).round(2)
road_summary
"""
            ),
            code(
                r"""
roads[["osm_id", "highway", "level", "bicycle", "foot", "length_m"]].head(10)
"""
            ),
            md("# V. Model design and validation rules"),
            code(
                r"""
weights = pd.DataFrame({
    "baseline_weight": pd.Series(BASELINE_WEIGHTS),
    "track_a_weight": pd.Series(TRACK_WEIGHTS),
}).fillna("")

mode_radii = pd.DataFrame(
    [{"mode": k, "radius_m": v, "radius_km": v / 1000} for k, v in MODE_RADII_M.items()]
)

display(weights)
display(mode_radii)
"""
            ),
            code(
                r"""
validation_checks = pd.DataFrame([
    {"check": "All core shapefiles exist", "status": all(path.exists() for path in paths.values())},
    {"check": "POI 2024 classified CSVs loaded", "status": poi_2024_meta.get("poi_status") == "loaded"},
    {"check": "Legacy POI directory exists", "status": poi_dir.exists()},
    {"check": "2024 district layer has 16 districts", "status": len(districts) == 16},
    {"check": "Road parquet has geometry", "status": "geometry" in roads.columns},
    {"check": "POI 2024 sport rows available", "status": int(poi_2024_meta.get("group_row_counts", {}).get("sport", 0)) > 10000},
])
validation_checks
"""
            ),
            code(
                r"""
out = ROOT / "data" / "processed" / "source_inventory.csv"
source_inventory = pd.concat(
    [
        inventory_df.assign(source_family="project_raw_layers"),
        poi_inventory.rename(columns={"file": "path", "major_category": "label"}).assign(source_family="gaode_poi"),
        pd.DataFrame(poi_2024_meta.get("files_used", [])).assign(label="POI 2024 classified CSVs", geometry_type="table", source_family="poi_2024"),
        green_inventory.rename(columns={"file": "path"}).assign(label="ai_green_space", source_family="ai_interpreted"),
    ],
    ignore_index=True,
    sort=False,
)
source_inventory.to_csv(out, index=False, encoding="utf-8-sig")
print(f"Wrote {out}")
source_inventory[["source_family", "label", "features", "geometry_type"]].head(25)
"""
            ),
            md(
                """
## Data limitations recorded for the final transparency panel

The analysis is source-rich but still approximate. POI data indicate the existence of facilities, not quality, price, opening hours, or public accessibility. The 15-minute catchments are mode-specific distance proxies rather than GTFS or traffic-aware routes. The road parquet makes it possible to discuss cycling and network structure, but a full all-grid Dijkstra routing computation would require more runtime and a complete routable multimodal network. These limitations are carried into `summary.json` and the web app transparency panel.
"""
            ),
        ]
    )


def build_02() -> dict:
    return notebook(
        [
            md(
                """
# 02 Grid, Network Preparation, and Four-Mode Isochrones

This notebook mirrors the supplied Shanghai network-extract notebook more closely than the short version did. It first prepares road travel times, then creates a 500 m analysis grid, then computes the practical four-mode accessibility surfaces used in the final score.
"""
            ),
            md("# Setup"),
            code(
                r"""
from pathlib import Path
import sys
import itertools
from operator import itemgetter
import numpy as np
import pandas as pd

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / ".deps"))
sys.path.insert(0, str(ROOT))

import geopandas as gpd
from shapely.geometry import Point, LineString
from scipy.spatial import cKDTree

from scripts.build_outputs import (
    PROJECT_CRS,
    MODE_RADII_M,
    add_accessibility_scores,
    add_districts,
    add_h3_ids,
    add_housing_price,
    create_analysis_mask,
    create_500m_grid,
    load_env,
    load_poi_points,
    load_supporting_points,
    locate_paths,
    merge_groups,
    read_file,
    union_geometry,
)

load_env()
paths = locate_paths()
"""
            ),
            md("# I. Road-network preparation"),
            code(
                r"""
roads = gpd.read_parquet(paths["roads"])
roads = roads.set_crs(PROJECT_CRS, allow_override=True) if roads.crs is None else roads.to_crs(PROJECT_CRS)
roads["length_m"] = roads.geometry.length
roads[["osm_id", "highway", "level", "bicycle", "foot", "geometry"]].head(3)
"""
            ),
            code(
                r"""
# Speeds mirror the supplied shanghai-network-extract notebook.
SPEEDS_MPS = {
    "foot": 1.33,
    "bike": 3.05,
    "car": 8.30,
}

roads["foot_time_s"] = roads["length_m"] / SPEEDS_MPS["foot"]
roads["bike_time_s"] = roads["length_m"] / SPEEDS_MPS["bike"]
roads["car_time_s"] = roads["length_m"] / SPEEDS_MPS["car"]

roads[["length_m", "foot_time_s", "bike_time_s", "car_time_s"]].describe().round(2)
"""
            ),
            code(
                r"""
gdf_car = roads[pd.to_numeric(roads["level"], errors="coerce").fillna(0) >= 3].copy()
gdf_foot = roads[pd.to_numeric(roads["foot"], errors="coerce").fillna(0) > 0].copy()
gdf_bike = roads[pd.to_numeric(roads["bicycle"], errors="coerce").fillna(0) > 0].copy()

pd.DataFrame([
    {"mode": "foot", "edges": len(gdf_foot), "km": gdf_foot["length_m"].sum() / 1000},
    {"mode": "bike", "edges": len(gdf_bike), "km": gdf_bike["length_m"].sum() / 1000},
    {"mode": "car", "edges": len(gdf_car), "km": gdf_car["length_m"].sum() / 1000},
]).round(1)
"""
            ),
            md("## I.1. Nearest-edge helper, following the reference notebook"),
            code(
                r"""
def ckdnearest(gdfA, gdfB):
    # Return nearest row indices in gdfB for every coordinate in gdfA.
    A = np.concatenate([np.array(geom.coords) for geom in gdfA.geometry.to_list()])
    B_parts = [np.array(geom.coords) for geom in gdfB.geometry.to_list()]
    B_ix = tuple(itertools.chain.from_iterable([
        itertools.repeat(i, x) for i, x in enumerate(list(map(len, B_parts)))
    ]))
    B = np.concatenate(B_parts)
    ckd_tree = cKDTree(B)
    dist, idx = ckd_tree.query(A, k=1)
    idx = np.atleast_1d(idx)
    row_positions = np.array([B_ix[int(i)] for i in idx], dtype=int)
    return row_positions, np.atleast_1d(dist)
"""
            ),
            code(
                r"""
sample_origin = gpd.GeoDataFrame(
    [["People Square", Point(21351908, 3456756)]],
    columns=["name", "geometry"],
    crs=PROJECT_CRS,
)

idx_car, dist_car = ckdnearest(sample_origin, gdf_car)
idx_bike, dist_bike = ckdnearest(sample_origin, gdf_bike)
idx_foot, dist_foot = ckdnearest(sample_origin, gdf_foot)

pd.DataFrame([
    {"mode": "car", "edge_id": gdf_car.iloc[idx_car].index[0], "nearest_m": float(dist_car[0])},
    {"mode": "bike", "edge_id": gdf_bike.iloc[idx_bike].index[0], "nearest_m": float(dist_bike[0])},
    {"mode": "foot", "edge_id": gdf_foot.iloc[idx_foot].index[0], "nearest_m": float(dist_foot[0])},
]).round(2)
"""
            ),
            md("## I.2. Dijkstra isochrone pattern"),
            code(
                r"""
DIJKSTRA_PSEUDOCODE = "\n".join([
    "1. Filter the road network by mode: foot, bike, or car.",
    "2. Convert each road edge to graph edges with travel-time weight.",
    "3. Snap an origin point to the nearest eligible edge.",
    "4. Run Dijkstra until travel time exceeds 15 * 60 seconds.",
    "5. Keep fully reachable edges and cut partially reachable edge segments.",
    "6. Buffer/union reachable segments into an isochrone polygon.",
])

print(DIJKSTRA_PSEUDOCODE)
"""
            ),
            code(
                r"""
threshold_s = 15 * 60
euclidean_buffers = gpd.GeoDataFrame(
    [
        ["walk", sample_origin.geometry.iloc[0].buffer(threshold_s * SPEEDS_MPS["foot"])],
        ["bike", sample_origin.geometry.iloc[0].buffer(threshold_s * SPEEDS_MPS["bike"])],
        ["car", sample_origin.geometry.iloc[0].buffer(threshold_s * SPEEDS_MPS["car"])],
    ],
    columns=["mode", "geometry"],
    crs=PROJECT_CRS,
)
euclidean_buffers["area_km2"] = euclidean_buffers.geometry.area / 1_000_000
euclidean_buffers[["mode", "area_km2"]].round(2)
"""
            ),
            md("# II. Build the 500 m grid"),
            code(
                r"""
city = read_file(paths["city_boundary"], crs=PROJECT_CRS)
built = read_file(paths["built_area_2020"], crs=PROJECT_CRS)
city_union = union_geometry(city)
built["geometry"] = built.geometry.make_valid().intersection(city_union)
built = built[~built.geometry.is_empty].copy()
analysis_mask = create_analysis_mask(paths, city)

pd.Series({
    "city_area_km2": city.geometry.area.sum() / 1_000_000,
    "built_area_km2": built.geometry.area.sum() / 1_000_000,
    "analysis_mask_km2": analysis_mask.geometry.area.sum() / 1_000_000,
    "built_polygons": len(built),
}).round(2)
"""
            ),
            code(
                r"""
grid = create_500m_grid(analysis_mask, label="land and urban-activity mask")
grid = add_districts(grid, paths["district_boundary"])

grid[["grid_id", "district", "cell_area_m2", "centroid_x", "centroid_y"]].head()
"""
            ),
            code(
                r"""
grid.groupby("district").size().sort_values(ascending=False).rename("grid_cells").head(20).to_frame()
"""
            ),
            md("# III. Load amenities and supporting layers"),
            code(
                r"""
poi_groups, poi_meta = load_poi_points()
support_groups, support_meta = load_supporting_points(paths)
groups = merge_groups(poi_groups, support_groups)

group_counts = pd.Series({k: len(v) for k, v in groups.items()}).sort_values(ascending=False)
print("POI status:", poi_meta["poi_status"])
print("POI source:", poi_meta.get("poi_source", "unknown"))
print("POI rows loaded:", f"{poi_meta['poi_rows_loaded']:,}")
group_counts.to_frame("features")
"""
            ),
            code(
                r"""
pd.Series(poi_meta.get("group_row_counts", {})).sort_values(ascending=False).to_frame("poi_rows")
"""
            ),
            code(
                r"""
support_meta
"""
            ),
            md("# IV. Four-mode accessibility scores"),
            code(
                r"""
pd.DataFrame(
    [{"mode": mode, "radius_m": radius, "radius_km": radius / 1000} for mode, radius in MODE_RADII_M.items()]
)
"""
            ),
            code(
                r"""
grid = add_accessibility_scores(grid, groups)
grid = add_housing_price(grid, groups["housing_price"])
grid = add_h3_ids(grid)

score_cols = [
    "baseline_walk", "health_walk", "composite_walk",
    "composite_bike", "composite_transit", "composite_car",
    "metro_dist_m", "major_road_dist_m", "rent_band",
]
grid[["grid_id", "district"] + score_cols].head()
"""
            ),
            code(
                r"""
mode_summary = grid[[
    "composite_walk", "composite_bike", "composite_transit", "composite_car",
    "baseline_walk", "health_walk",
]].describe().round(2)
mode_summary
"""
            ),
            code(
                r"""
category_cols = [
    "food_walk_score", "healthcare_walk_score", "education_walk_score",
    "open_space_walk_score", "transit_access_walk_score", "civic_walk_score",
    "sport_walk_score", "green_outdoor_walk_score", "cycling_env_walk_score",
    "healthy_food_walk_score", "env_quality_walk_score",
]
grid[category_cols].mean().sort_values(ascending=False).round(2).to_frame("mean_score")
"""
            ),
            md("# V. Cache the grid layer"),
            code(
                r"""
grid_out = ROOT / "data" / "processed" / "shanghai_500m_health_grid.parquet"
grid.to_parquet(grid_out, index=False)
print(f"Wrote {grid_out}")
print(f"Rows: {len(grid):,}")
print(f"Columns: {len(grid.columns):,}")
"""
            ),
            code(
                r"""
qa = pd.DataFrame([
    {"check": "grid has H3 IDs", "value": grid["h3_id"].notna().all()},
    {"check": "all composite walk scores are finite", "value": np.isfinite(grid["composite_walk"]).all()},
    {"check": "metro distances computed", "value": grid["metro_dist_m"].notna().mean() > 0.95},
    {"check": "district label coverage", "value": grid["district"].ne("Unknown").mean()},
])
qa
"""
            ),
            md(
                """
## Notebook output

This notebook produces `data/processed/shanghai_500m_health_grid.parquet`. The final notebook aggregates that cell-level layer into H3 resolution 8 for the web application.
"""
            ),
        ]
    )


def build_03() -> dict:
    return notebook(
        [
            md(
                """
# 03 Scoring, H3 Aggregation, and Web GeoJSON Export

This notebook follows the H3 example notebook's structure: H3 metadata first, then point/cell indexing, hierarchy checks, aggregation, neighborhood rings, and final deck.gl-ready export.
"""
            ),
            md("# Setup"),
            code(
                r"""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / ".deps"))
sys.path.insert(0, str(ROOT))

import geopandas as gpd
import h3

from scripts.build_outputs import (
    H3_RESOLUTION,
    BASELINE_WEIGHTS,
    TRACK_WEIGHTS,
    aggregate_to_h3,
    main,
)
"""
            ),
            md("# I. H3 preliminaries"),
            code(
                r"""
h3_meta = []
for res in range(5, 11):
    h3_meta.append({
        "resolution": res,
        "avg_edge_m": h3.average_hexagon_edge_length(res, unit="m"),
        "avg_area_m2": h3.average_hexagon_area(res, unit="m^2"),
        "avg_area_km2": h3.average_hexagon_area(res, unit="km^2"),
    })

pd.DataFrame(h3_meta).round(3)
"""
            ),
            code(
                r"""
shanghai_center = (31.2304, 121.4737)
center_cells = []
for res in range(5, 11):
    cell = h3.latlng_to_cell(shanghai_center[0], shanghai_center[1], res)
    center_cells.append({
        "resolution": res,
        "h3_id": cell,
        "parent_res_5": h3.cell_to_parent(cell, 5) if res >= 5 else None,
    })

pd.DataFrame(center_cells)
"""
            ),
            code(
                r"""
center_h3 = h3.latlng_to_cell(shanghai_center[0], shanghai_center[1], H3_RESOLUTION)
ring_rows = []
for k in range(0, 4):
    ring_rows.append({"k_ring": k, "cells": len(h3.grid_disk(center_h3, k))})
pd.DataFrame(ring_rows)
"""
            ),
            md("## I.1. Parent-child hierarchy"),
            code(
                r"""
parent = h3.cell_to_parent(center_h3, H3_RESOLUTION - 1)
children = h3.cell_to_children(parent, H3_RESOLUTION)

pd.Series({
    "center_h3_res8": center_h3,
    "parent_res7": parent,
    "children_at_res8": len(children),
    "center_is_child": center_h3 in children,
})
"""
            ),
            md("# II. Scoring design"),
            code(
                r"""
weights = pd.DataFrame({
    "baseline_weight": pd.Series(BASELINE_WEIGHTS),
    "track_a_weight": pd.Series(TRACK_WEIGHTS),
}).fillna("")
weights
"""
            ),
            code(
                r"""
FORMULA = "\n".join([
    "For each 500 m grid cell:",
    "  category_score = 0.68 * distance_score + 0.32 * count_score",
    "  baseline_score = weighted mean of six everyday-service categories",
    "  track_score = weighted mean of five Healthy Lifestyle & Sport categories",
    "  composite_score = 0.60 * baseline_score + 0.40 * track_score",
    "",
    "For H3:",
    "  H3 score = mean of all 500 m grid cells whose centroids fall in the H3 cell",
])
print(FORMULA)
"""
            ),
            md("# III. Run or load the scored grid"),
            code(
                r"""
grid_path = ROOT / "data" / "processed" / "shanghai_500m_health_grid.parquet"
if not grid_path.exists():
    print("Grid cache missing; rebuilding all outputs from raw data.")
    main()
else:
    print(f"Using cached grid: {grid_path}")

grid = gpd.read_parquet(grid_path)
print(grid.shape)
grid[["grid_id", "district", "h3_id", "composite_score", "baseline_score", "track_score"]].head()
"""
            ),
            code(
                r"""
score_fields = [
    "composite_score", "baseline_score", "track_score",
    "composite_walk", "composite_bike", "composite_transit", "composite_car",
]
grid[score_fields].describe().round(2)
"""
            ),
            md("# IV. Aggregate 500 m cells to H3 resolution 8"),
            code(
                r"""
h3_gdf = aggregate_to_h3(grid)
print(h3_gdf.shape)
h3_gdf[["h3_id", "district", "grid_count", "composite_score", "baseline_score", "track_score"]].head()
"""
            ),
            code(
                r"""
pd.Series({
    "h3_cells": len(h3_gdf),
    "grid_cells": len(grid),
    "mean_grid_cells_per_h3": h3_gdf["grid_count"].mean(),
    "min_score": h3_gdf["composite_score"].min(),
    "mean_score": h3_gdf["composite_score"].mean(),
    "max_score": h3_gdf["composite_score"].max(),
}).round(2)
"""
            ),
            code(
                r"""
district_summary = (
    h3_gdf.groupby("district")
    .agg(
        h3_cells=("h3_id", "count"),
        composite_mean=("composite_score", "mean"),
        health_mean=("track_score", "mean"),
        metro_dist_mean=("metro_dist_m", "mean"),
    )
    .sort_values("composite_mean", ascending=False)
    .round(2)
)
district_summary.head(20)
"""
            ),
            md("# V. H3 neighborhood analysis"),
            code(
                r"""
top_cell = h3_gdf.sort_values("composite_score", ascending=False).iloc[0]
neighbors = set(h3.grid_disk(top_cell["h3_id"], 1))
neighbor_df = h3_gdf[h3_gdf["h3_id"].isin(neighbors)].copy()

pd.Series({
    "top_h3": top_cell["h3_id"],
    "district": top_cell["district"],
    "top_score": top_cell["composite_score"],
    "neighbor_cells_found": len(neighbor_df),
    "neighbor_mean_score": neighbor_df["composite_score"].mean(),
}).round(2)
"""
            ),
            code(
                r"""
top10 = h3_gdf.sort_values("composite_score", ascending=False)[[
    "h3_id", "district", "composite_score", "baseline_score", "track_score",
    "metro_dist_m", "rent_band", "top_amenities",
]].head(10)
top10
"""
            ),
            code(
                r"""
bottom10 = h3_gdf.sort_values("composite_score", ascending=True)[[
    "h3_id", "district", "composite_score", "baseline_score", "track_score",
    "metro_dist_m", "rent_band", "top_amenities",
]].head(10)
bottom10
"""
            ),
            md("# VI. Optional lightweight visualization"),
            code(
                r"""
# This cell is optional. It runs only if matplotlib is installed.
try:
    import matplotlib.pyplot as plt
    ax = h3_gdf.plot(
        column="composite_score",
        cmap="YlGn",
        linewidth=0.05,
        edgecolor="white",
        figsize=(9, 9),
        legend=True,
    )
    ax.set_axis_off()
    ax.set_title("H3 resolution 8 composite score")
except Exception as exc:
    print("Static plot skipped:", exc)
"""
            ),
            md("# VII. Export full and web-ready GeoJSON"),
            code(
                r"""
output_dir = ROOT / "data" / "output"
app_data_dir = ROOT / "app" / "data"
output_dir.mkdir(parents=True, exist_ok=True)
app_data_dir.mkdir(parents=True, exist_ok=True)

full_geojson = output_dir / "shanghai_health_h3_r8.geojson"
web_geojson = app_data_dir / "shanghai_health_h3_r8.geojson"

h3_gdf.to_file(full_geojson, driver="GeoJSON")
print(full_geojson, full_geojson.stat().st_size)
"""
            ),
            code(
                r"""
web_columns = [
    "h3_id", "district", "grid_count",
    "composite_score", "baseline_score", "track_score",
    "composite_walk", "composite_bike", "composite_transit", "composite_car",
    "baseline_walk", "baseline_bike", "baseline_transit", "baseline_car",
    "health_walk", "health_bike", "health_transit", "health_car",
    "food_walk_score", "healthcare_walk_score", "education_walk_score",
    "open_space_walk_score", "transit_access_walk_score", "civic_walk_score",
    "sport_walk_score", "green_outdoor_walk_score", "cycling_env_walk_score",
    "healthy_food_walk_score", "env_quality_walk_score",
    "food_walk_count", "healthcare_walk_count", "education_walk_count",
    "sport_walk_count", "green_outdoor_walk_count", "transit_access_walk_count",
    "metro_dist_m", "major_road_dist_m", "housing_price_proxy", "rent_band",
    "top_amenities", "geometry",
]

h3_web = h3_gdf[[c for c in web_columns if c in h3_gdf.columns]].copy()
h3_web.to_file(web_geojson, driver="GeoJSON")
print(web_geojson, web_geojson.stat().st_size)
"""
            ),
            code(
                r"""
summary = {
    "project": "15-Minute Shanghai - Track A Healthy Lifestyle & Sport",
    "grid_size_m": 500,
    "h3_resolution": H3_RESOLUTION,
    "grid_cells": int(len(grid)),
    "h3_cells": int(len(h3_gdf)),
    "score_range": {
        "min": round(float(h3_gdf["composite_score"].min()), 2),
        "mean": round(float(h3_gdf["composite_score"].mean()), 2),
        "max": round(float(h3_gdf["composite_score"].max()), 2),
    },
    "method_notes": [
        "500 m cells are generated from a land and urban-activity mask so coastal districts, Changxing Island, and Chongming Island remain visible while open sea is excluded.",
        "The mask combines the 2020 built-up area, non-water land-use polygons, Baidu AOI polygons, and a small road-network buffer, clipped to the Shanghai administrative boundary.",
        "15-minute access is modelled with mode-specific distance catchments.",
        "Road data support cycling environment and major-road environmental context.",
    ],
}

summary_path = output_dir / "summary_notebook_export.json"
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
summary
"""
            ),
            md("# VIII. deck.gl / H3HexagonLayer handoff"),
            code(
                r"""
DECK_GL_FIELDS = [
    "h3_id",
    "composite_walk", "composite_bike", "composite_transit", "composite_car",
    "baseline_walk", "health_walk",
    "sport_walk_score", "green_outdoor_walk_score", "cycling_env_walk_score",
    "metro_dist_m", "rent_band", "top_amenities",
]

h3_web[DECK_GL_FIELDS].head()
"""
            ),
            md(
                """
## Final export check

The web application loads `app/data/shanghai_health_h3_r8.geojson`. Each feature contains an H3 index, polygon geometry, mode-specific scores, baseline/Track A scores, detail-panel fields, and recommender fields. This mirrors the H3 example's final handoff to deck.gl, but uses Shanghai's health-and-sport scoring rather than Toulouse bus-stop counts.
"""
            ),
        ]
    )


def main() -> None:
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    outputs = {
        "01_data_collection.ipynb": build_01(),
        "02_grid_isochrones.ipynb": build_02(),
        "03_scoring_h3.ipynb": build_03(),
    }
    for filename, nb in outputs.items():
        path = NOTEBOOKS / filename
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {path} with {len(nb['cells'])} cells")


if __name__ == "__main__":
    main()
