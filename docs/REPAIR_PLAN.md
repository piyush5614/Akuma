# Repair Baseline

## Environment and branch

- Branch: `repair/redesign`
- Baseline date: 2026-11-21
- Git: 2.56.0
- Python: 3.13.5
- Node: 22.20.0
- Android/JDK: unavailable on `PATH`; baseline Android Gradle build not run
- Android/JDK: JDK 17 and SDK API 35 were found at installed local paths; explicit
  `JAVA_HOME` and `ANDROID_HOME` made the baseline build run successfully
- Docker: 29.3.1 from preflight

## Baseline results

- Backend pytest: 88 passed, 4 JWT key-length warnings
- Backend Ruff: 5 findings (2 unused imports, 2 import-order findings, 1 redundant F401 in `schemas/__init__.py`)
- Web lint: passed
- Web typecheck: passed
- Web tests: 1 file, 2 tests passed
- Web build: passed; 405 KB JavaScript bundle, 28.6 KB CSS
- Android: blocked; `java` is unavailable on `PATH`
- Android re-run: `testDebugUnitTest`, `lintDebug`, and `assembleDebug` passed
  with JDK 17 and Android SDK API 35

## Finding re-verification

| Area | Finding | Status | Evidence |
|---|---|---|---|
| Backend | 3-mandi in-memory store | Confirmed | `backend/app/services/store.py` |
| Backend | Fabricated trend | Confirmed | `backend/app/main.py` trend route |
| Backend | Flat seasonality and backtest zeros | Confirmed | `backend/app/main.py` seasonality/backtest routes |
| Backend | Constant crop-profit assumptions | Confirmed | `backend/app/main.py` `_crop_profit_row` |
| Backend | Sell/wait ignores real signals | Confirmed | recommendation calls `decide(0, 0, 0, ...)` |
| Backend | Regions collapse to one mandi | Confirmed | `backend/app/main.py` regions route |
| Backend | Crop catalog mismatch | Confirmed | 19 in-memory crops vs 8 seed CSV crops |
| Backend | Monolithic route module | Confirmed | `backend/app/main.py` owns all public/admin routes |
| Web | Hardcoded onion/10 quintal | Confirmed | Dashboard, Explorer, Regions and Insights |
| Web | Fake overview/insights | Confirmed | `Dashboard.tsx`, `SimplePages.tsx` |
| Web | Data/Settings/Queries are incomplete | Confirmed | `SimplePages.tsx` |
| Web | Regions mirrors Explorer | Confirmed | `SimplePages.tsx` and `Explorer.tsx` |
| Web | Map lacks ranking/linking/sheets | Confirmed | `components/IndiaMap.tsx` |
| Web | i18n and auth incomplete | Confirmed | sidebar-only i18n, no auth guard |
| Android | Monolithic MainActivity | Confirmed | `MainActivity.kt` |
| Android | Placeholder Insights/Settings | Confirmed | `MainActivity.kt` |
| Android | Raw quantity fallback | Confirmed | `quantity.toDoubleOrNull() ?: 10.0` |
| Android | Letter navigation icons and no voice/map | Confirmed | `MainActivity.kt`, `ChatPanel.kt` |
| Repo | README install mismatch | Confirmed; fixed | README now uses `pip install -e backend` |
| Repo | Junk outside version control | Confirmed | ignored caches/build/database/APK must be cleaned locally |
| Repo | Weak JWT/admin defaults | Confirmed; guarded | production startup now rejects defaults |
| Repo | Broken Part 7 indentation | Confirmed; fixed | `docs/DECISIONS.md` |

## Part 0 cleanup status

- Created `repair/redesign`.
- Saved the repair prompt as `docs/REPAIR_PROMPT.md`.
- Updated ignore rules and removed targeted caches/build/database/APK artifacts where
  the local process allowed.
- No tracked junk was found by `git ls-files -ci --exclude-standard`.
- Production startup now rejects weak `JWT_SECRET` and `ADMIN_PASSWORD` values.

## Web redesign verification

- Replaced the FairFarm shell and login with the reference-derived professional
  blue administration system.
- Rebuilt Overview, Explorer, Regions, Insights, Data, Settings, Query Log,
  and Saathi page surfaces.
- Added an auth guard and logout control around protected dashboard routes.
- Added a linked recommendation/map/detail layout and Saathi voice/feedback
  controls.
- Verified at desktop and 390 px widths in-browser with no horizontal overflow.
- Backend tests: 88 passed.
- Backend Ruff: passed.
- Web lint/typecheck: passed.
- Web Vitest: 2 passed.
- Web production build: passed.
- OpenAPI contract check: 18 operations present.
- Live E2E check: 14 endpoint groups, 5 recommendation samples, 3 languages,
  CORS, ranking, and validation passed.
