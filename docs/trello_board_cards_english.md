# Trello Board Content - 15MC Shanghai

Board name:

```text
15MC Shanghai - [Your Name]
```

Recommended lists:

```text
Backlog
Sprint 1 - Week 1
Sprint 2 - Week 2
Sprint 3 - Week 3
Sprint 4 - Week 4
Sprint 5 - Week 5
Done
Blocked
```

Recommended labels:

```text
Data - red
Analysis - yellow
App - green
Literature - blue
Review - purple
```

Suggested due dates assume Week 1 ends on 2026-06-12. If your course calendar uses another Week 1 date, keep the same Friday-of-week pattern and shift all dates together.

---

## Backlog

### Card: Add real network-routing sensitivity test

Label: Analysis

Due date: 2026-07-10

Description:

Extend the current Euclidean 15-minute catchment method with a real road-network sensitivity test. This is a stretch task because the current deliverable already uses mode-specific distance catchments and road-network attributes, but full Dijkstra routing would make the isochrone method stronger.

Definition of Done:

- A small sample of origins is tested with network-based walking, cycling, and car service areas.
- Results are compared with the current catchment method.
- Limitations are documented in the final notebook or README.

Checklist:

- Review `shanghai-network-extract.ipynb`.
- Select 5-10 representative grid origins.
- Build or load a routable graph from the road parquet.
- Run Dijkstra travel-time search for at least one mode.
- Compare network polygons with current 15-minute distance buffers.
- Add a short sensitivity note to `02_grid_isochrones.ipynb`.

---

### Card: Add public deployment URL

Label: App

Due date: 2026-07-10

Description:

Deploy the static web application to a public URL so the final H3 map can be opened without running a local server. The app folder is already static and can be deployed to Vercel, Netlify, or GitHub Pages.

Definition of Done:

- Public URL is available.
- The H3 GeoJSON loads correctly from `app/data`.
- The map, toggles, click panel, recommender, and transparency panel work online.

Checklist:

- Create or use a Vercel/GitHub account.
- Upload or connect the project repository.
- Set the deployment root to `app`.
- Test the deployed URL on desktop.
- Test the deployed URL on mobile.
- Add the final URL to README and final submission notes.

---

### Card: Add district comparison and equity summary

Label: Analysis

Due date: 2026-07-10

Description:

Extend the final analysis with a short district-level comparison so the project does not only show top-scoring hexagons. This task focuses on spatial inequality and helps explain the difference between the city center, suburban districts, and peripheral areas.

Definition of Done:

- District-level mean score table is added.
- High-score and low-score districts are briefly interpreted.
- A short equity note is added to the final notebook or README.

Checklist:

- Group H3 cells by district.
- Calculate mean composite, baseline, and Track A scores.
- Identify the highest and lowest districts.
- Compare central and suburban patterns.
- Write a short interpretation note.

---

### Card: Export presentation-ready static figures

Label: Review

Due date: 2026-07-10

Description:

Prepare a few clean static figures from the notebooks or app outputs for presentation, submission backup, or demo slides. These figures should summarize the H3 map, district comparison, and one example of local detail.

Definition of Done:

- At least three static figures are exported.
- Figures are readable in presentation format.
- File paths are documented.

Checklist:

- Export one full-city H3 choropleth.
- Export one district comparison chart or table image.
- Export one detail view or recommender view screenshot.
- Save figures in a documented folder.
- Check readability on a slide-sized canvas.

---

## Sprint 1 - Week 1

### Card: Read 15-minute city literature

Label: Literature

Due date: 2026-06-12

Description:

Review the core 15-minute city literature and identify how proximity, accessibility, equity, and urban heterogeneity should shape the Shanghai analysis. The literature notes will support the top markdown cell of `01_data_collection.ipynb`.

Definition of Done:

- At least four relevant sources are logged.
- Notes cover accessibility measurement, neighborhood heterogeneity, and healthy-lifestyle planning.
- An approximately 800-word literature review is drafted in `01_data_collection.ipynb`.

Checklist:

- Summarize the 15-minute city concept.
- Review the Paris heterogeneity paper supplied for the project.
- Add notes on Shanghai 15-minute community life circles.
- Add notes on walkability, cycling, and public-health access.
- Draft the literature review in English.

---

### Card: Set up project repository structure

Label: Review

Due date: 2026-06-12

Description:

Create a clean project structure for the notebooks, raw data, processed outputs, web app, and documentation. The structure must make the workflow reproducible from raw data to final H3 GeoJSON.

Definition of Done:

