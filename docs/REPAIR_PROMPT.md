# FairFarm Repair and Redesign Prompt (for the coding agent)
**For me (the human):** Open your FairFarm repo in VS Code and paste everything below `PROMPT START` into your coding agent (Claude Code or Antigravity). Save this file as `docs/REPAIR_PROMPT.md`. Reply `CONTINUE` after each completion report.

**What I checked:** I unzipped your source (leaving out node_modules, the database, the APK and caches) and read the backend, web and Android code, the docs and the demo data. I did **not** run the app or the builds, so the findings below come from reading code. If something looks wrong on screen that is not listed, send screenshots and I will add it. Your zip is 339 MB mostly because of the 44 MB database, the APK and dependencies; Part 0 cleans that up.

---

## PROMPT START

### 0. Mission
You are a senior team in one: product designer, full-stack engineer, Android engineer and QA lead. Repair and redesign the existing **FairFarm** repo (FastAPI backend, React + Vite web dashboard, Kotlin + Jetpack Compose Android app, Saathi chatbot). The owner finds the UI unprofessional, the map poor, the quantity and weight input confusing, and the features incomplete. Goal: a polished, interactive, trustworthy product where **every number on screen comes from real backend data** (demo data clearly labelled DEMO) and **every button works**.

### 1. Working protocol

1. Do ONE part at a time, in order. Before each part re-read this prompt, `docs/PROGRESS.md` and `docs/DECISIONS.md`.
2. After each part post the report below, update `docs/PROGRESS.md` and `docs/DECISIONS.md`, commit, then STOP until I say CONTINUE.
3. Never claim something works unless you ran it. Report real commands and real results. If you cannot run something (emulator, Docker), say so and list what I must do.
4. If blocked, post a `⛔ PART N BLOCKED` report with cause, attempts and options. Never fake output, stub silently or weaken tests.
5. Keep the backend as the single source of truth for pricing, ranking and rules. Clients never recompute them.
6. Do not break the API silently: if a contract changes, update `docs/API_CONTRACT.md`, the web client, the Android client, `scripts/contract_check.py` and the tests together.
7. Use conventional commits. Latest stable dependency versions, pinned.

```
✅ PART N COMPLETE: <name>
Done: <3-6 bullets>
Files: <created/changed, grouped by folder>
Ran: <commands + result>
Checks: <tests/lint/build with counts>
Assumptions / known issues: <list or none>
Next: PART N+1 <name>. Reply CONTINUE.
```

### 2. Audit findings (verified by reading the code; re-verify in Part 0 and fix every item)
**A. Backend and data**

1. `backend/app/services/store.py` serves the whole API from an in-memory list of only **3 mandis** (Pune, Nashik, Satara) with flat hardcoded prices. The seeded SQLite database (25 mandis, 8 crops, 2 years of history from `backend/scripts/seed_demo.py`) is **never read by the API**.
2. `GET /mandis/{id}/trend` fabricates points (price plus offset x 5, arrivals always 100).
3. `GET /insights/seasonality` returns index 1.00 for every month with hardcoded best months [1, 2] and worst [7, 8].
4. `GET /insights/backtest` returns zeros. `GET /insights/crop-profit` and `POST /insights/next-crops` use the same constants for every crop (price range 1800 to 3200, cost 70000, three fixed midpoints).
5. `POST /recommend` calls `decide(0, 0, 0, perishable)`, so sell-or-wait only reflects perishability and ignores price trend, arrivals and season.
6. `GET /regions/prices` returns one mandi per region.
7. Crop catalog mismatch: 19 crops in `store.py`, 8 in the seed and in `data/demo/crops.csv`.
8. `backend/app/main.py` (about 18 KB) holds every route, while `api/v1`, `models`, `db` and `core` are empty `.gitkeep` folders.
**B. Web dashboard**

1. Crop is hardcoded to onion and quantity to 10 quintal on Overview, Explorer, Regions and Insights. There is no crop or quantity control anywhere.
2. Overview shows a hardcoded '2 / 3' fresh reports and a fixed 'Maharashtra' header.
3. The Insights seasonality chart is fake (bar heights computed from the index), and crop profit is a placeholder card.
4. Data page: the file input and button do nothing. Query log: always empty. Settings: hardcoded starting values, never loads the saved settings, only 3 fields, no validation.
5. Regions is a copy of Explorer (same query, same map).
6. `IndiaMap.tsx`: India-wide zoom 5, plain circles coloured only by freshness, popup shows only the modal price (not net return), no 'you are here' marker, no ranking, no route, no fit-to-bounds, no list sync.
7. i18n covers only sidebar labels; all page copy is hardcoded English; no auth guard on routes; components are dense one-liners and `app.css` is 43 very long lines.
**C. Android app**

