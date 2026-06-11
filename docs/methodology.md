# Methodology

## Research Question

Where in Shanghai can residents live an active, healthy life reachable by walking or cycling within 15 minutes?

## Spatial Units

The analysis uses two linked spatial units:

- A 500 m grid for calculation.
- Uber H3 resolution 8 hexagons for aggregation and web display.

Each 500 m cell center is treated as a residential origin. Accessibility is calculated from each origin, then summarized into H3 hexagons.

## Baseline Indicators

The assignment brief requires six universal baseline indicators but does not list them. This project defines the baseline as six everyday urban needs commonly used in 15-minute community life circle studies and walkability research:

| Indicator | What Counts | Default Rule |
| --- | --- | --- |
| Food and daily retail | supermarket, convenience store, fresh market, grocery | at least 1 reachable POI |
| Primary healthcare | clinic, community health center, hospital, pharmacy | at least 1 reachable POI |
| Education and childcare | kindergarten, primary school, middle school, childcare | at least 1 reachable POI |
| Public open space | park, garden, square, playground | at least 1 reachable feature |
| Public transport access | metro station, bus stop, transit stop | at least 1 reachable stop |
| Civic and community services | library, community center, post office, government service, police station | at least 1 reachable POI |

For each grid cell and travel mode, each indicator is coded as `1` if at least one qualifying feature is reachable within 15 minutes and `0` otherwise.

The official baseline score uses walking and cycling only:

```text
baseline_indicator = max(walk_indicator, bike_indicator)
baseline_score = mean(six baseline indicators) * 100
```

Car scores are computed only for comparison.

## Track A Health Indicators

Track A adds a second layer focused on sport, green infrastructure, healthy food, and environmental quality.

| Group | Indicators | Weight |
| --- | --- | --- |
| Sport facilities | gym, sports field/court/track, swimming pool, yoga/martial arts/dance | 35% |
| Green and outdoor activity | sport-capable park/open space, NDVI | 25% |
| Cycling environment | dedicated cycling lane length within isochrone | 15% |
| Healthy food | fresh market or health food access | 10% |
| Environmental quality | AQI or PM2.5, inverted so cleaner air scores higher | 15% |

Continuous values are normalized to 0-100 using percentile clipping:

```text
normalized = clip((value - p5) / (p95 - p5), 0, 1) * 100
```

AQI is inverted:

```text
air_quality_score = 100 - normalized_aqi
```

## Composite Score

The default project score prioritizes universal access while still allowing Track A to tell a health-specific story:

```text
composite_score = 0.60 * baseline_score + 0.40 * health_score
```

The web app can expose this as a recommender with sliders, but the notebook should keep the default score fixed and documented for reproducibility.

## Structural Limits and Scope

This project treats the 15-minute city as a proximity framework for everyday services and healthy-lifestyle amenities, not as a claim that every urban function can be localized. Barthelemy's Paris study argues that employment access can face structural limits because large employers draw workers from broad catchment areas. This means universal 15-minute commuting may be impossible without major economic restructuring, even if transport and land-use planning improve.

For that reason, employment is not part of the Track A health score. The Shanghai app should communicate this limitation clearly: a high-scoring hexagon means strong local access to daily and health amenities, not complete self-sufficiency and not necessarily a short commute to work.

Recommended sensitivity checks:

- compare walk-only, bike-only, and walk-or-bike scores
- compare 10-, 15-, and 20-minute thresholds if time allows
- report sport deserts rather than only top-scoring neighborhoods
- compare inner-city and suburban score distributions

## Isochrone Strategy

Preferred method:

1. Use real routing APIs such as Gaode for walking, cycling, transit, and car travel times.
2. Cache all route/isochrone responses locally.
3. Never publish API keys.

MVP fallback:

1. Use OSM street network and mode-specific speeds.
2. Compute network service areas or network travel-time accessibility.
3. Use straight-line buffers only as a clearly labelled backup, not as the final method.

Suggested speeds for fallback:

| Mode | Speed | 15-minute distance |
| --- | ---: | ---: |
| Walk | 4.8 km/h | 1.2 km |
| Bike | 14 km/h | 3.5 km |
| Transit | route/API preferred | route/API preferred |
| Car | route/API preferred | route/API preferred |

## H3 Aggregation

Each 500 m grid center is assigned to one H3 resolution 8 cell. H3-level values are calculated as:

- mean score
- count of contributing grid cells
- mean indicator values
- top amenities by count or nearest distance

The final file for the web application should be:

```text
data/output/shanghai_health_h3_r8.geojson
```
