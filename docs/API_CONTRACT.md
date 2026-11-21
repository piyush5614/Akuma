# API contract v1

Base path: `/api/v1`. JSON responses use this envelope:

```json
{"data": {}, "data_as_of": "2026-11-21T00:00:00Z", "is_demo": true}
```

Errors always use `{"code":"VALIDATION_ERROR","message":"...","details":{}}`.
Supported languages are `en`, `mr`, and `hi`; prices are INR per quintal.

## Public endpoints

| Method and path | Request/query | Response `data` example |
|---|---|---|
| `GET /health` | none | `{"status":"ok"}` |
| `GET /meta` | none | `{"api_version":"1.0.0","min_app_version":"1.0.0","is_demo":true}` |
| `GET /crops` | none | `[{"id":"onion","name":{"en":"Onion","mr":"कांदा","hi":"प्याज"},"unit":"quintal","perishability":"high"}]` |
| `GET /mandis` | `crop_id`, `lat`, `lng`, `radius_km` (5–300) | `[{"id":"pune","name":"Pune","district":"Pune","state":"Maharashtra","location":{"lat":18.52,"lng":73.86},"freshness":"FRESH","latest_report_date":"2026-11-21","modal_price_inr":"2400"}]` |
| `POST /recommend` | `{"crop_id":"onion","quantity_quintal":10,"farmer_location":{"lat":18.52,"lng":73.86},"radius_km":50}` | `{"crop_id":"onion","quantity_quintal":"10","recommendations":[{"mandi":{},"distance_km":"12.4","costs":{"road_km":"16.1","transport_inr":"96.60","fee_inr":"24.00","shrinkage_inr":"48.00","net_per_quintal_inr":"2231.40","total_net_inr":"22314.00"},"rank":1}],"old_mandis":[],"sell_or_wait":{"decision":"UNSURE","reason_codes":["INSUFFICIENT_SIGNAL"],"reason":{"en":"Check again tomorrow.","mr":"उद्या पुन्हा तपासा.","hi":"कल फिर जाँचें."},"disclaimer":"Guidance, not a guarantee"}}` |
| `GET /mandis/{id}/trend` | `crop_id`, optional `days` | `{"mandi_id":"pune","crop_id":"onion","points":[{"reported_on":"2026-11-21","modal_price_inr":"2400","arrivals_quintal":"120"}]}` |
| `GET /insights/seasonality` | `crop_id` | `{"crop_id":"onion","months":[{"month":1,"price_index":"1.08","median_modal_price_inr":"2500"}],"best_months":[1,2],"worst_months":[7,8]}` |
| `GET /insights/crop-profit` | `water_availability=low|medium|high` | `[{"crop_id":"onion","price_range_inr_per_quintal":["1800","3200"],"yield_range_quintal_per_acre":["50","80"],"cost_inr_per_acre":"70000","risk_adjusted_midpoint_inr_per_acre":"115000","water_fit":"medium","herd_warning":false,"source":"DEMO"}]` |
| `GET /insights/backtest` | `crop_id` | `{"crop_id":"onion","window_days":365,"rule_hit_rate":"0.62","baseline_hit_rate":"0.54","sample_count":120,"measured_only":true}` |
| `GET /regions/prices` | `crop_id`, optional `date` | `[{"region_id":"pune","name":"Pune","location":{"lat":18.52,"lng":73.86},"average_modal_price_inr":"2400","mandi_count":3,"freshness":"FRESH"}]` |
| `POST /chat` | `{"message":"Which mandi pays more?","input_mode":"text","ui_language":"auto","context":{"lat":18.52,"lng":73.86,"crop_id":"onion"},"client":{"platform":"android","app_version":"1.0.0"}}` | `{"session_id":"...","reply":{"text":"Pune gives the best net return.","speak_text":"Pune gives the best net return.","language":"en","script":"latin"},"cards":[],"chips":["Show today's price"],"meta":{"intent":"best_mandi","tools_used":["find_best_mandis"],"data_as_of":"2026-11-21T00:00:00Z","is_demo":true,"confidence":0.95,"grounded":true,"fallback_used":false,"request_id":"..."}}` |
| `GET /chat/starters?lang=` | `lang=en|mr|hi` | Localized starter question list. |
| `POST /chat/feedback` | `{"request_id":"...","rating":"up","reason_code":"clear"}` | `{"accepted":true}` |
| `POST /auth/login` | `{"email":"admin@example.com","password":"..."}` | `{"access_token":"...","token_type":"bearer","expires_in_seconds":3600}` |

## Admin endpoints

All admin endpoints require `Authorization: Bearer <JWT>`.

| Method and path | Request | Response `data` example |
|---|---|---|
| `GET /admin/summary` | none | `{"mandi_count":25,"crop_count":8,"report_count":1000,"fresh_report_pct":"0.82","query_count":12}` |
| `GET /admin/settings` | none | `{"road_factor":"1.3","transport_rate_per_quintal_km":"0.60","fee_pct":"0.01","shrinkage_pct_by_crop":{"onion":"0.02"}}` |
| `PUT /admin/settings` | Same settings object | Updated settings object. |
| `POST /admin/data/import` | Multipart CSV file | `{"imported_records":100,"skipped_records":2,"errors":[]}` |
| `GET /admin/queries` | `limit`, `offset` | `{"items":[{"requested_at":"2026-11-21T10:00:00Z","crop_id":"onion","radius_km":"50","location_rounded":["18.52","73.86"]}],"total":1}` |

## Validation and domain rules

`quantity_quintal` is 0.1–10000; latitude and longitude are range checked;
`radius_km` is 5–300. Net return is calculated only by the backend:
`road_km = haversine_km * road_factor`, then transport, fee, shrinkage, and
total net are deducted. Ranking is total net descending, then distance.

### Saathi chat contract

`POST /chat` accepts a 1–500 character message. `ui_language=auto` detects
English, Marathi, or Hindi; Marathi and Hindi replies use Devanagari script.
`context` is optional and is merged with server-owned location/context before
tools run. Chat cards are typed as `mandi_ranking`, `trend`, `seasonality`,
`crop_suggestions`, or `term`. Every factual card must carry freshness/demo
metadata in its typed data. Errors use the common error envelope.

