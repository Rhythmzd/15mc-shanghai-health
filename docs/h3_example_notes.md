# H3 Example Notebook Notes

Source file:

`H3 example urban_analytics.ipynb`

The example notebook demonstrates H3 spatial indexing on urban data from Toulouse, France. It is useful for this project because it shows how to move from point-level urban data to hexagonal aggregation and deck.gl-style visualization.

## Useful Ideas for This Project

1. Assign each point or grid centroid to an H3 cell.
2. Convert H3 cells to polygon boundaries for GeoJSON export.
3. Aggregate point or grid values by H3 ID.
4. Use H3 neighborhood functions for optional spatial QA.
5. Use `H3HexagonLayer` in pydeck/deck.gl for interactive 2D or 3D previews.

## Version Difference

The example notebook uses old H3 Python API names from `h3==3.6.4`. This project uses `h3>=4.0`, so code should use the newer names.

| Old API in Example | New API for This Project |
| --- | --- |
| `h3.geo_to_h3(lat, lng, resolution)` | `h3.latlng_to_cell(lat, lng, resolution)` |
| `h3.h3_to_geo_boundary(h, geo_json=True)` | `h3.cell_to_boundary(cell)` |
| `h3.h3_to_geo(h)` | `h3.cell_to_latlng(cell)` |
| `h3.h3_to_children(h)` | `h3.cell_to_children(cell)` |
| `h3.k_ring(h, k)` | `h3.grid_disk(cell, k)` |
| `h3.hex_ring(h, k)` | `h3.grid_ring(cell, k)` |
| `h3.polyfill(...)` | `h3.polygon_to_cells(...)` or `h3.h3shape_to_cells(...)` |

## How We Use It

For the Shanghai project, H3 is mainly the final display and aggregation layer:

```text
500 m grid scores
-> assign each grid centroid to H3 resolution 8
-> average scores and indicators by h3_id
-> convert h3_id to polygon geometry
-> export shanghai_health_h3_r8.geojson
-> load in React + deck.gl H3HexagonLayer
```

The example notebook also includes more advanced topics such as spatial autocorrelation and TensorFlow classifiers. Those are interesting but not necessary for the course deliverable, so they are not part of the MVP.

