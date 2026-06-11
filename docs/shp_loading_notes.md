# Shanghai POI Shapefile Loading Notes

The supplied local `Shp` folder is a strong primary POI source for this project. It contains WGS84 point shapefiles grouped by Gaode-style industry categories.

## Why This Source Helps

- It directly covers many baseline categories: food, healthcare, education, public services, transport, and retail.
- It directly supports Track A categories: sport/leisure, fitness, parks/scenic spots, fresh food, and health-related services.
- It includes district fields (`adcode`, `adname`) that can support district-level summaries.
- It includes `type`, `typecode`, `行业大`, `行业中`, and `行业小`, which are better for classification than filename alone.

## Path Handling

Use a raw string, forward slashes, or `.env` configuration. Avoid plain backslashes in Python strings because sequences such as `\x` can be interpreted as escape codes.

Good:

```python
Path(r"D:\21570\wechat_files\xwechat_files\...\Shp")
Path("D:/21570/wechat_files/xwechat_files/.../Shp")
```

Risky:

```python
Path("D:\21570\wechat_files\xwechat_files\...\Shp")
```

Recommended project setting:

```text
SHANGHAI_POI_SHP_DIR=D:/21570/wechat_files/xwechat_files/wxid_58oway7w5m2s12_81f1/msg/file/2026-06/Shp
```

Put that line in a local `.env` file, not in GitHub.

## Output Files

The notebook should create:

```text
data/processed/all_pois.gpkg
data/processed/poi_category_inventory.csv
data/processed/baseline_pois.gpkg
data/processed/track_a_pois.gpkg
```

These processed files become the input for grid accessibility scoring.

