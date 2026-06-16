from __future__ import annotations

import json
import math
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT / ".deps"
if DEPS.exists():
    sys.path.insert(0, str(DEPS))

import geopandas as gpd
import h3
import numpy as np
import pandas as pd
import pyogrio
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, box

from scripts.poi_2024 import load_poi_2024_points


RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "data" / "output"
APP_DATA = ROOT / "app" / "data"
WGS84 = "EPSG:4326"
PROJECT_CRS = "EPSG:4576"
GRID_SIZE_M = 500
H3_RESOLUTION = 8

MODE_RADII_M = {
    "walk": 1200,
    "bike": 3500,
    "transit": 2500,
    "car": 5000,
}

BASELINE_WEIGHTS = {
    "food": 0.20,
    "healthcare": 0.18,
    "education": 0.18,
    "open_space": 0.18,
    "transit_access": 0.16,
    "civic": 0.10,
}

TRACK_WEIGHTS = {
    "sport": 0.35,
    "green_outdoor": 0.25,
    "cycling_env": 0.15,
    "healthy_food": 0.10,
    "env_quality": 0.15,
}

TARGET_COUNTS = {
    "food": 10,
    "healthcare": 4,
    "education": 5,
    "open_space": 4,
    "transit_access": 6,
    "civic": 4,
    "sport": 5,
    "green_outdoor": 5,
    "cycling_env": 12,
    "healthy_food": 5,
}

POI_MAJOR_TO_GROUPS = {
    "购物服务": ["food"],
    "餐饮服务": ["food"],
    "生活服务": ["food"],
    "医疗保健服务": ["healthcare"],
    "科教文化服务": ["education"],
    "政府机构及社会团体": ["civic"],
    "公共设施": ["civic"],
    "体育休闲服务": ["sport", "open_space", "green_outdoor"],
    "风景名胜": ["open_space", "green_outdoor"],
    "交通设施服务": ["transit_access"],
}

HEALTHY_FOOD_KEYWORDS = [
    "菜",
    "蔬",
    "水果",
    "生鲜",
    "农贸",
    "食品",
    "超市",
    "便利",
    "市场",
]

AOI_GROUP_KEYWORDS = {
    "food": ["购物", "餐饮", "生活服务", "超市", "市场", "商场", "便利"],
    "healthcare": ["医疗", "医院", "药房", "诊所", "卫生"],
    "education": ["科教", "学校", "幼儿园", "大学", "培训", "文化"],
    "civic": ["政府", "公共设施", "社区", "政务", "文化"],
    "sport": ["体育", "健身", "运动", "球场", "游泳", "羽毛球", "篮球"],
    "open_space": ["公园", "广场", "风景", "绿地", "景区"],
    "green_outdoor": ["公园", "广场", "风景", "绿地", "景区"],
    "healthy_food": ["菜", "蔬", "水果", "生鲜", "农贸", "食品", "超市", "市场"],
}


def log(message: str) -> None:
    print(f"[build_outputs] {message}", flush=True)


def load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def ensure_dirs() -> None:
    for path in (PROCESSED, OUTPUT, APP_DATA):
        path.mkdir(parents=True, exist_ok=True)


def find_one(base: Path, label: str, include: list[str], exclude: list[str] | None = None) -> Path:
    exclude = exclude or []
    matches = []
    for path in base.rglob("*.shp"):
        text = str(path)
        if all(term in text for term in include) and not any(term in text for term in exclude):
            matches.append(path)
    if not matches:
        raise FileNotFoundError(f"Could not locate {label}: include={include}, exclude={exclude}")
    matches.sort(key=lambda p: (len(str(p)), str(p)))
    return matches[0]


def read_file(path: Path, crs: str | None = None, columns: list[str] | None = None) -> gpd.GeoDataFrame:
    kwargs = {"encoding": "utf-8"}
    if columns:
        try:
            available = set(pyogrio.read_info(path)["fields"])
            cols = [c for c in columns if c in available]
            gdf = pyogrio.read_dataframe(path, columns=cols, encoding="utf-8")
        except Exception:
            gdf = gpd.read_file(path, **kwargs)
    else:
        gdf = gpd.read_file(path, **kwargs)
    if gdf.crs is None:
        gdf = gdf.set_crs(WGS84, allow_override=True)
    if crs:
        gdf = gdf.to_crs(crs)
    gdf = gdf[gdf.geometry.notna()].copy()
    return gdf


