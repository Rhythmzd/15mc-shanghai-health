const DATA_URL = "./data/shanghai_health_h3_r8.geojson";
const SUMMARY_URL = "./data/summary.json";

const modeLabels = {
  walk: "Walk",
  bike: "Bike",
  transit: "Transit",
  car: "Car",
};

const metricLabels = {
  composite: "Composite",
  baseline: "Baseline",
  health: "Track A",
};

const sliderConfig = [
  { key: "sport", label: "Sport", field: "sport_walk_score", value: 35 },
  { key: "green", label: "Green", field: "green_outdoor_walk_score", value: 25 },
  { key: "cycling", label: "Cycling", field: "cycling_env_walk_score", value: 15 },
  { key: "food", label: "Healthy food", field: "healthy_food_walk_score", value: 10 },
  { key: "transit", label: "Transit", field: "transit_access_walk_score", value: 15 },
];

const state = {
  geojson: null,
  features: [],
  summary: null,
  map: null,
  overlay: null,
  metric: "composite",
  mode: "walk",
  selectedId: null,
  topIds: new Set(),
  topVersion: 0,
  weights: Object.fromEntries(sliderConfig.map((item) => [item.key, item.value])),
};

const numberFmt = new Intl.NumberFormat("en-US");
const scoreFmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 });

