from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT / ".deps"
if DEPS.exists():
    sys.path.insert(0, str(DEPS))

import geopandas as gpd
import pandas as pd

WGS84 = "EPSG:4326"
POI_2024_DIRNAME = "POI 2024"
CLASSIFIED_SUBDIR = "csv格式/已分类"
POI_2024_COLUMNS = [
    "id",
    "name",
    "address",
    "bigType",
    "midType",
    "smallType",
    "typecode",
    "wgs84Lng",
    "wgs84Lat",
    "adname",
    "adcode",
]
CHUNK_SIZE = 100_000

CATEGORY_FILES = {
    "food_shop": "购物服务",
    "food_dining": "餐饮服务",
    "healthcare": "医疗保健服务",
    "education": "科教文化服务",
    "civic_gov": "政府机构及社会团体",
    "civic_public": "公共设施",
    "transit": "交通设施服务",
    "sport": "体育休闲服务",
    "scenic": "风景名胜",
}

SPORT_INCLUDE_KEYWORDS = [
    "体育",
    "运动",
    "健身",
    "健身房",
    "体育馆",
    "球馆",
    "球场",
    "篮球",
    "足球",
    "网球",
    "羽毛球",
    "乒乓球",
    "游泳",
    "游泳馆",
    "瑜伽",
    "舞蹈",
    "武术",
    "跆拳道",
    "高尔夫",
    "台球",
    "跑步",
    "跑道",
    "溜冰",
    "攀岩",
]
SPORT_EXCLUDE_KEYWORDS = [
    "KTV",
    "ktv",
    "会所",
    "酒吧",
    "洗浴",
    "桑拿",
    "足疗",
    "按摩",
    "棋牌",
    "影城",
    "游戏厅",
    "娱乐场所",
]
OPEN_SPACE_KEYWORDS = [
    "公园",
    "口袋公园",
    "广场",
    "绿地",
    "湿地",
    "森林",
    "滨江",
    "滨水",
    "植物园",
    "花园",
    "风景",
    "景区",
]
HEALTHY_FOOD_KEYWORDS = [
    "菜市场",
    "农贸",
    "生鲜",
    "水果",
    "蔬菜",
    "果蔬",
    "超市",
    "便利店",
    "市场",
]
EDUCATION_KEYWORDS = [
    "学校",
    "小学",
    "中学",
    "初中",
    "高中",
    "幼儿园",
    "托育",
    "托儿",
    "大学",
    "学院",
    "职业",
    "早教",
]
TRANSIT_INCLUDE_KEYWORDS = [
    "地铁",
    "轨道",
    "轻轨",
    "公交",
    "客运",
    "火车",
    "高铁",
    "车站",
    "渡口",
    "轮渡",
    "码头",
]
TRANSIT_EXCLUDE_KEYWORDS = [
    "停车",
    "停车场",
    "充电",
    "加油",
    "加气",
    "服务区",
    "收费站",
    "洗车",
    "维修",
]


def _empty_groups() -> dict[str, list[gpd.GeoDataFrame]]:
    return {
        "food": [],
        "healthcare": [],
        "education": [],
        "open_space": [],
        "transit_access": [],
        "civic": [],
        "sport": [],
        "green_outdoor": [],
        "healthy_food": [],
    }


def _classified_dir(raw_dir: Path) -> Path:
    return raw_dir / POI_2024_DIRNAME / CLASSIFIED_SUBDIR


def _category_paths(raw_dir: Path) -> dict[str, Path]:
    classified_dir = _classified_dir(raw_dir)
    paths: dict[str, Path] = {}
    if not classified_dir.exists():
        return paths
    for key, category in CATEGORY_FILES.items():
        matches = sorted(classified_dir.glob(f"*-{category}.csv"))
        if matches:
            paths[key] = matches[0]
    return paths


def _text_frame(df: pd.DataFrame) -> pd.Series:
    cols = [c for c in ["name", "address", "bigType", "midType", "smallType"] if c in df.columns]
    if not cols:
        return pd.Series([""] * len(df), index=df.index)
    return df[cols].fillna("").astype(str).agg(" ".join, axis=1)


def _keyword_mask(text: pd.Series, keywords: list[str]) -> pd.Series:
    if not keywords:
        return pd.Series(False, index=text.index)
    pattern = "|".join(keywords)
    return text.str.contains(pattern, case=False, regex=True, na=False)


def _read_filtered_csv(
    path: Path,
    project_crs: str,
    include_keywords: list[str] | None = None,
    exclude_keywords: list[str] | None = None,
    source_label: str | None = None,
) -> tuple[gpd.GeoDataFrame, dict[str, int | str]]:
    include_keywords = include_keywords or []
    exclude_keywords = exclude_keywords or []
    rows_loaded = 0
    frames: list[pd.DataFrame] = []

    for chunk in pd.read_csv(
        path,
        usecols=POI_2024_COLUMNS,
        dtype=str,
        encoding="utf-8",
        chunksize=CHUNK_SIZE,
    ):
        rows_loaded += len(chunk)
        chunk = chunk.dropna(subset=["wgs84Lng", "wgs84Lat"]).copy()
        chunk["wgs84Lng"] = pd.to_numeric(chunk["wgs84Lng"], errors="coerce")
        chunk["wgs84Lat"] = pd.to_numeric(chunk["wgs84Lat"], errors="coerce")
        chunk = chunk[chunk["wgs84Lng"].between(120, 123) & chunk["wgs84Lat"].between(30, 33)].copy()
        if chunk.empty:
            continue
        text = _text_frame(chunk)
        if include_keywords:
            chunk = chunk[_keyword_mask(text, include_keywords)].copy()
            text = text.loc[chunk.index]
        if exclude_keywords and not chunk.empty:
            chunk = chunk[~_keyword_mask(text, exclude_keywords)].copy()
        if not chunk.empty:
            frames.append(chunk)

    if not frames:
        empty = gpd.GeoDataFrame({"source": []}, geometry=[], crs=project_crs)
        return empty, {"file": path.name, "rows_loaded": rows_loaded, "rows_selected": 0}

    df = pd.concat(frames, ignore_index=True).drop_duplicates(subset="id", keep="first")
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["wgs84Lng"], df["wgs84Lat"]),
        crs=WGS84,
    ).to_crs(project_crs)
    gdf["source"] = source_label or path.stem
    return gdf, {"file": path.name, "rows_loaded": rows_loaded, "rows_selected": int(len(gdf))}