- Repository contains `notebooks`, `scripts`, `data/raw`, `data/processed`, `data/output`, `app`, and `docs`.
- README explains the project question, scoring approach, and outputs.
- `.gitignore` protects API keys and large raw data.

Checklist:

- Create folder structure.
- Add `README.md`.
- Add `.gitignore`.
- Add `requirements.txt`.
- Add `.env.example`.
- Add documentation folder.

---

### Card: Define baseline and Track A indicators

Label: Analysis

Due date: 2026-06-12

Description:

Translate the assignment track into measurable indicators. The project uses six baseline 15-minute city indicators and five Track A Healthy Lifestyle & Sport indicators.

Definition of Done:

- Baseline indicators are documented.
- Track A indicators and weights are documented.
- Assumptions are clearly stated in methodology notes.

Checklist:

- Define baseline food and daily retail access.
- Define healthcare access.
- Define education and childcare access.
- Define public open space access.
- Define public transport access.
- Define civic and community service access.
- Define sport, green/outdoor, cycling, healthy food, and environmental quality indicators.
- Write the composite score formula.

---

### Card: Create Trello board and invite instructor

Label: Review

Due date: 2026-06-12

Description:

Set up the Trello board as a solo agile project management space. The board should show sprint columns, clear cards, labels, due dates, and project movement over time.

Definition of Done:

- Board is named `15MC Shanghai - [Your Name]`.
- Instructor is invited as a board member.
- Lists and labels match the assignment requirements.

Checklist:

- Create board.
- Add lists from Backlog to Blocked.
- Create labels: Data, Analysis, App, Literature, Review.
- Invite instructor.
- Add first sprint cards.

---

## Sprint 2 - Week 2

### Card: Inventory downloaded Shanghai datasets

Label: Data

Due date: 2026-06-19

Description:

Inspect the downloaded Shanghai datasets and decide which files are relevant for the Healthy Lifestyle & Sport track. This includes administrative boundaries, traffic, AOI, built-up area, land use, AI-interpreted features, roads, and POI shapefiles.

Definition of Done:

- All downloaded folders are listed with file counts.
- Relevant layers are identified.
- Source notes are saved in documentation.

Checklist:

- Inspect `03-admin`.
- Inspect `04-traffic`.
- Inspect `08-AOI`.
- Inspect `09-landuse`.
- Inspect `10-AI interpreted data`.
- Inspect `11-built area`.
- Inspect `shanghai-roads-simplified.parquet`.
- Record source roles in `docs/data_sources.md`.

---

### Card: Load and validate POI shapefiles

Label: Data

Due date: 2026-06-19

Description:

Load the Gaode POI shapefiles and map major categories to baseline and Track A indicators. The POI data provide food, healthcare, education, sport, civic, and transport-related amenity points.

Definition of Done:

- POI folder path is stored in `.env`.
- Selected POI categories are counted and validated.
- POI categories are mapped to scoring groups.

Checklist:

- Load all POI shapefiles from the `Shp` folder.
- Check CRS and geometry type.
- Count records by major category.
- Select categories for baseline indicators.
- Select categories for Track A indicators.
- Document category mapping in `01_data_collection.ipynb`.

---

### Card: Validate boundary, built-up area, and district layers

Label: Data

Due date: 2026-06-19

Description:

Use the 2024 Shanghai administrative layers and 2020 built-up area layer to define the spatial study area. The 500 m grid should be generated inside the built-up area rather than the full rectangular bounding box.

Definition of Done:

- City boundary, district boundary, and built-up area layers load successfully.
- CRS is checked and converted to a projected metric CRS.
- District names can be joined to grid cells.

Checklist:

- Load 2024 city boundary.
- Load 2024 district boundary.
- Load 2020 built-up area.
- Reproject to EPSG:4576.
- Check geometry validity.
- Confirm district label field.

---

### Card: Build 500 m analysis grid

Label: Analysis

Due date: 2026-06-19

Description:

Generate the 500 m grid used as the calculation surface. Each cell represents a potential local origin for the 15-minute accessibility analysis.

Definition of Done:

- Grid covers the 2020 built-up area.
- Each grid cell has a unique ID and centroid.
- Grid is saved to `data/processed`.

Checklist:

- Reproject built-up area to EPSG:4576.
- Generate 500 m square cells.
- Keep cells intersecting the built-up area.
- Add centroid coordinates.
- Add district labels.
- Save grid cache.

---

## Sprint 3 - Week 3

### Card: Prepare road-network travel-time fields

Label: Analysis

Due date: 2026-06-26

Description:

Use the supplied Shanghai road parquet and the logic from `shanghai-network-extract.ipynb` to calculate road length and approximate mode-specific travel times.

Definition of Done:

- Road edges load from parquet.
- Length, walking time, cycling time, and car time are calculated.
- Road filters for foot, bike, and car are documented.

Checklist:

- Load `shanghai-roads-simplified.parquet`.
- Calculate edge length in meters.
- Calculate walking time using 1.33 m/s.
- Calculate cycling time using 3.05 m/s.
- Calculate car time using 8.30 m/s.
- Filter foot, bike, and car eligible edges.
- Add road summary to notebook.

---

### Card: Compute four-mode accessibility scores

Label: Analysis

Due date: 2026-06-26

Description:

Calculate 15-minute accessibility for walking, cycling, transit, and car. The MVP uses mode-specific catchment distances and nearest/count metrics for each amenity group.

Definition of Done:

- Each 500 m grid cell has walk, bike, transit, and car scores.
- Amenity counts and nearest distances are calculated.
- Method limitations are documented.

Checklist:

- Build KDTree indexes for amenity groups.
- Compute nearest amenity distance.
- Compute amenity counts within mode radii.
- Apply walk radius of 1.2 km.
- Apply bike radius of 3.5 km.
- Apply transit radius of 2.5 km.
- Apply car radius of 5 km.
- Save scored grid to parquet.

---

### Card: Calculate baseline and Track A scores

Label: Analysis

Due date: 2026-06-26

Description:

Convert accessibility fields into the final scoring model. The baseline score measures everyday 15-minute services, while the Track A score measures healthy lifestyle and sport access.

Definition of Done:

- Baseline score is calculated from six indicators.
- Track A score is calculated from five indicators.
- Composite score is calculated as 60% baseline and 40% Track A.

Checklist:

- Normalize category distance and count measures.
- Apply baseline weights.
- Apply Track A weights.
- Calculate composite score.
- Check score distribution.
- Save results to `data/processed/shanghai_500m_health_grid.parquet`.

---

### Card: Expand and document notebooks

Label: Review

Due date: 2026-06-26

Description:

Make the three notebooks readable as final coursework deliverables. They should show the workflow step by step rather than only calling one script.

Definition of Done:

- `01_data_collection.ipynb` contains source validation and literature review.
- `02_grid_isochrones.ipynb` contains grid, road-network, and four-mode accessibility workflow.
- `03_scoring_h3.ipynb` contains scoring, H3 aggregation, and export workflow.

Checklist:

- Add markdown section headings.
- Add validation tables.
- Add road-network preparation cells.
- Add H3 metadata and hierarchy cells.
- Check that all code cells parse.
- Confirm notebooks match the assignment deliverable names.

---

## Sprint 4 - Week 4

### Card: Aggregate scored grid to H3 resolution 8

Label: Analysis

Due date: 2026-07-03

Description:

Convert the 500 m grid scores into H3 resolution 8 hexagons for web display. H3 cells provide a compact spatial index and a clean map layer for deck.gl.

Definition of Done:

- Each grid centroid is assigned to an H3 ID.
- H3 scores are aggregated from grid cells.
- H3 polygons are exported as GeoJSON.

Checklist:

- Assign H3 resolution 8 IDs.
- Group grid cells by H3 ID.
- Aggregate mean scores and indicator values.
- Add district and rent-band fields.
- Convert H3 cells to polygon geometry.
- Export full H3 GeoJSON.

---

### Card: Build web app skeleton

Label: App

Due date: 2026-07-03

Description:

Create the first working web application skeleton that loads the H3 GeoJSON and displays a choropleth map.

Definition of Done:

- Static app folder exists.
- Map loads in browser.
- H3 layer is visible and colored by score.
- Layout is responsive enough for desktop and mobile testing.

Checklist:

- Create `app/index.html`.
- Create `app/styles.css`.
- Create `app/app.js`.
- Load MapLibre and deck.gl.
- Load H3 GeoJSON from `app/data`.
- Add initial color scale and legend.

---

### Card: Add data transparency panel

Label: App

Due date: 2026-07-03

Description:

Add a transparency panel to explain source counts, collection status, and method limitations. This is important because POI and catchment-based accessibility have known limitations.

Definition of Done:

- App reads `summary.json`.
- Data source counts are visible.
- Method limitations are visible.

Checklist:

- Export `summary.json`.
- Copy summary to `app/data`.
- Display POI row count.
- Display traffic, green-space, and road counts.
- Display method notes.

---

## Sprint 5 - Week 5

### Card: Add mode and layer toggles