def union_geometry(gdf: gpd.GeoDataFrame):
    fixed = gdf.copy()
    fixed["geometry"] = fixed.geometry.make_valid()
    return fixed.geometry.union_all()


def create_500m_grid(mask: gpd.GeoDataFrame, label: str = "analysis area") -> gpd.GeoDataFrame:
    mask_union = union_geometry(mask)
    minx, miny, maxx, maxy = mask.total_bounds
    xs = np.arange(math.floor(minx / GRID_SIZE_M) * GRID_SIZE_M, maxx + GRID_SIZE_M, GRID_SIZE_M)
    ys = np.arange(math.floor(miny / GRID_SIZE_M) * GRID_SIZE_M, maxy + GRID_SIZE_M, GRID_SIZE_M)
    cells = []
    ids = []
    for ix, x in enumerate(xs[:-1]):
        for iy, y in enumerate(ys[:-1]):
            geom = box(x, y, x + GRID_SIZE_M, y + GRID_SIZE_M)
            if geom.intersects(mask_union):
                cells.append(geom)
                ids.append(f"g{ix:04d}_{iy:04d}")
    grid = gpd.GeoDataFrame({"grid_id": ids}, geometry=cells, crs=mask.crs)
    grid["cell_area_m2"] = grid.geometry.area
    grid["centroid_x"] = grid.geometry.centroid.x
    grid["centroid_y"] = grid.geometry.centroid.y
    log(f"Created {len(grid):,} 500 m grid cells from {label}.")
    return grid


def point_from_polygons(gdf: gpd.GeoDataFrame, label: str) -> gpd.GeoDataFrame:
    if gdf.empty:
        return gpd.GeoDataFrame({"source": []}, geometry=[], crs=PROJECT_CRS)
    out = gdf.copy()
    out["geometry"] = out.geometry.representative_point()
    out["source"] = label
    return out


def clean_text_frame(gdf: gpd.GeoDataFrame) -> pd.Series:
    text_cols = [c for c in ["name", "type", "type1", "type2", "type3", "行业大", "行业中", "行业小"] if c in gdf.columns]
    if not text_cols:
        return pd.Series([""] * len(gdf), index=gdf.index)
    text = gdf[text_cols].fillna("").astype(str).agg(" ".join, axis=1)
    return text


def keyword_mask(text: pd.Series, keywords: list[str]) -> pd.Series:
    if not keywords:
        return pd.Series(False, index=text.index)
    pattern = "|".join(re.escape(k) for k in keywords)
    return text.str.contains(pattern, case=False, regex=True, na=False)