1. `MainActivity.kt` holds the whole UI in one composable: no navigation graph, **no map** (osmdroid is a dependency but unused), no Room cache (dependency unused), no voice.
2. Insights and Settings are one line of placeholder text. The 'Open directions' button on mandi cards does nothing.
3. **Quantity is a raw text field** ('Quantity (quintal)') that silently falls back to 10 on bad input: no unit choice (kg, quintal, tonne), no validation message, no quick amounts, no explanation of what a quintal is.
4. Bottom-nav icons are the first letter of each label, a floating button overlays content, and result cards show only total net and freshness (no distance, per-quintal price, cost breakdown or styled sell/wait chip).
5. `strings.xml` holds only the app name; all text is hardcoded English; no `values-mr` or `values-hi`; no language switch; fonts not bundled.
6. Saathi shows plain text bubbles; the backend's cards, chips, feedback and `speak_text` are unused; no mic, no speaker.
**D. Repo and docs**

1. README says `pip install -r backend/requirements.txt` but that file does not exist (only `pyproject.toml`).
2. The zip contains junk: `.github/modernize/`, `.ruff_cache`, `.pytest_cache`, `apps/web/dist`, a 44 MB `fairfarm.db` and an APK. Make sure they are git-ignored and removed from history if committed.
3. JWT secret and admin password fall back to dev values; production must refuse to start with defaults.
4. `docs/DECISIONS.md` has broken indentation in the Part 7 section, and docs describe features that are stubs (seasonality, backtest, crop profit).

### 3. Definition of done
**3.1 Quantity and weight (shared component, web and Android)**

- **QuantityPicker** with a unit toggle **kg | quintal | tonne** (default quintal), a stepper (minus and plus; steps: quintal 1, kg 50, tonne 0.5), a typed input, and quick chips (5, 10, 20, 50 quintal).
- Always show the converted value under the field, for example '10 quintal = 1,000 kg = 1 tonne', and a one-line help text: '1 quintal = 100 kg'.
- Inline validation (0.1 to 10,000 quintal equivalent), Indian number formatting, remember the last value, never silently replace a bad value.
- API: accept `quantity` and `unit` (`kg|quintal|tonne`) and keep `quantity_quintal` working. The backend converts and echoes `quantity_input`, `quantity_quintal` and `quantity_kg`.
- Result screens show BOTH 'per quintal' and 'total for your quantity'.
**3.2 Map (web and Android)**

- Basemap OpenStreetMap (keep attribution), but a custom look: markers are **price pills** (for example '₹2,310/q net'), coloured by rank tier with the best mandi highlighted (lime ring), plus numbered rank badges.
- A 'You' marker with an accuracy circle; fit the view to the farmer plus the top 5 mandis (never the whole of India unless there is no data); dashed line from the farmer to the selected mandi; Navigate button (geo intent on Android, Google Maps link on web).
- Map and list are linked: tapping a pin highlights the list card and the reverse. A selected mandi opens a card or bottom sheet with the cost breakdown (price, transport, fee, shrinkage, net).
- Layer toggle: **Net return | Modal price | Freshness**. Legend, recenter button, loading and empty states, marker clustering if there are more than 40 markers.
- Regions page: district bubbles sized by arrivals and coloured by price vs the state median for the chosen crop, with a side panel (sparkline, top crops). No GeoJSON is required; do not add one without checking its licence.
**3.3 Features that must be real**

1. **Best mandi:** ranked list with cost breakdown, distance, report date, freshness badge and **'You gain ₹X vs the nearest mandi'** (computed in the backend as `gain_vs_nearest_inr`).
2. **Sell or wait:** computed from real price slope, arrivals change and seasonality in the database; show reason codes in plain language, a mini chart and an uncertainty label.
3. **Trend:** real series from the database with 7/30/90 day toggle and arrivals bars.
4. **Seasonality:** real monthly index, best and worst months highlighted, month labels.
5. **Crop planner:** a short wizard (what did you grow, water availability, land size) giving ranked crops with profit range, risk, water fit and a plain explanation. Replace the hardcoded constants with the assumptions table plus database prices; keep `is_demo` and `source` visible.
6. **Regions** (see 3.2), **Data** (working CSV import with validation preview and a freshness table), **Settings** (load, edit, validate and save every parameter, reset to defaults, show the effect on an example), **Query log** (real data from `/admin/queries`), **Overview** (real KPIs from `/admin/summary`).
7. **Saathi:** render the backend's cards and chips, add the mic and speaker buttons, thumbs feedback, and keep chat history offline.
8. **Language:** English, Marathi and Hindi across the whole UI with a visible switcher; bundled Inter and Noto Sans Devanagari fonts.
9. Web auth guard with logout; Android offline cache with a 'last updated' banner.