Label: App

Due date: 2026-07-10

Description:

Add user controls for mode and score layer. Users should be able to switch between walk, bike, transit, and car, and between composite, baseline, and Track A scores.

Definition of Done:

- Mode toggle updates the H3 map.
- Layer toggle updates the H3 map.
- Active score label updates correctly.

Checklist:

- Add walk, bike, transit, and car buttons.
- Add composite, baseline, and Track A buttons.
- Connect controls to map styling.
- Check that detail panel updates with active mode.
- Test interaction in browser.

---

### Card: Add H3 click detail panel

Label: App

Due date: 2026-07-10

Description:

Allow users to click any H3 cell and inspect its details, including score components, top amenities, metro distance, road buffer, rent-band proxy, and contributing grid-cell count.

Definition of Done:

- Clicking an H3 cell updates the detail panel.
- Panel shows score bars and key fields.
- Selected H3 cell is visually highlighted.

Checklist:

- Add click handler.
- Display H3 ID and district.
- Display composite, baseline, and Track A scores.
- Display top amenities.
- Display metro distance.
- Display housing/rent proxy.
- Highlight selected cell.

---

### Card: Build Where-to-Live recommender

Label: App

Due date: 2026-07-10

Description:

Create a small recommender that lets users adjust priorities for sport, green space, cycling, healthy food, and transit. The app should highlight the top 10 H3 cells based on the selected priorities.

Definition of Done:

- Priority sliders work.
- Top 10 H3 cells are ranked and displayed.
- Clicking a recommendation zooms to that H3 cell.

Checklist:

- Add sliders for sport, green, cycling, healthy food, and transit.
- Calculate weighted recommendation score.
- Show top 10 list.
- Highlight top 10 cells on map.
- Add reset button.

---

### Card: Optimize web GeoJSON for loading speed

Label: App

Due date: 2026-07-10

Description:

Reduce the web version of the H3 GeoJSON so it contains only fields needed for the app. The full analysis file can remain in `data/output`, but the app should load a smaller file.

Definition of Done:

- Full analysis GeoJSON remains available.
- Lightweight web GeoJSON is written to `app/data`.
- App loads the lightweight file successfully.

Checklist:

- Select required app fields.
- Export lightweight GeoJSON.
- Confirm file size reduction.
- Test data endpoint locally.
- Confirm map still works.

---

### Card: Run final QA and prepare demo

Label: Review

Due date: 2026-07-10

Description:

Review the final notebooks, data outputs, web app, and Trello board. Prepare a short demo narrative explaining the research question, method, findings, and limitations.

Definition of Done:

- Notebooks are named correctly and contain complete workflow documentation.
- H3 GeoJSON and web app data are generated.
- Local web app runs successfully.
- Trello board has labels, due dates, details, and checklist items.

Checklist:

- Check `01_data_collection.ipynb`.
- Check `02_grid_isochrones.ipynb`.
- Check `03_scoring_h3.ipynb`.
- Check `data/output/summary.json`.
- Check app at local server URL.
- Check Trello labels and due dates.
- Write 3-minute demo script.

---

## Done

Move cards here after completion. In each moved card, keep the checklist visible and add a short completion note such as:

```text
Completion note: Finished and reviewed. Output saved in the project repository.
```

Suggested completed cards for the current project status:

```text
Set up project repository structure
Define baseline and Track A indicators
Inventory downloaded Shanghai datasets
Load and validate POI shapefiles
Validate boundary, built-up area, and district layers
Build 500 m analysis grid
Prepare road-network travel-time fields
Compute four-mode accessibility scores
Calculate baseline and Track A scores
Expand and document notebooks
Aggregate scored grid to H3 resolution 8
Build web app skeleton
Add data transparency panel
Add mode and layer toggles
Add H3 click detail panel
Build Where-to-Live recommender
Optimize web GeoJSON for loading speed
```

---

## Blocked

### Card: Deploy public URL to Vercel

Label: App

Due date: 2026-07-10

Description:

The local web app is complete, but public deployment requires access to a Vercel, Netlify, or GitHub Pages account. This card should stay in Blocked until account login and deployment permission are available.

Definition of Done:

- Deployment account access is available.
- Static `app` folder is deployed.
- Public URL is tested and added to final submission materials.

Checklist:

- Confirm deployment platform.
- Log in to deployment account.
- Upload or connect repository.
- Set `app` as static site root.
- Test map and data loading online.
- Add public URL to README.

Blocker:

```text
Requires user account login or deployment token. Local app is already available at http://127.0.0.1:5173.
```