function $(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getMetricField() {
  if (state.metric === "baseline") return `baseline_${state.mode}`;
  if (state.metric === "health") return `health_${state.mode}`;
  return `composite_${state.mode}`;
}

function getScore(feature, field = getMetricField()) {
  return Number(feature?.properties?.[field] ?? feature?.properties?.composite_score ?? 0);
}

function colorFor(score) {
  if (score >= 85) return [33, 116, 90, 218];
  if (score >= 75) return [101, 169, 81, 214];
  if (score >= 65) return [214, 198, 75, 210];
  if (score >= 50) return [217, 144, 40, 210];
  return [200, 91, 74, 210];
}

function meters(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "No data";
  if (n >= 1000) return `${scoreFmt.format(n / 1000)} km`;
  return `${numberFmt.format(Math.round(n))} m`;
}

function scoreBar(label, value) {
  const score = Math.max(0, Math.min(100, Number(value) || 0));
  return `
    <div class="score-row">
      <span>${escapeHtml(label)}</span>
      <div class="bar"><span style="width:${score}%"></span></div>
      <strong>${scoreFmt.format(score)}</strong>
    </div>
  `;
}

function featureCenter(feature) {
  const ring = feature.geometry?.coordinates?.[0] || [];
  if (!ring.length) return [121.47, 31.23];
  const total = ring.reduce(
    (acc, coord) => {
      acc[0] += coord[0];
      acc[1] += coord[1];
      return acc;
    },
    [0, 0],
  );
  return [total[0] / ring.length, total[1] / ring.length];
}

function initMap() {
  state.map = new maplibregl.Map({
    container: "map",
    center: [121.47, 31.23],
    zoom: 9.15,
    minZoom: 8,
    maxZoom: 15,
    style: {
      version: 8,
      sources: {
        osm: {
          type: "raster",
          tiles: [
            "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
          ],
          tileSize: 256,
          attribution: "OpenStreetMap contributors",
        },
      },
      layers: [{ id: "osm", type: "raster", source: "osm" }],
    },
  });

  state.map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
  state.overlay = new deck.MapboxOverlay({ interleaved: false, layers: [] });
  state.map.addControl(state.overlay);
}

function makeLayer() {
  const field = getMetricField();
  const common = {
    id: "h3-health-layer",
    pickable: true,
    autoHighlight: true,
    opacity: 0.88,
    getFillColor: (feature) => colorFor(getScore(feature, field)),
    getLineColor: (feature) => {
      const id = feature.properties.h3_id;
      if (id === state.selectedId) return [23, 33, 43, 255];
      if (state.topIds.has(id)) return [255, 255, 255, 240];
      return [255, 255, 255, 70];
    },
    getLineWidth: (feature) => {
      const id = feature.properties.h3_id;
      if (id === state.selectedId) return 95;
      if (state.topIds.has(id)) return 65;
      return 14;
    },
    lineWidthUnits: "meters",
    lineWidthMinPixels: 0.35,
    lineWidthMaxPixels: 4,
    onClick: ({ object }) => {
      if (object) selectFeature(object, true);
    },
    updateTriggers: {
      getFillColor: [field],
      getLineColor: [state.selectedId, state.topVersion],
      getLineWidth: [state.selectedId, state.topVersion],
    },
  };

  if (deck.H3HexagonLayer) {
    return new deck.H3HexagonLayer({
      ...common,
      data: state.features,
      getHexagon: (feature) => feature.properties.h3_id,
      extruded: false,
      stroked: true,
      filled: true,
    });
  }

  return new deck.GeoJsonLayer({
    ...common,
    data: state.geojson,
    stroked: true,
    filled: true,
  });
}

function updateLayer() {
  if (!state.overlay) return;
  state.overlay.setProps({
    layers: [makeLayer()],
    getTooltip: ({ object }) => {
      if (!object) return null;
      const p = object.properties;
      const field = getMetricField();
      return {
        text: `${p.district || "Shanghai"}\n${metricLabels[state.metric]} ${modeLabels[state.mode]}: ${scoreFmt.format(p[field] ?? 0)}`,
      };
    },
  });
  $("active-field").textContent = `${metricLabels[state.metric]} ${modeLabels[state.mode]}`;
  const active = selectedFeature();
  if (active) renderDetail(active);
}

function selectedFeature() {
  if (!state.selectedId) return null;
  return state.features.find((feature) => feature.properties.h3_id === state.selectedId) || null;
}

function selectFeature(feature, fly = false) {
  state.selectedId = feature.properties.h3_id;
  renderDetail(feature);
  renderTopList();
  updateLayer();
  if (fly && state.map) {
    state.map.flyTo({ center: featureCenter(feature), zoom: Math.max(state.map.getZoom(), 11.4), speed: 0.9 });
  }
}

function renderDetail(feature) {
  const p = feature.properties;
  const activeValue = getScore(feature);
  $("detail-district").textContent = p.district || "Shanghai";
  $("detail-title").textContent = p.h3_id;
  $("score-stack").innerHTML = [
    scoreBar(`${metricLabels[state.metric]} ${modeLabels[state.mode]}`, activeValue),
    scoreBar("Baseline", p[`baseline_${state.mode}`] ?? p.baseline_score),
    scoreBar("Track A", p[`health_${state.mode}`] ?? p.track_score),
    scoreBar("Sport", p.sport_walk_score),
    scoreBar("Green", p.green_outdoor_walk_score),
  ].join("");

  $("detail-list").innerHTML = `
    <dt>Top amenities</dt><dd>${escapeHtml(p.top_amenities)}</dd>
    <dt>Metro distance</dt><dd>${meters(p.metro_dist_m)}</dd>
    <dt>Road buffer</dt><dd>${meters(p.major_road_dist_m)}</dd>
    <dt>Housing proxy</dt><dd>${p.housing_price_proxy ? numberFmt.format(Math.round(p.housing_price_proxy)) : "No data"}</dd>
    <dt>Rent band</dt><dd>${escapeHtml(p.rent_band)}</dd>
    <dt>Grid cells</dt><dd>${numberFmt.format(Math.round(p.grid_count || 0))}</dd>
  `;
}

function updateStats() {
  const values = state.features.map((feature) => getScore(feature)).filter(Number.isFinite);
  const mean = values.reduce((sum, value) => sum + value, 0) / Math.max(values.length, 1);
  $("mean-score").textContent = scoreFmt.format(mean);
  $("hex-count").textContent = numberFmt.format(state.features.length);
  $("grid-count").textContent = numberFmt.format(state.summary?.grid_cells || 0);
}

function renderDataPanel() {
  const summary = state.summary || {};
  const supporting = summary.supporting_data || {};
  const roads = supporting.roads_summary || {};
  const layers = supporting.supporting_layers || [];
  const layerText = layers.map((layer) => `${layer.layer}: ${numberFmt.format(layer.rows)}`).join(", ");
  const generated = summary.generated_at ? new Date(summary.generated_at).toLocaleString() : "No data";
  $("data-panel").innerHTML = `
    <dt>Generated</dt><dd>${escapeHtml(generated)}</dd>
    <dt>POI rows</dt><dd>${numberFmt.format(summary.poi?.poi_rows_loaded || 0)}</dd>
    <dt>Traffic/green</dt><dd>${escapeHtml(layerText)}</dd>
    <dt>Roads</dt><dd>${numberFmt.format(roads.rows || 0)} edges, ${numberFmt.format(roads.total_km || 0)} km</dd>
    <dt>Limitations</dt><dd>${escapeHtml((summary.method_notes || []).join(" "))}</dd>
  `;
}

function renderControls() {
  $("metric-controls").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-metric]");
    if (!button) return;
    state.metric = button.dataset.metric;
    [...$("metric-controls").querySelectorAll("button")].forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    updateStats();
    updateLayer();
  });

  $("mode-controls").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-mode]");
    if (!button) return;
    state.mode = button.dataset.mode;
    [...$("mode-controls").querySelectorAll("button")].forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    updateStats();
    updateLayer();
  });
}