### 4. Design direction
Premium, minimal, calm and confident, for farmers first. Keep the identity (ink green, ivory canvas, one lime accent) but raise the craft:

- 8-point spacing grid, a clear type scale (display, title, body, caption), tabular numbers for prices, and a strong visual hierarchy: **one primary answer per screen** (the best mandi and the gain).
- Lime is a fill colour with ink text only (check contrast, AA). Red/amber/green status always carries an icon or text.
- Real iconography: Lucide on web; Material icons (extended) on Android. A crop emoji or icon per crop in pickers. No letters as icons.
- Motion 150 to 250 ms, ease-out, skeleton loaders instead of spinners, respect reduced motion. Friendly empty and error states with a clear next action.
- Web: collapsible sidebar, a persistent **context bar** (crop, quantity, location) shared by all pages, responsive down to tablet. Android: top app bar, bottom navigation with icons, cards, bottom sheets, 48dp targets, font scaling, TalkBack labels, adaptive launcher icon and splash screen.
- Do not use stock photos or copy any reference design.

---

## PART 0: Baseline, hygiene and plan
**Tasks:** run the existing backend tests, web lint, typecheck, tests and build, and Android unit tests (if the SDK exists); record real results in `docs/REPAIR_PLAN.md` together with a re-verification of every finding in section 2 (confirm or correct each, with file and line). Clean the repo: update `.gitignore`, remove `.github/modernize/`, caches, `dist`, the database and APK from version control (keep `artifacts/.gitkeep`), add a `requirements.txt` generated from `pyproject.toml` or fix the README to match, make production refuse default JWT and admin secrets, and fix `docs/DECISIONS.md` formatting. Create a git branch `repair/redesign`.

**Done when:** baseline results are recorded, the repo is clean and the README quick start works from a fresh clone (test it).

## PART 1: Real data layer
**Tasks:** build proper `db/`, `models/` and repositories over the seeded SQLite database (keep PostgreSQL-ready SQLAlchemy). Make the API read from it and delete the in-memory `store.py`. Unify the crop catalog: one source (database table plus CSV seed) with all crops the product supports, in en/mr/hi, and update `seed_demo.py` so every crop has realistic DEMO history with seasonality, gaps and arrivals. Extend the demo mandi set so a farmer anywhere in Maharashtra has at least 5 mandis within 150 km (coordinates marked approximate). Implement real services: `trend`, `seasonality` (monthly median / yearly median), `sell_or_wait` (7-day slope, arrivals change, seasonal expectation, thresholds in config), `backtest` (rule vs 'same as last week', measured hit rate only), `regions` (district averages with mandi count and arrivals) and `crop_profit` (assumptions table plus database prices, p25 to p75 ranges, water and volatility risk, herd warning).

**Tests:** hand-computed cases for each service using small synthetic series; seed idempotency; every endpoint returns database-driven values (assert they differ between crops and mandis).

**Done when:** no endpoint returns a hardcoded business value, and `pytest` and `ruff` pass.

## PART 2: API and backend structure
**Tasks:** split `main.py` into `api/v1/` routers (catalog, recommend, insights, regions, chat, auth, admin), `core/` (config, security, errors) and `services/`. Add the quantity and unit support from 3.1. Extend `POST /recommend` to return, per mandi: modal price per quintal, `net_per_quintal_inr`, the cost breakdown, distance, report date, freshness, `is_nearest`, `gain_vs_nearest_inr`; and at the top level: `best`, `nearest`, the assumptions used (rates) and a short explanation. Keep Decimal money, half-up rounding to whole rupees for display. Add pagination or limits where needed, consistent errors, request ids. Update the OpenAPI contract, `docs/API_CONTRACT.md` and `scripts/contract_check.py`.

**Done when:** API tests cover every route (including unit conversion and validation errors), the contract check passes and `/openapi.json` matches the docs.

## PART 3: Design system v2 (I review this part)
**Tasks:** rewrite `docs/DESIGN_SYSTEM.md` and `docs/design/tokens.json` to section 4 (type scale, spacing, radius, elevation, motion, colours with contrast ratios). Generate the web CSS variables and Android theme and typography from the tokens. Bundle fonts. Build `docs/design/preview/index.html`: static, polished mock screens at desktop and phone widths for Overview, Explorer with the new map, QuantityPicker states, Result with cost breakdown, Planner wizard, Seasonality, Settings, Saathi chat. Use realistic DEMO numbers.