def load_poi_points() -> tuple[dict[str, list[gpd.GeoDataFrame]], dict]:
    poi_2024_groups, poi_2024_meta = load_poi_2024_points(RAW, PROJECT_CRS)
    if poi_2024_meta.get("poi_status") == "loaded":
        log(
            "Loaded POI 2024 classified CSVs: "
            + ", ".join(
                f"{group}={count:,}"
                for group, count in sorted((poi_2024_meta.get("group_row_counts") or {}).items())
            )
        )
        return poi_2024_groups, poi_2024_meta

    poi_dir_value = os.environ.get("SHANGHAI_POI_SHP_DIR", "")
    meta = {
        "poi_source": "legacy Gaode shapefiles",
        "poi_dir": poi_dir_value,
        "poi_files_used": [],
        "poi_rows_loaded": 0,
        "poi_status": "not configured",
    }
    groups: dict[str, list[gpd.GeoDataFrame]] = {k: [] for k in set(sum(POI_MAJOR_TO_GROUPS.values(), []))}
    groups.setdefault("healthy_food", [])
    if not poi_dir_value:
        return groups, meta

    poi_dir = Path(poi_dir_value)
    if not poi_dir.exists():
        meta["poi_status"] = "path missing or unreadable"
        return groups, meta

    selected_majors = set(POI_MAJOR_TO_GROUPS)
    try:
        files = sorted(poi_dir.glob("*.shp"))
    except PermissionError as exc:
        meta["poi_status"] = f"permission denied: {exc}"
        return groups, meta

    keep_columns = [
        "name",
        "type",
        "typecode",
        "address",
        "经度",
        "纬度",
        "adcode",
        "adname",
        "行业大",
        "行业中",
        "行业小",
    ]
    for shp in files:
        parts = shp.stem.split("_")
        major = parts[1] if len(parts) >= 2 else shp.stem
        if major not in selected_majors:
            continue
        try:
            gdf = read_file(shp, crs=PROJECT_CRS, columns=keep_columns)
        except Exception as exc:
            log(f"Skipped POI {shp.name}: {type(exc).__name__}: {exc}")
            continue
        if gdf.empty:
            continue
        gdf["source_major"] = major
        gdf["source"] = f"Gaode POI: {major}"
        text = clean_text_frame(gdf)
        for group in POI_MAJOR_TO_GROUPS[major]:
            groups.setdefault(group, []).append(gdf)
        if major in {"购物服务", "餐饮服务", "生活服务"}:
            hf = gdf[keyword_mask(text, HEALTHY_FOOD_KEYWORDS)].copy()
            if not hf.empty:
                groups["healthy_food"].append(hf)
        meta["poi_files_used"].append(shp.name)
        meta["poi_rows_loaded"] += len(gdf)
        log(f"Loaded POI {major}: {len(gdf):,} rows")
    meta["poi_status"] = "loaded" if meta["poi_rows_loaded"] else "no selected files loaded"
    return groups, meta


def append_group(groups: dict[str, list[gpd.GeoDataFrame]], group: str, gdf: gpd.GeoDataFrame) -> None:
    if not gdf.empty:
        groups.setdefault(group, []).append(gdf[[c for c in gdf.columns if c != "geometry"] + ["geometry"]].copy())


