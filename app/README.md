# 15-Minute Shanghai Web App

Static web application for the Track A Healthy Lifestyle & Sport deliverable.

## Run locally

From the project root:

```powershell
python -m http.server 5173 -d app
```

Open `http://localhost:5173`.

## Data

The app reads:

```text
app/data/shanghai_health_h3_r8.geojson
app/data/summary.json
```

The full analysis GeoJSON remains in:

```text
data/output/shanghai_health_h3_r8.geojson
```

## Implemented features

- H3 resolution 8 choropleth using deck.gl `H3HexagonLayer` with GeoJSON fallback.
- Mode toggle for walk, bike, transit, and car.
- Composite, baseline, and Track A layer toggle.
- H3 detail panel with top amenities, metro distance, road buffer, housing proxy, and rent band.
- Priority-slider recommender with top 10 highlighted hexes.
- Data transparency panel with source counts and method limitations.

## Deployment

The `app` folder can be deployed as a static site on Vercel, Netlify, or GitHub Pages. No build step is required.