**Done when:** the preview opens in a browser and covers every screen in sections 3.1 to 3.3. Then STOP for my review.

## PART 4: Web dashboard rebuild
**Tasks:** restructure `apps/web/src` into `app/` (router, providers, auth guard), `pages/`, `features/` (explorer, planner, insights, regions, data, settings, saathi), `components/ui` and `components/map` and `components/charts`, `api/`, `i18n/` (en, mr, hi JSON, complete) and `lib/` (format, units). Format with Prettier, one component per file, split `app.css` into tokens plus per-component styles. Build the shell with the context bar, QuantityPicker, CropPicker, the map from 3.2 (react-leaflet with custom price-pill markers), Recharts charts, working Data, Settings and Query log pages, real Overview KPIs, Saathi page with cards, loading, empty and error states, and keyboard and screen reader support.

**Tests:** Vitest for unit conversion, formatting, QuantityPicker validation and key pages with mocked API; if possible, a Playwright smoke test that clicks every button and saves screenshots at 1440 and 390 px widths into `docs/screenshots/`.

**Done when:** `npm run lint`, `typecheck`, `test` and `build` pass, and a dead-button audit (a list of every interactive element with its handler or route) shows none without an action.

## PART 5: Android app rebuild
**Tasks:** restructure into `ui/{home,result,mandi,insights,planner,ask,settings,components,theme}`, `data`, `domain`, `di` (Hilt with KSP if it builds cleanly, otherwise a simple manual container; record the choice). Use Navigation Compose with a bottom bar with real icons (Home, Insights, Ask, Settings) and routes for Result, Mandi detail and the Planner wizard. Build: Home with the QuantityPicker (3.1), a crop grid with icons, location chip (GPS with permission rationale and a manual fallback), and one clear 'Find best market' button; Result with a hero card (best mandi, gain vs nearest), ranked cards (price pill, net per quintal, total, distance, freshness, sell/wait chip), a Map toggle using osmdroid with the 3.2 behaviour, and a Navigate button that opens a geo intent; Mandi detail with the trend chart range toggle and cost breakdown; Insights with real seasonality bars; the Planner wizard; Settings (language switcher en/mr/hi using per-app locales, vehicle rate, water availability, about and data freshness, DEMO label); Saathi with cards, chips, mic (SpeechRecognizer mr-IN, hi-IN, en-IN), speaker (TextToSpeech with voice availability check), thumbs feedback and Room-stored history. Add Room caching of the crop list and last result with an offline banner. Provide `values/`, `values-mr/` and `values-hi/` strings for all text (no hardcoded UI text), the bundled fonts, an adaptive icon and a splash screen.

**Tests:** unit tests for unit conversion, mappers, repositories (fake API) and ViewModels; `./gradlew testDebugUnitTest lintDebug assembleDebug`.

**Done when:** the build and tests pass (or you state exactly what could not run) and every button on every screen performs an action.

## PART 6: Integration and end-to-end checks
**Tasks:** update `scripts/contract_check.py` and `scripts/e2e_check.py` for the new API (units, `gain_vs_nearest_inr`, real insights, admin settings round trip, CSV import, chat cards). Verify that the web client, the Android client and the backend agree on field names, units and language codes. Run all suites, fix every failure at its root cause, and start the full stack with Docker (or locally if Docker is unavailable) and exercise a farmer journey: pick onion, 20 quintal, see the ranking, open the map, read the sell/wait reason, ask Saathi in Marathi.

**Done when:** everything passes, or each remaining failure is listed with cause and impact.

## PART 7: Final QA, docs and release
**Tasks:** run the dead-button audit on web and Android; check contrast, font scaling and TalkBack labels; measure web bundle size and fix anything obviously heavy; rebuild the debug APK and copy it to `artifacts/FairFarm-debug.apk` only if you built it yourself; update `README.md`, `apps/android/README.md`, `DOCKER_README.md` (with the agent handoff prompt), `docs/TESTING.md`, `docs/DATA.md` and `docs/PROGRESS.md` so they describe only what truly works. Remove docs claims about stubs.

**Final report:** what changed, before-and-after notes for each audit finding in section 2, real test results, screenshots list, commands to run everything, demo login, what I must verify myself (native Marathi and Hindi wording, real Agmarknet import, helpline numbers) and known limitations.

## PROMPT END