def load_supporting_points(paths: dict[str, Path]) -> tuple[dict[str, list[gpd.GeoDataFrame]], dict]:
    groups: dict[str, list[gpd.GeoDataFrame]] = {
        "food": [],
        "healthcare": [],
        "education": [],
        "open_space": [],
        "transit_access": [],
        "civic": [],
        "sport": [],
        "green_outdoor": [],
        "cycling_env": [],
        "healthy_food": [],
        "major_roads": [],
        "metro": [],
        "housing_price": [],
    }
    meta: dict[str, object] = {"supporting_layers": []}

    bus = read_file(paths["bus_stops"], crs=PROJECT_CRS)
    bus["source"] = "bus stops"
    append_group(groups, "transit_access", bus)
    meta["supporting_layers"].append({"layer": "bus_stops", "rows": int(len(bus))})

    metro = read_file(paths["metro_stations"], crs=PROJECT_CRS)
    metro["source"] = "metro stations"
    append_group(groups, "transit_access", metro)
    append_group(groups, "metro", metro)
    meta["supporting_layers"].append({"layer": "metro_stations", "rows": int(len(metro))})

    try:
        exits = read_file(paths["metro_exits"], crs=PROJECT_CRS)
        exits["source"] = "metro exits"
        append_group(groups, "transit_access", exits)
        meta["supporting_layers"].append({"layer": "metro_exits", "rows": int(len(exits))})
    except Exception as exc:
        meta["metro_exits_error"] = str(exc)

    aoi = read_file(
        paths["aoi"],
        crs=PROJECT_CRS,
        columns=["name", "type", "type1", "type2", "type3", "价格", "wgs_lng", "wgs_lat"],
    )
    aoi_points = point_from_polygons(aoi, "Baidu AOI")
    text = clean_text_frame(aoi_points)
    for group, keywords in AOI_GROUP_KEYWORDS.items():
        subset = aoi_points[keyword_mask(text, keywords)].copy()
        append_group(groups, group, subset)
    if "价格" in aoi_points.columns:
        price = pd.to_numeric(aoi_points["价格"], errors="coerce")
        housing = aoi_points[(price > 0) & keyword_mask(text, ["住宅", "小区", "商务住宅"])].copy()
        housing["housing_price_proxy"] = price.loc[housing.index]
        append_group(groups, "housing_price", housing)
    meta["supporting_layers"].append({"layer": "baidu_aoi", "rows": int(len(aoi))})

    landuse = read_file(paths["landuse_webmap"], crs=PROJECT_CRS, columns=["name", "fclass", "code"])
    if "fclass" in landuse.columns:
        parks = landuse[landuse["fclass"].fillna("").str.lower().isin(["park", "grass", "forest", "recreation_ground"])]
    else:
        parks = landuse.iloc[0:0]
    park_points = point_from_polygons(parks, "OSM/AOI landuse parks")
    append_group(groups, "open_space", park_points)
    append_group(groups, "green_outdoor", park_points)
    meta["supporting_layers"].append({"layer": "landuse_parks", "rows": int(len(parks))})

    green_frames = []
    for shp in sorted((RAW / "ai_interpreted").rglob("*绿地.shp")):
        try:
            g = read_file(shp, crs=PROJECT_CRS, columns=[])
            g["source"] = shp.parent.name
            green_frames.append(g)
        except Exception as exc:
            log(f"Skipped AI green {shp.name}: {type(exc).__name__}: {exc}")
    if green_frames:
        green = pd.concat(green_frames, ignore_index=True)
        green = gpd.GeoDataFrame(green, geometry="geometry", crs=PROJECT_CRS)
        green_points = point_from_polygons(green, "AI interpreted green space")
        append_group(groups, "open_space", green_points)
        append_group(groups, "green_outdoor", green_points)
        meta["supporting_layers"].append({"layer": "ai_green_space", "rows": int(len(green))})

    roads = gpd.read_parquet(paths["roads"])
    if roads.crs is None:
        roads = roads.set_crs(PROJECT_CRS, allow_override=True)
    else:
        roads = roads.to_crs(PROJECT_CRS)
    roads["length_m"] = roads.geometry.length
    roads_summary = {
        "rows": int(len(roads)),
        "total_km": round(float(roads["length_m"].sum() / 1000), 1),
    }
    if "bicycle" in roads.columns:
        bike_roads = roads[pd.to_numeric(roads["bicycle"], errors="coerce").fillna(0) > 0].copy()
    else:
        bike_roads = roads.iloc[0:0].copy()
    if bike_roads.empty and "highway" in roads.columns:
        bike_roads = roads[roads["highway"].isin(["cycleway", "residential", "living_street", "tertiary"])].copy()
    bike_roads["source"] = "bike-suitable road edges"
    bike_points = point_from_polygons(bike_roads, "bike-suitable road edges")
    append_group(groups, "cycling_env", bike_points)
    roads_summary["bike_suitable_km"] = round(float(bike_roads["length_m"].sum() / 1000), 1)

    if "level" in roads.columns:
        major_roads = roads[pd.to_numeric(roads["level"], errors="coerce").fillna(0) >= 4].copy()
    else:
        major_roads = roads.iloc[0:0].copy()
    major_roads["source"] = "major road edges"
    major_points = point_from_polygons(major_roads, "major road edges")
    append_group(groups, "major_roads", major_points)
    roads_summary["major_road_km"] = round(float(major_roads["length_m"].sum() / 1000), 1)
    meta["roads_summary"] = roads_summary

    return groups, meta


def merge_groups(*group_dicts: dict[str, list[gpd.GeoDataFrame]]) -> dict[str, gpd.GeoDataFrame]:
    merged: dict[str, gpd.GeoDataFrame] = {}
    all_keys = set()
    for group_dict in group_dicts:
        all_keys.update(group_dict.keys())
    for key in sorted(all_keys):
        frames = []
        for group_dict in group_dicts:
            frames.extend(group_dict.get(key, []))
        frames = [f for f in frames if f is not None and not f.empty]
        if frames:
            out = pd.concat(frames, ignore_index=True)
            merged[key] = gpd.GeoDataFrame(out, geometry="geometry", crs=PROJECT_CRS)
        else:
            merged[key] = gpd.GeoDataFrame({"source": []}, geometry=[], crs=PROJECT_CRS)
    return merged