function renderSliders() {
  $("sliders").innerHTML = sliderConfig
    .map(
      (item) => `
        <label class="slider-row">
          <span>${escapeHtml(item.label)}</span>
          <input type="range" min="0" max="100" step="1" value="${state.weights[item.key]}" data-weight="${item.key}" />
          <strong id="weight-${item.key}">${state.weights[item.key]}</strong>
        </label>
      `,
    )
    .join("");

  $("sliders").addEventListener("input", (event) => {
    const input = event.target.closest("input[data-weight]");
    if (!input) return;
    state.weights[input.dataset.weight] = Number(input.value);
    $(`weight-${input.dataset.weight}`).textContent = input.value;
    updateRecommender();
  });

  $("reset-weights").addEventListener("click", () => {
    sliderConfig.forEach((item) => {
      state.weights[item.key] = item.value;
      const input = document.querySelector(`input[data-weight="${item.key}"]`);
      if (input) input.value = item.value;
      const label = $(`weight-${item.key}`);
      if (label) label.textContent = item.value;
    });
    updateRecommender();
  });
}

function recommendationScore(feature) {
  const total = Object.values(state.weights).reduce((sum, value) => sum + value, 0) || 1;
  return sliderConfig.reduce((sum, item) => {
    const value = Number(feature.properties[item.field] || 0);
    return sum + value * (state.weights[item.key] / total);
  }, 0);
}

function updateRecommender() {
  const top = [...state.features]
    .map((feature) => ({ feature, score: recommendationScore(feature) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 10);
  state.topIds = new Set(top.map((item) => item.feature.properties.h3_id));
  state.topVersion += 1;
  state.topRank = top;
  renderTopList();
  updateLayer();
}

function renderTopList() {
  const top = state.topRank || [];
  $("top-list").innerHTML = top
    .map((item, index) => {
      const p = item.feature.properties;
      const active = p.h3_id === state.selectedId ? "active" : "";
      return `
        <li>
          <button class="${active}" data-h3="${escapeHtml(p.h3_id)}">
            <strong>${index + 1}. ${escapeHtml(p.district || "Shanghai")} · ${scoreFmt.format(item.score)}</strong>
            <span>${escapeHtml(p.top_amenities || "")}</span>
          </button>
        </li>
      `;
    })
    .join("");

  $("top-list").querySelectorAll("button[data-h3]").forEach((button) => {
    button.addEventListener("click", () => {
      const feature = state.features.find((item) => item.properties.h3_id === button.dataset.h3);
      if (feature) selectFeature(feature, true);
    });
  });
}

async function loadData() {
  const [geojsonResponse, summaryResponse] = await Promise.all([fetch(DATA_URL), fetch(SUMMARY_URL)]);
  if (!geojsonResponse.ok) throw new Error(`GeoJSON request failed: ${geojsonResponse.status}`);
  state.geojson = await geojsonResponse.json();
  state.summary = summaryResponse.ok ? await summaryResponse.json() : null;
  state.features = state.geojson.features || [];
}

async function init() {
  try {
    if (!window.maplibregl || !window.deck) {
      throw new Error("Map libraries did not load");
    }
    initMap();
    renderControls();
    renderSliders();
    await loadData();
    renderDataPanel();
    updateStats();
    updateRecommender();
    const first = [...state.features].sort((a, b) => getScore(b) - getScore(a))[0];
    if (first) selectFeature(first, false);
    $("loading").classList.add("hidden");
  } catch (error) {
    $("loading").textContent = error.message;
    console.error(error);
  }
}

document.addEventListener("DOMContentLoaded", init);
