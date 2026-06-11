# Downloaded Dataset Inventory

These datasets were downloaded from the shared `2025-data-analysis-project` Baidu Netdisk folder and extracted into:

```text
data/raw/
```

## Extraction Summary

| Archive | Extracted Folder | Main Contents | Project Use |
| --- | --- | --- | --- |
| `03-admin.rar` | `data/raw/admin` | Shanghai city, district, township, community boundaries | study boundary, district summaries, grid clipping |
| `04-traffic.rar` | `data/raw/traffic` | metro stations/exits/lines, bus stops/routes, parking, bridges/tunnels, bike-share Excel files | public transport access, nearest metro, transit context |
| `08-AOI.zip` | `data/raw/aoi` | Baidu AOI polygons and webmap landuse polygons | land-use context, named activity areas |
| `11-built area.rar` | `data/raw/built_area` | built-up area polygons for 1990, 2000, 2010, 2020 | restrict analysis to built-up urban area |
| `09-landuse.rar` | `data/raw/landuse` | ESA 10 m land-use data, GLC 30 m land-use rasters for 2000/2010/2020, construction land classification | green/open-space context, built land, land-use validation |
| `10-AI interpreted data archive` | `data/raw/ai_interpreted` | AI-interpreted building, water, green space, and road-network shapefiles by Shanghai district group | Track A green-space proxy, road-network supplement, built environment context |
| `shanghai-roads-simplified.parquet` | `data/raw/roads` | simplified road network with OSM-style attributes and geometry | walking/cycling/car network analysis and isochrone fallback |

## File Type Counts After Extraction

| File Type | Count |
| --- | ---: |
| `.shp` | 86 |
| `.tif` | 4 |
| `.csv` | 4 |
| `.xlsx` | 2 |
| `.xls` | 1 |
| `.parquet` | 1 |
| `.json` | 2 |
| `.pdf` | 5 |
| `.png` | 5 |
| `.txt` | 3 |

## Priority Files for the Current Project

### Boundary and Grid

Use first:

```text
data/raw/admin/.../2024/[Shanghai city boundary].shp
data/raw/admin/.../2024/[Shanghai district boundary].shp
data/raw/admin/.../2024/[Shanghai township boundary].shp
data/raw/built_area/.../[Shanghai built-up area 2020].shp
```

Why:

- The city boundary defines the study area.
- The district boundary supports district-level summaries.
- The township boundary supports finer contextual maps.
- The 2020 built-up area can remove non-urban or undeveloped areas from the 500 m grid.

### Transit and Mobility

Use first:

```text
data/raw/traffic/.../[bus stops].shp
data/raw/traffic/.../[bus routes].shp
data/raw/traffic/.../[metro stations].shp
data/raw/traffic/.../[metro exits].shp
data/raw/traffic/.../[open-source metro lines].shp
data/raw/traffic/.../[bike-share GCJ-02 table].xlsx
data/raw/roads/shanghai-roads-simplified.parquet
```

Why:

- Supports baseline public transport access.
- Supports hex detail panel fields such as nearest metro distance.
- Bike-share data may be useful for Track A mobility context, but note that it uses GCJ-02/Mars coordinates and may need coordinate conversion before spatial joins.
- The road Parquet is useful for route/network fallback calculations because it contains `highway`, `bicycle`, `bicycle_safety`, `foot`, `foot_safety`, `max_speed`, `motorcar`, `geometry`, and `edge_id`.

### Land Use, Green Space, and Built Environment

Use first:

```text
data/raw/aoi/.../[landuse webmap].shp
data/raw/aoi/.../[Baidu AOI polygons].shp
data/raw/landuse/.../ESA/TIF/[ESA 10m land-use raster].tif
data/raw/landuse/.../ESA/SHP/[ESA 10m land-use polygons].shp
data/raw/landuse/.../[construction land classification].shp
```

Why:

- Supports green/open-space indicators.
- Helps validate whether parks and sport deserts are in built-up, agricultural, or industrial land.
- ESA 10 m raster/vector is useful for land-cover proportions within H3 cells.

### AI-Interpreted Green Space and Roads

Use first:

```text
data/raw/ai_interpreted/.../*[green space].shp
data/raw/ai_interpreted/.../*[road network].shp
```

Why:

- Green-space polygons can support Track A's green/outdoor activity score.
- Road-network layers can supplement walkability/cycling context.
- Building layers are useful for urban density context but are not essential for the MVP.

## Notes and Caveats

- Most `.cpg` files declare UTF-8. Read shapefiles with `encoding="utf-8"` when using GeoPandas.
- Some traffic/bike-share files use GCJ-02/Mars coordinates. They should not be mixed with WGS84 layers without coordinate conversion.
- Large land-use shapefiles and AI road-network shapefiles may be heavy. For the MVP, prefer targeted layers instead of loading everything at once.
- Raw datasets should not be committed to GitHub because of file size and licensing uncertainty.