def xy_array(gdf: gpd.GeoDataFrame) -> np.ndarray:
    if gdf.empty:
        return np.empty((0, 2))
    return np.column_stack([gdf.geometry.x.to_numpy(), gdf.geometry.y.to_numpy()])


def tree_metrics(points: gpd.GeoDataFrame, centroids_xy: np.ndarray, radius_by_mode: dict[str, int]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    if points.empty:
        return np.full(len(centroids_xy), np.inf), {
            mode: np.zeros(len(centroids_xy), dtype=int) for mode in radius_by_mode
        }
    tree = cKDTree(xy_array(points))
    dist, _ = tree.query(centroids_xy, k=1, workers=-1)
    counts = {}
    for mode, radius in radius_by_mode.items():
        counts[mode] = tree.query_ball_point(centroids_xy, r=radius, return_length=True, workers=-1)
    return dist, counts


def score_access(dist: np.ndarray, counts: np.ndarray, radius: float, target_count: int) -> np.ndarray:
    dist_score = np.clip(1 - (dist / radius), 0, 1)
    count_score = np.clip(np.log1p(counts) / np.log1p(max(target_count, 1)), 0, 1)
    return np.round((0.68 * dist_score + 0.32 * count_score) * 100, 2)


def add_accessibility_scores(grid: gpd.GeoDataFrame, groups: dict[str, gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    centroids_xy = grid[["centroid_x", "centroid_y"]].to_numpy()
    result = grid.copy()
    categories = list(BASELINE_WEIGHTS) + ["sport", "green_outdoor", "cycling_env", "healthy_food"]
    categories = list(dict.fromkeys(categories))

    for category in categories:
        dist, counts = tree_metrics(groups.get(category, gpd.GeoDataFrame(geometry=[])), centroids_xy, MODE_RADII_M)
        result[f"{category}_dist_m"] = np.where(np.isfinite(dist), np.round(dist, 1), np.nan)
        for mode, radius in MODE_RADII_M.items():
            result[f"{category}_{mode}_count"] = counts[mode].astype(int)
            result[f"{category}_{mode}_score"] = score_access(
                dist, counts[mode], radius, TARGET_COUNTS.get(category, 5)
            )

    metro_dist, _ = tree_metrics(groups.get("metro", gpd.GeoDataFrame(geometry=[])), centroids_xy, {"walk": 5000})
    result["metro_dist_m"] = np.where(np.isfinite(metro_dist), np.round(metro_dist, 1), np.nan)

    major_dist, _ = tree_metrics(groups.get("major_roads", gpd.GeoDataFrame(geometry=[])), centroids_xy, {"walk": 1000})
    result["major_road_dist_m"] = np.where(np.isfinite(major_dist), np.round(major_dist, 1), np.nan)
    road_buffer_score = np.clip(major_dist / 900, 0, 1) * 100
    road_buffer_score[~np.isfinite(major_dist)] = 50

    for mode in MODE_RADII_M:
        result[f"env_quality_{mode}_score"] = np.round(
            0.68 * result[f"green_outdoor_{mode}_score"] + 0.32 * road_buffer_score,
            2,
        )
        baseline = np.zeros(len(result))
        for category, weight in BASELINE_WEIGHTS.items():
            baseline += result[f"{category}_{mode}_score"].to_numpy() * weight
        track = np.zeros(len(result))
        for category, weight in TRACK_WEIGHTS.items():
            track += result[f"{category}_{mode}_score"].to_numpy() * weight
        result[f"baseline_{mode}"] = np.round(baseline, 2)
        result[f"health_{mode}"] = np.round(track, 2)
        result[f"composite_{mode}"] = np.round(0.60 * baseline + 0.40 * track, 2)

    result["baseline_score"] = result["baseline_walk"]
    result["track_score"] = result["health_walk"]
    result["composite_score"] = result["composite_walk"]
    return result


def add_districts(grid: gpd.GeoDataFrame, district_path: Path) -> gpd.GeoDataFrame:
    districts = read_file(district_path, crs=PROJECT_CRS)
    district_col = next((c for c in ["县级", "县", "name", "NAME", "区县"] if c in districts.columns), None)
    if district_col is None:
        grid["district"] = "Unknown"
        return grid
    centroids = gpd.GeoDataFrame(
        grid[["grid_id"]].copy(),
        geometry=gpd.points_from_xy(grid["centroid_x"], grid["centroid_y"]),
        crs=PROJECT_CRS,
    )
    joined = gpd.sjoin(centroids, districts[[district_col, "geometry"]], how="left", predicate="within")
    district_by_grid = joined.groupby("grid_id")[district_col].first()
    grid["district"] = grid["grid_id"].map(district_by_grid).fillna("Unknown")
    missing = grid["district"].eq("Unknown")
    if missing.any():
        fallback = gpd.sjoin(
            grid.loc[missing, ["grid_id", "geometry"]].copy(),
            districts[[district_col, "geometry"]],
            how="left",
            predicate="intersects",
        )
        fallback_by_grid = fallback.groupby("grid_id")[district_col].first()
        grid.loc[missing, "district"] = grid.loc[missing, "grid_id"].map(fallback_by_grid).fillna("Unknown")
    return grid


def add_housing_price(grid: gpd.GeoDataFrame, housing_points: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if housing_points.empty or "housing_price_proxy" not in housing_points.columns:
        grid["housing_price_proxy"] = np.nan
        grid["rent_band"] = "No AOI price proxy"
        return grid
    centroids_xy = grid[["centroid_x", "centroid_y"]].to_numpy()
    tree = cKDTree(xy_array(housing_points))
    dist, idx = tree.query(centroids_xy, k=1, workers=-1)
    price = pd.to_numeric(housing_points.iloc[idx]["housing_price_proxy"], errors="coerce").to_numpy(copy=True)
    price[dist > 2500] = np.nan
    grid["housing_price_proxy"] = np.round(price, 0)
    bins = [-np.inf, 40000, 80000, 120000, np.inf]
    labels = ["lower", "middle", "upper", "premium"]
    grid["rent_band"] = pd.cut(grid["housing_price_proxy"], bins=bins, labels=labels).astype("object")
    grid.loc[grid["housing_price_proxy"].isna(), "rent_band"] = "No nearby AOI price proxy"
    return grid


def add_h3_ids(grid: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    centroids = gpd.GeoSeries(
        gpd.points_from_xy(grid["centroid_x"], grid["centroid_y"]),
        crs=PROJECT_CRS,
    ).to_crs(WGS84)
    grid["lon"] = centroids.x
    grid["lat"] = centroids.y
    grid["h3_id"] = [h3.latlng_to_cell(lat, lon, H3_RESOLUTION) for lat, lon in zip(grid["lat"], grid["lon"])]
    return grid


def top_amenity_string(row: pd.Series, mode: str = "walk") -> str:
    labels = [
        ("food", "Food/retail"),
        ("healthcare", "Healthcare"),
        ("education", "Education"),
        ("sport", "Sport"),
        ("green_outdoor", "Green/outdoor"),
        ("transit_access", "Transit"),
    ]
    values = []
    for key, label in labels:
        col = f"{key}_{mode}_count"
        if col in row:
            values.append((float(row[col]), label))
    values.sort(reverse=True)
    return ", ".join(f"{label}: {int(round(value))}" for value, label in values[:3])


def most_common(series: pd.Series) -> str:
    mode = series.dropna().astype(str).mode()
    return mode.iloc[0] if len(mode) else "Unknown"


def h3_boundary(cell: str) -> Polygon:
    boundary = h3.cell_to_boundary(cell)
    return Polygon([(lng, lat) for lat, lng in boundary])


def aggregate_to_h3(grid: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    numeric_cols = [
        c
        for c in grid.columns
        if c not in {"geometry", "grid_id", "district", "rent_band"}
        and pd.api.types.is_numeric_dtype(grid[c])
    ]
    agg = {c: "mean" for c in numeric_cols}
    agg["grid_id"] = "count"
    h3_df = grid.groupby("h3_id").agg(agg).rename(columns={"grid_id": "grid_count"}).reset_index()
    h3_df["district"] = grid.groupby("h3_id")["district"].agg(most_common).reindex(h3_df["h3_id"]).values
    h3_df["rent_band"] = grid.groupby("h3_id")["rent_band"].agg(most_common).reindex(h3_df["h3_id"]).values
    h3_df["top_amenities"] = h3_df.apply(top_amenity_string, axis=1)
    for col in h3_df.select_dtypes(include=[np.number]).columns:
        if col not in {"grid_count"}:
            h3_df[col] = h3_df[col].round(2)
    h3_df["geometry"] = h3_df["h3_id"].apply(h3_boundary)
    h3_gdf = gpd.GeoDataFrame(h3_df, geometry="geometry", crs=WGS84)
    keep_first = [
        "h3_id",
        "district",
        "grid_count",
        "composite_score",
        "baseline_score",
        "track_score",
        "composite_walk",
        "composite_bike",
        "composite_transit",
        "composite_car",
        "baseline_walk",
        "baseline_bike",
        "baseline_transit",
        "baseline_car",
        "health_walk",
        "health_bike",
        "health_transit",
        "health_car",
        "sport_walk_score",
        "green_outdoor_walk_score",
        "cycling_env_walk_score",
        "healthy_food_walk_score",
        "env_quality_walk_score",
        "food_walk_count",
        "healthcare_walk_count",
        "education_walk_count",
        "sport_walk_count",
        "green_outdoor_walk_count",
        "transit_access_walk_count",
        "metro_dist_m",
        "major_road_dist_m",
        "housing_price_proxy",
        "rent_band",
        "top_amenities",
    ]
    ordered = [c for c in keep_first if c in h3_gdf.columns] + [
        c for c in h3_gdf.columns if c not in keep_first and c != "geometry"
    ] + ["geometry"]
    return h3_gdf[ordered]


def locate_paths() -> dict[str, Path]:
    return {
        "city_boundary": find_one(RAW / "admin", "2024 city boundary", ["2024", "市界"]),
        "district_boundary": find_one(RAW / "admin", "2024 district boundary", ["2024", "县界"]),
        "built_area_2020": find_one(RAW / "built_area", "2020 built-up area", ["2020"]),
        "bus_stops": find_one(RAW / "traffic", "bus stops", ["公交站点"]),
        "metro_stations": find_one(RAW / "traffic", "metro stations", ["地铁站"], ["出入口", "线"]),
        "metro_exits": find_one(RAW / "traffic", "metro exits", ["地铁出入口"]),
        "aoi": find_one(RAW / "aoi", "Baidu AOI polygons", ["AOI面"]),
        "landuse_webmap": find_one(RAW / "aoi", "landuse webmap", ["Landuse"]),
        "roads": RAW / "roads" / "shanghai-roads-simplified.parquet",
    }


def write_outputs(grid: gpd.GeoDataFrame, h3_gdf: gpd.GeoDataFrame, summary: dict) -> None:
    grid_out = PROCESSED / "shanghai_500m_health_grid.parquet"
    h3_out = OUTPUT / "shanghai_health_h3_r8.geojson"
    h3_app = APP_DATA / "shanghai_health_h3_r8.geojson"
    summary_out = OUTPUT / "summary.json"
    summary_app = APP_DATA / "summary.json"
    web_columns = [
        "h3_id",
        "district",
        "grid_count",
        "composite_score",
        "baseline_score",
        "track_score",
        "composite_walk",
        "composite_bike",
        "composite_transit",
        "composite_car",
        "baseline_walk",
        "health_walk",
        "food_walk_score",
        "healthcare_walk_score",
        "education_walk_score",
        "open_space_walk_score",
        "transit_access_walk_score",
        "civic_walk_score",
        "sport_walk_score",
        "green_outdoor_walk_score",
        "cycling_env_walk_score",
        "healthy_food_walk_score",
        "env_quality_walk_score",
        "food_walk_count",
        "healthcare_walk_count",
        "education_walk_count",
        "sport_walk_count",
        "green_outdoor_walk_count",
        "transit_access_walk_count",
        "metro_dist_m",
        "major_road_dist_m",
        "housing_price_proxy",
        "rent_band",
        "top_amenities",
        "geometry",
    ]

    grid.drop(columns=["lon", "lat"], errors="ignore").to_parquet(grid_out, index=False)
    h3_gdf.to_file(h3_out, driver="GeoJSON")
    h3_web = h3_gdf[[c for c in web_columns if c in h3_gdf.columns]].copy()
    h3_web.to_file(h3_app, driver="GeoJSON")
    summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_app.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"Wrote {grid_out.relative_to(ROOT)}")
    log(f"Wrote {h3_out.relative_to(ROOT)}")
    log(f"Wrote lightweight web data to {h3_app.relative_to(ROOT)}")
    log(f"Wrote {summary_out.relative_to(ROOT)}")
    log(f"Wrote {summary_app.relative_to(ROOT)}")


def main() -> None:
    started = time.time()
    load_env()
    ensure_dirs()
    paths = locate_paths()
    log("Located source layers:")
    for key, value in paths.items():
        log(f"  {key}: {value.relative_to(ROOT) if value.is_relative_to(ROOT) else value}")

    city = read_file(paths["city_boundary"], crs=PROJECT_CRS)
    city_union = union_geometry(city)
    city_mask = city.copy()
    city_mask["geometry"] = city_mask.geometry.make_valid()
    city_mask = city_mask[~city_mask.geometry.is_empty].copy()
    grid = create_500m_grid(city_mask, label="Shanghai administrative boundary")
    grid = add_districts(grid, paths["district_boundary"])

    poi_groups, poi_meta = load_poi_points()
    support_groups, support_meta = load_supporting_points(paths)
    groups = merge_groups(poi_groups, support_groups)
    group_counts = {k: int(len(v)) for k, v in groups.items()}
    log("Point/group counts: " + ", ".join(f"{k}={v:,}" for k, v in sorted(group_counts.items()) if v))

    grid = add_accessibility_scores(grid, groups)
    grid = add_housing_price(grid, groups.get("housing_price", gpd.GeoDataFrame(geometry=[])))
    grid = add_h3_ids(grid)
    h3_gdf = aggregate_to_h3(grid)

    summary = {
        "project": "15-Minute Shanghai - Track A Healthy Lifestyle & Sport",
        "generated_at": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(),
        "grid_size_m": GRID_SIZE_M,
        "h3_resolution": H3_RESOLUTION,
        "grid_cells": int(len(grid)),
        "h3_cells": int(len(h3_gdf)),
        "score_range": {
            "min": round(float(h3_gdf["composite_score"].min()), 2),
            "mean": round(float(h3_gdf["composite_score"].mean()), 2),
            "max": round(float(h3_gdf["composite_score"].max()), 2),
        },
        "paths": {k: str(v) for k, v in paths.items()},
        "poi": poi_meta,
        "supporting_data": support_meta,
        "group_counts": group_counts,
        "method_notes": [
            "500 m cells are generated inside the Shanghai administrative boundary so coastal districts, Changxing Island, and Chongming Island remain visible.",
            "The 2020 built-up area layer is retained as a source reference, but it is not used to remove low-density island or coastal cells from the web map.",
            "15-minute access is modelled with mode-specific Euclidean catchments: walk 1.2 km, bike 3.5 km, transit 2.5 km, car 5 km.",
            "Road-network data are used for cycling environment and major-road environmental penalty; full Dijkstra is left as a notebook extension because no complete travel-time network is supplied for all modes.",
            "AOI price is used only as a housing/rent-band proxy for the web detail panel.",
        ],
        "runtime_seconds": round(time.time() - started, 1),
    }
    write_outputs(grid, h3_gdf, summary)
    log("Done.")


if __name__ == "__main__":
    main()
