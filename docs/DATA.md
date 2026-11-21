# Data model

## Core tables

| Table | Important columns | Notes |
|---|---|---|
| `crops` | `id`, `name_en`, `name_mr`, `name_hi`, `perishability` | Supported crop catalogue. |
| `mandis` | `id`, `name`, `district`, `state`, `lat`, `lng`, `approximate_location` | Mandi coordinates are approximate for demo data. |
| `price_reports` | `crop_id`, `mandi_id`, `reported_on`, `modal_price_inr`, `record_type`, `is_demo` | Modal price is used as published; it is never averaged across mandis. |
| `arrival_reports` | `crop_id`, `mandi_id`, `reported_on`, `quantity_quintal`, `record_type`, `is_demo` | Used by sell-or-wait guidance. |
| `crop_assumptions` | `crop_id`, `yield_p25`, `yield_p75`, `cost_per_acre`, `water_need`, `source` | DEMO assumptions carry a source label. |
| `settings` | `road_factor`, `transport_rate`, `fee_pct`, `shrinkage_pct_by_crop` | Domain defaults are configurable by admins. |
| `users` | `email`, `password_hash`, `role` | Admin authentication only. |
| `query_logs` | `requested_at`, `crop_id`, `radius_km`, `lat_2dp`, `lng_2dp` | No personal data; location is rounded to two decimals. |

`record_type` is either `DEMO` or `AGMARKNET`. Every DEMO record has
`is_demo=true`; the UI must label demo values in the footer and responses.

## Freshness

Freshness is calculated from the latest report date relative to the request:
`FRESH` is one day old or less, `STALE` is two to seven days, `OLD` is over
seven days, and `NO_REPORT` has no report. Missing reports are never treated
as zero. Only FRESH and STALE records are ranked; OLD records are shown below
the ranking.

## Agmarknet notes

The published modal price is the market's reported modal price for a crop,
mandi, and date. FairFarm consumes an exported CSV from data.gov.in or the
portal and does not scrape websites. Imports validate the documented columns
and fail with a clear structure-change error if the portal changes its export.
Real records are retained with `record_type=AGMARKNET`; approximate demo
coordinates and generated records are never mixed into real provenance.

