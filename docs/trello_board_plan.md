# Trello Board Plan

Board name:

```text
15MC Shanghai - [Your Name]
```

## Columns

1. Backlog
2. Sprint 1 - Week 1
3. Sprint 2 - Week 2
4. Sprint 3 - Week 3
5. Sprint 4 - Week 4
6. Sprint 5 - Week 5
7. Done
8. Blocked

## Labels

- Data: red
- Analysis: yellow
- App: green
- Literature: blue
- Review: purple

## Sprint 1 - Literature and Environment

### Read 15-minute city literature

Label: Literature

Definition of Done:

- At least four academic sources are logged.
- Notes cover accessibility measurement and equity critique.
- A draft literature review is added to `01_data_collection.ipynb`.

Checklist:

- Read Moreno et al. 2021.
- Read one Shanghai 15-minute life circle article.
- Read one supply-demand/equity article.
- Read one critique of 15-minute city/gentrification.
- Write citation notes.

### Create project repository structure

Label: Review

Definition of Done:

- Repository has notebooks, data, docs, and app folders.
- `.gitignore`, `README.md`, and `requirements.txt` are present.
- Data folders do not expose sensitive or large data.

Checklist:

- Create folder structure.
- Add requirements.
- Add data provenance log.
- Add method notes.

### Define baseline and Track A indicators

Label: Analysis

Definition of Done:

- Six baseline indicators are documented.
- Track A scoring indicators and weights are documented.
- Assumptions are stated clearly.

Checklist:

- Map baseline indicators to data categories.
- Map Track A indicators to data categories.
- Document scoring formula.

## Sprint 2 - Data Collection and Grid

### Download or collect Shanghai boundary

Label: Data

Definition of Done:

- Shanghai boundary is saved in `data/raw/`.
- CRS and license are recorded.
- Boundary is validated and plotted.

Checklist:

- Find boundary source.
- Save raw file.
- Reproject to a metric CRS.
- Write validation notes.

### Collect OSM streets and POIs

Label: Data

Definition of Done:

- Streets, POIs, parks, cycleways, and transit stops are collected.
- POI categories are mapped to baseline and Track A indicators.
- Data source date is logged.

Checklist:

- Download OSM extract or query OSMnx.
- Extract baseline POIs.
- Extract Track A POIs.
- Save cleaned GeoPackage/Parquet.

### Build 500 m grid

Label: Analysis

Definition of Done:

- 500 m grid covers the Shanghai boundary.
- Each cell has a unique ID and center point.
- Grid is saved in `data/processed/`.

Checklist:

- Reproject boundary.
- Generate square grid.
- Clip to Shanghai boundary.
- Calculate centroids.

## Sprint 3 - Isochrones, Joins, and Scoring

### Compute 15-minute accessibility by mode

Label: Analysis

Definition of Done:

- Walk, bike, transit, and car accessibility fields exist.
- All API/network results are cached.
- Car is marked as comparison-only.

Checklist:

- Implement walk accessibility.
- Implement bike accessibility.
- Implement transit accessibility.
- Implement car comparison accessibility.
- Cache outputs.

### Join POIs to isochrones

Label: Analysis

Definition of Done:

- Each grid cell has baseline indicator counts.
- Each grid cell has Track A indicator counts or values.
- Spot checks are documented.

Checklist:

- Spatial join baseline POIs.
- Spatial join sport POIs.
- Calculate cycleway length.
- Add NDVI and AQI fields if available.

### Calculate baseline and Track A scores

Label: Analysis

Definition of Done:

- Baseline score is 0-100.
- Health score is 0-100.
- Composite score is 0-100.
- Weighting rationale is documented.

Checklist:

- Normalize indicators.
- Apply group weights.
- Check score distributions.
- Save scored grid.

## Sprint 4 - H3 and App Skeleton

### Aggregate grid scores to H3 r8

Label: Analysis

Definition of Done:

- H3 resolution 8 cells are generated.
- Scores and indicators are aggregated.
- `shanghai_health_h3_r8.geojson` is exported.

Checklist:

- Assign grid centers to H3 IDs.
- Aggregate mean scores.
- Convert H3 cells to polygons.
- Export GeoJSON.

### Build web app skeleton

Label: App

Definition of Done:

- Map loads local GeoJSON.
- H3 cells are colored by score.
- Basic responsive layout works.

Checklist:

- Create React app.
- Add Mapbox/deck.gl.
- Load H3 GeoJSON.
- Add legend and loading state.

## Sprint 5 - App Completion and Demo

### Add app interactions

Label: App

Definition of Done:

- Mode toggle works.
- Baseline/Track layer toggle works.
- Hex click detail panel works.
- Recommender highlights top 10 hexes.
- Data transparency panel is visible.

Checklist:

- Add mode toggle.
- Add layer toggle.
- Add click panel.
- Add priority sliders.
- Add transparency panel.

### Optimize and deploy app

Label: App

Definition of Done:

- Public URL is deployed.
- App loads in under 4 seconds on a typical connection.
- Mobile viewport is checked.

Checklist:

- Reduce GeoJSON size if needed.
- Test desktop viewport.
- Test mobile viewport.
- Deploy to Vercel.
- Save deployment URL.

### Final review

Label: Review

Definition of Done:

- Notebooks run in order.
- Data provenance is complete.
- Trello board shows real sprint movement.
- Demo script is ready.

Checklist:

- Run notebooks from clean kernel.
- Check README.
- Check app.
- Ask peer for feedback.
- Prepare final demo.

