# Data Sources

This file is the data provenance log. Update it whenever data is collected, transformed, replaced, or excluded.

## Core Sources

| Source | Use | Status | Notes |
| --- | --- | --- | --- |
| Local Shanghai POI Shp folder | Gaode-style POIs by industry category | available | 17 WGS84 shapefiles, about 1.49 million POIs; use UTF-8 encoding |
| Downloaded 2025 data-analysis-project package | admin, traffic, AOI, built area, landuse, AI-interpreted layers | available | extracted to `data/raw`; see `docs/downloaded_dataset_inventory.md` |
| `shanghai-roads-simplified.parquet` | simplified OSM-style Shanghai road network | available | copied to `data/raw/roads`; contains road class, walking, cycling, car, speed, and geometry fields |
| OpenStreetMap / Geofabrik | streets, POIs, parks, cycleways, transit stops | planned | recommended open baseline source |
| Shanghai Open Data | administrative boundaries, public facilities, parks, land use | planned | verify dataset availability before final analysis |
| Gaode Maps API | real routing and POI search | optional | requires API key; follow terms of service |
| Google Earth Engine Sentinel-2 | NDVI greenery index | optional | requires GEE access |
| AQICN or CNEMC | AQI or PM2.5 by station/district | optional | document collection date and spatial interpolation |

## Local Shanghai POI Shapefiles

The local folder supplied for this project contains 17 WGS84 shapefiles with consistent fields:

```text
OBJECTID, id, name, type, typecode, address, 经度, 纬度, tel, pcode, pname,
citycode, cityname, adcode, adname, gridcode, distance, business_a,
timestamp, biz_ext, 行业大, 行业中, 行业小, typecode_X, typecode_Y
```

The `.cpg` files declare `UTF-8`, so the notebook should call:

```python
gpd.read_file(shp_file, encoding="utf-8")
```

Current inventory:

| Shapefile Category | Records |
| --- | ---: |
| 交通设施服务 | 86,065 |
| 住宿服务 | 29,444 |
| 体育休闲服务 | 30,458 |
| 公共设施 | 18,005 |
| 公司企业 | 142,224 |
| 医疗保健服务 | 23,135 |
| 商务住宅 | 41,628 |
| 地名地址信息 | 490,460 |
| 政府机构及社会团体 | 52,224 |
| 汽车相关 | 29,606 |
| 生活服务 | 147,345 |
| 科教文化服务 | 39,876 |
| 购物服务 | 198,286 |
| 道路附属设施 | 341 |
| 金融保险服务 | 13,032 |
| 风景名胜 | 6,703 |
| 餐饮服务 | 142,087 |
| Total | 1,490,919 |

## Baseline POI Mapping

| Baseline Indicator | OSM Tags / Candidate Categories |
| --- | --- |
| Food and daily retail | `shop=supermarket`, `shop=convenience`, `shop=grocery`, `amenity=marketplace` |
| Primary healthcare | `amenity=clinic`, `amenity=hospital`, `amenity=doctors`, `amenity=pharmacy` |
| Education and childcare | `amenity=kindergarten`, `amenity=school`, `amenity=college`, `amenity=childcare` |
| Public open space | `leisure=park`, `leisure=garden`, `leisure=playground`, `place=square` |
| Public transport access | `railway=station`, `station=subway`, `public_transport=platform`, `highway=bus_stop` |
| Civic and community services | `amenity=library`, `amenity=community_centre`, `amenity=post_office`, `amenity=police`, `office=government` |

## Track A POI Mapping

| Track A Indicator | OSM Tags / Candidate Categories |
| --- | --- |
| Gym or fitness studio | `leisure=fitness_centre`, `sport=fitness` |
| Sport-capable park/open space | `leisure=park`, `leisure=pitch`, `leisure=sports_centre`, `leisure=track` |
| Sports field/court/track | `leisure=pitch`, `leisure=track`, `sport=basketball`, `sport=running`, `sport=soccer`, `sport=tennis` |
| Swimming pool | `leisure=swimming_pool`, `sport=swimming` |
| Yoga/martial arts/dance | `sport=yoga`, `sport=martial_arts`, `sport=dance`, keyword fallback in names |
| Cycle lane length | `highway=cycleway`, `cycleway=*`, `bicycle=designated` |
| Fresh market/healthy food | `amenity=marketplace`, `shop=greengrocer`, `shop=health_food`, `shop=organic` |
| NDVI | Sentinel-2 imagery |
| AQI/PM2.5 | station or district environmental data |

## Citation Seeds

- Moreno, C., Allam, Z., Chabaud, D., Gall, C., and Pratlong, F. (2021). Introducing the "15-Minute City": Sustainability, Resilience and Place Identity in Future Post-Pandemic Cities. Smart Cities, 4(1), 93-111. https://doi.org/10.3390/smartcities4010006
- Yang, Y., Qian, Y., Zeng, J., Wei, X., and Yang, M. (2023). Walkability Measurement of 15-Minute Community Life Circle in Shanghai. Land, 12(1), 153. https://doi.org/10.3390/land12010153
- Wu, H., Wang, L., Zhang, Z., and Gao, J. (2021). Analysis and optimization of 15-minute community life circle based on supply and demand matching: A case study of Shanghai. PLOS ONE, 16(8), e0256904. https://doi.org/10.1371/journal.pone.0256904
- Casarin, G., MacLeavy, J., and Manley, D. (2023). Rethinking urban utopianism: The fallacy of social mix in the 15-minute city. Urban Studies, 60(16). https://doi.org/10.1177/00420980231169174
- Barthelemy, M. (2026). Why urban heterogeneity limits the 15-minute city. arXiv:2603.12122v2. https://doi.org/10.48550/arXiv.2603.12122