def _append(groups: dict[str, list[gpd.GeoDataFrame]], group: str, gdf: gpd.GeoDataFrame) -> None:
    if not gdf.empty:
        groups[group].append(gdf.copy())


def load_poi_2024_points(raw_dir: Path, project_crs: str) -> tuple[dict[str, list[gpd.GeoDataFrame]], dict]:
    groups = _empty_groups()
    category_paths = _category_paths(raw_dir)
    base_dir = raw_dir / POI_2024_DIRNAME
    meta: dict[str, object] = {
        "poi_source": "POI 2024 classified CSVs",
        "poi_dir": str(base_dir),
        "poi_status": "not found",
        "poi_rows_loaded": 0,
        "files_used": [],
    }
    if not category_paths:
        return groups, meta

    def record(key: str, stats: dict[str, int | str], extras: dict[str, int] | None = None) -> None:
        item = {"source_key": key, **stats}
        if extras:
            item.update(extras)
        meta["files_used"].append(item)
        meta["poi_rows_loaded"] = int(meta["poi_rows_loaded"]) + int(stats.get("rows_selected", 0))

    shopping_path = category_paths.get("food_shop")
    if shopping_path:
        shopping, stats = _read_filtered_csv(shopping_path, project_crs, source_label="POI 2024 shopping")
        _append(groups, "food", shopping)
        healthy_food = shopping[_keyword_mask(_text_frame(shopping), HEALTHY_FOOD_KEYWORDS)].copy()
        _append(groups, "healthy_food", healthy_food)
        record("food_shop", stats, {"healthy_food_rows": int(len(healthy_food))})

    dining_path = category_paths.get("food_dining")
    if dining_path:
        dining, stats = _read_filtered_csv(dining_path, project_crs, source_label="POI 2024 dining")
        _append(groups, "food", dining)
        record("food_dining", stats)

    healthcare_path = category_paths.get("healthcare")
    if healthcare_path:
        healthcare, stats = _read_filtered_csv(healthcare_path, project_crs, source_label="POI 2024 healthcare")
        _append(groups, "healthcare", healthcare)
        record("healthcare", stats)

    education_path = category_paths.get("education")
    if education_path:
        education, stats = _read_filtered_csv(
            education_path,
            project_crs,
            include_keywords=EDUCATION_KEYWORDS,
            source_label="POI 2024 education",
        )
        _append(groups, "education", education)
        record("education", stats)

    civic_gov_path = category_paths.get("civic_gov")
    if civic_gov_path:
        civic_gov, stats = _read_filtered_csv(civic_gov_path, project_crs, source_label="POI 2024 civic government")
        _append(groups, "civic", civic_gov)
        record("civic_gov", stats)

    civic_public_path = category_paths.get("civic_public")
    if civic_public_path:
        civic_public, stats = _read_filtered_csv(civic_public_path, project_crs, source_label="POI 2024 public facilities")
        _append(groups, "civic", civic_public)
        record("civic_public", stats)

    transit_path = category_paths.get("transit")
    if transit_path:
        transit, stats = _read_filtered_csv(
            transit_path,
            project_crs,
            include_keywords=TRANSIT_INCLUDE_KEYWORDS,
            exclude_keywords=TRANSIT_EXCLUDE_KEYWORDS,
            source_label="POI 2024 transit",
        )
        _append(groups, "transit_access", transit)
        record("transit", stats)

    scenic_path = category_paths.get("scenic")
    if scenic_path:
        scenic, stats = _read_filtered_csv(scenic_path, project_crs, source_label="POI 2024 scenic")
        _append(groups, "open_space", scenic)
        _append(groups, "green_outdoor", scenic)
        record("scenic", stats)

    sport_path = category_paths.get("sport")
    if sport_path:
        sport_raw, stats = _read_filtered_csv(sport_path, project_crs, source_label="POI 2024 sport raw")
        sport_text = _text_frame(sport_raw)
        sport = sport_raw[
            _keyword_mask(sport_text, SPORT_INCLUDE_KEYWORDS)
            & ~_keyword_mask(sport_text, SPORT_EXCLUDE_KEYWORDS)
        ].copy()
        sport_parks = sport_raw[_keyword_mask(sport_text, OPEN_SPACE_KEYWORDS)].copy()
        _append(groups, "sport", sport)
        _append(groups, "open_space", sport_parks)
        _append(groups, "green_outdoor", sport_parks)
        record(
            "sport",
            stats,
            {"sport_rows": int(len(sport)), "park_like_rows": int(len(sport_parks))},
        )

    meta["group_row_counts"] = {
        key: int(sum(len(frame) for frame in frames))
        for key, frames in groups.items()
        if frames
    }
    meta["poi_status"] = "loaded" if meta["group_row_counts"] else "no filtered rows matched"
    return groups, meta
