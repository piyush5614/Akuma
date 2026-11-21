# FairFarm: Master Build Prompt for the Coding Agent
**For me (the human):** Create an empty folder named fairfarm, open it in VS Code or Antigravity, and paste everything below the line `PROMPT START` into the agent. After each completion report, reply `CONTINUE`. Once the repo exists, save this file as `docs/MASTER_PROMPT.md`. To let the agent run parts back to back, add `AUTO_CONTINUE=true` at the top of your message (it still stops if blocked).

---

## PROMPT START

### 0. Role and mission
You are a senior team in one person: full-stack engineer, Android engineer, UI/UX designer and DevOps lead. Build FairFarm, a three-part product for Indian farmers (hackathon problem 6.2: 'Which Mandi Pays More Today?'):

1. **Backend API**: the single source of truth for all logic.
2. **Web dashboard** for admins and agriculture officers.
3. **Android farmer app**: installable, working with the same backend.
Promise to farmers: *We don't show prices, we show what ends up in your pocket.* Core features: net-profit ranking of nearby mandis, map view, sell-now-or-wait hint, seasonality insights (when prices usually rise), which-crop-to-grow profit suggestions, Marathi/Hindi/English with voice, and trust labels on data freshness.

### 1. Working protocol (applies to every part)

1. Do ONE part at a time, in order. Before each part, re-read this prompt, `docs/PROGRESS.md` and `docs/DECISIONS.md`.
2. When a part is done, post the completion report below, update `docs/PROGRESS.md`, commit, then STOP and wait for me to say CONTINUE.
3. Never claim something works unless you ran it. Report real commands and real results. If you cannot run something (for example no Android SDK), say so plainly and list the exact steps left for me.
4. If blocked, stop and post a `⛔ PART N BLOCKED` report: cause, what you tried, options. Never fake output, silently stub features, or weaken tests to make them pass.
5. Ask me questions only for decisions only I can make. Otherwise choose a sensible default and record it in `docs/DECISIONS.md`.
6. Use conventional commits, one or more per part.
**Completion report format**

```
✅ PART N COMPLETE: <name>
Done: <3-6 bullets>
Files: <created/changed, grouped by folder>
Ran: <commands + result>
Checks: <tests/lint/build status with counts>
Assumptions / known issues: <list or none>
Next: PART N+1 <name>. Reply CONTINUE.
```

### 2. Engineering standards

- Use the latest stable versions at build time, verified with the package manager, and pin them (commit lockfiles).
- No hardcoded secrets, URLs or magic numbers. Config comes from `.env` (only `.env.example` is committed).
- No dead buttons, no TODO placeholders, no lorem ipsum on shipped screens. Every button, tab, chip and menu item must do something real.
- Every user-facing string exists in English, Marathi and Hindi (i18n files, no inline strings).
- Handle loading, empty, error and offline states on every screen.
- Accessibility: AA contrast, touch targets of at least 48dp, never color alone (pair it with an icon or text).
- Money: Decimal or integers in the backend, INR, round half-up to whole rupees for display, unit is quintal.
- Demo data is labelled DEMO in the database (`is_demo=true`), in the UI footer and in the README. Never present demo numbers as real.
- Every module has tests, functions stay small, lint and format configs are included.

### 3. Domain rules (single source of truth, implemented ONLY in the backend)

```
road_km          = haversine_km(farmer, mandi) * road_factor      (default 1.3)
transport        = road_km * transport_rate_per_quintal_km        (default 0.60, ASSUMPTION)
fee              = modal_price * fee_pct                          (default 1.0%, ASSUMPTION)
shrinkage        = modal_price * shrinkage_pct(crop)              (per crop, ASSUMPTION)
net_per_quintal  = modal_price - transport - fee - shrinkage
total_net        = net_per_quintal * quantity_quintal
```

- Use the published modal price as is. Never average modal prices across mandis. A missing report is NO_REPORT, never zero.
- Freshness: FRESH (1 day old or less), STALE (2 to 7 days), OLD (over 7 days), NO_REPORT. Rank only FRESH and STALE mandis; show OLD greyed out below the ranking.
- Ranking: total_net descending, ties broken by distance.
- **Sell-or-wait** (rule-based, thresholds in config, unit-tested): slope of the last 7 reported modal prices (% per day), arrivals change (last 3 days vs the prior 7), seasonal expectation (next 14 days vs now). WAIT if slope is above +1%/day and arrivals are falling by more than 10%, or if the seasonal rise is above 5% with slope of 0 or more. SELL_NOW if slope is below -1%/day, or arrivals rise more than 15% with slope of 0 or less, or the crop is highly perishable. Otherwise UNSURE. Return reason codes, a plain sentence in en/mr/hi, and the disclaimer 'Guidance, not a guarantee'.
- **Backtest:** compare the rule against the baseline 'same as last week' on history and expose the measured hit rate to the dashboard. Never claim accuracy beyond what is measured.
- **Seasonality:** month-wise price index (monthly median modal price divided by yearly median) per crop, with best and worst months.
- **Crop profit:** profit range per acre = (harvest-month price p25 to p75 x yield range) minus cost per acre, risk-adjusted by crop water need vs the farmer's water availability (low, medium, high), price volatility, perishability and a herd warning (price up more than 25% in 60 days). Rank by risk-adjusted midpoint and always show the range. Crop assumptions are DEMO values with a `source` column.
- **Chat:** rule-based intent classifier (best_mandi, price_today, sell_or_wait, which_crop, help) over en/mr/hi keywords that calls the same services and returns templated answers plus suggestion chips. Put it behind a `ChatProvider` interface so an LLM can be plugged in later (not required now).

### 4. Repository structure (match exactly; add files only when justified)

```
fairfarm/
  README.md
  AGENTS.md
  DOCKER_README.md
  Makefile
  docker-compose.yml
  .env.example
  .gitignore
  .editorconfig
  docs/            ARCHITECTURE.md, API_CONTRACT.md, DESIGN_SYSTEM.md, DATA.md,
                   TESTING.md, DECISIONS.md, PROGRESS.md, MASTER_PROMPT.md, design/
  backend/
    Dockerfile, pyproject.toml, alembic/
    app/           main.py, api/v1/, core/, db/, models/, schemas/, services/, i18n/
    tests/         unit/, api/
    scripts/       seed_demo.py, import_agmarknet.py
  apps/
    web/           Dockerfile, nginx.conf, src/{app,pages,features,components,api,i18n,styles,lib}, tests
    android/       README.md, gradle wrapper, app/src/main/java/.../{ui,data,domain,di,util}, res/
  data/            demo/ (CSV seeds), geo/
  scripts/         e2e_check.py, contract_check.py, dev_up.sh
  artifacts/       FairFarm-debug.apk after build (git-ignored except .gitkeep)
```

### 5. Tech stack (change only with a recorded reason)

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PostgreSQL 16 (SQLite for quick local runs), JWT + bcrypt, pytest, ruff.
- **Web:** React + TypeScript + Vite, Tailwind CSS, TanStack Query, React Router, Recharts, Leaflet + OpenStreetMap (no API key), Lucide icons, Vitest + Testing Library, ESLint + Prettier.
- **Android:** Kotlin, Jetpack Compose (Material 3), MVVM + repository, Hilt, Retrofit + OkHttp + kotlinx.serialization, Room (offline cache), osmdroid (OpenStreetMap, no API key), Android TextToSpeech and SpeechRecognizer, Navigation Compose, min SDK 24, compile and target SDK = latest stable the installed SDK supports.
- **DevOps:** Docker, docker compose, Makefile, GitHub Actions workflow (lint, test, build).

### 6. Design direction (original design inspired by my reference image; do NOT copy it)
Reference mood: minimalist and airy, near-black text on off-white, one lime-green accent, big confident headings, rounded cards, pill buttons with a small circular arrow chip, soft borders, calm motion. Create your own FairFarm brand and layouts. Do not reuse the reference's photos, copy text or exact layout.

Starting tokens (refine in Part 2): lime accent `#C8EE5A`, ink `#101410`, canvas `#F8F9F4`, surface `#FFFFFF`, line `#E4E7DC`, muted text `#667064`, success `#2E9E5B`, warning `#E0A100`, danger `#D64545`. Radius: cards 20, pills 999. Fonts: Inter (Latin) and Noto Sans Devanagari (Marathi and Hindi), bundled with the apps. One token file feeds both the web CSS variables and the Android theme.

### 7. API surface (v1; OpenAPI is the contract and `/openapi.json` must be exact)
`GET /health`, `GET /meta` (api version, min_app_version, demo flag), `GET /crops`, `GET /mandis`, `POST /recommend`, `GET /mandis/{id}/trend`, `GET /insights/seasonality`, `GET /insights/crop-profit`, `GET /insights/backtest`, `GET /regions/prices`, `POST /chat`, `POST /auth/login`, and admin routes (JWT): `GET /admin/summary`, `GET` and `PUT /admin/settings`, `POST /admin/data/import`, `GET /admin/queries`.

Validation: quantity 0.1 to 10000 quintal; lat/lng in range; radius 5 to 300 km; one error body shape `{code, message, details}`; every response carries `data_as_of` and `is_demo`.

---

## PART 0: Preflight and scaffold
**Goal:** a clean, committed, professional skeleton.

**Tasks:** check installed tools and versions (git, Python, Node, Docker, JDK, Android SDK, adb) and record them in `docs/DECISIONS.md`; create the exact folder tree from section 4 (`.gitkeep` only where needed); add `.gitignore`, `.editorconfig`, `.env.example`, a `Makefile` (targets: help, up, down, seed, test, lint, e2e) and structured docs; create `docs/PROGRESS.md` with a checklist of all parts; run `git init` and make the first commit; save this prompt as `docs/MASTER_PROMPT.md`.

**Done when:** the tree matches, `make help` works and the first commit exists.

## PART 1: Specification and API contract
**Goal:** contracts before code.

**Tasks:** write `docs/ARCHITECTURE.md` (a mermaid diagram: Agmarknet or demo data, loader, database, API, then web and Android), `docs/DATA.md` (tables, columns, record_type, freshness, demo flag, and notes on Agmarknet: what modal price means, missing reports, portal structure changes), and `docs/API_CONTRACT.md` (every endpoint with request and response JSON examples, text in en/mr/hi where returned, and error codes). Create the Pydantic schemas in `backend/app/schemas/` to match.

**Done when:** every endpoint in section 7 is documented with examples and the schemas import without errors.

## PART 2: Design system and screen specs (I review this part)
**Goal:** a design I can approve before any UI code.

**Tasks:** write `docs/DESIGN_SYSTEM.md` (tokens, type scale, spacing, components, states, motion, accessibility, i18n rules). Create `docs/design/tokens.json` and generate `apps/web/src/styles/tokens.css` and the Android theme files from it. Create `docs/design/preview.html`, a static page I can open in a browser showing the palette, type, buttons, cards, chips, map pin legend and sample charts. Write wireframes (ASCII or SVG) for every screen in `docs/design/`.

**Web pages:** Login; Overview (KPIs, searches by crop, average net gain, data freshness, top mandis); Price Explorer (crop picker, map, table, trend); Regions (district average price circles on the map); Insights (seasonality, crop profit, backtest score); Data and Settings (CSV import, freshness table, transport/fee/shrinkage editor); Query log.

**Android screens:** Language select; Home (crop, quantity, location by GPS or manual search); Result (best-mandi hero card, ranked list, map toggle, sell-or-wait chip, speaker button); Mandi detail (trend chart, cost breakdown, Navigate button); Insights (seasonality, crop profit); Ask (chat, mic, speaker, suggestion chips); Settings (language, vehicle rate, water availability, about and data freshness). Bottom navigation: Home, Insights, Ask, Settings.

**Done when:** `preview.html` opens and every screen has a wireframe. Then STOP for my review.

## PART 3: Backend
**Tasks:** models and migrations; services (`pricing`, `ranking`, `trend`, `seasonality`, `crop_profit`, `backtest`, `chat`, `freshness`) implementing section 3 exactly; a router for every endpoint in section 7; JWT admin auth (seeded admin from env); CORS from env; request logging with request ids; one consistent error handler; `/recommend` logs anonymised queries (no personal data, location rounded to 2 decimals) for dashboard analytics; server-generated text in en/mr/hi.

**Tests:** unit tests for net price math (hand-computed cases), ranking ties, freshness, every sell-or-wait branch, seasonality and crop-profit risk adjustment; API tests for every endpoint including validation errors and auth.

**Done when:** `pytest` passes, `ruff` is clean and `/openapi.json` matches `docs/API_CONTRACT.md`.

## PART 4: Demo data and seeding
**Tasks:** generate realistic DEMO data deterministically (fixed random seed): about 25 Maharashtra mandis with approximate coordinates (mark them approximate), 8 crops (onion, tomato, soybean, wheat, jowar, gram, cotton, pomegranate), 2 years of daily prices ending today with seasonality, noise, arrivals and realistic gaps (no_report days), a crop assumptions table, and a demo admin. `seed_demo.py` must be idempotent. Also write `import_agmarknet.py`, which imports a real Agmarknet CSV export (from data.gov.in or the portal) into the same tables using the documented columns, with clear errors if the structure changes. Do not scrape websites.

**Done when:** `make seed` works twice without duplicates and `/recommend` returns sensible ranked results with varied freshness.

## PART 5: Web dashboard
**Tasks:** build every page from Part 2 using the approved design; a typed API client checked against `/openapi.json`; TanStack Query with loading, empty and error states; i18n (en/mr/hi); responsive from tablet to desktop; Leaflet maps with colored pins (green, amber, red plus icon and text); Recharts for trend and seasonality; a settings editor that really updates the backend; CSV import with a validation preview.

**Tests:** component tests for key widgets and API client tests with mocks.

**Done when:** `npm run lint`, `npm run typecheck`, `npm test` and `npm run build` pass and the app works against the running backend.

## PART 6: Android farmer app
**Tasks:** create a complete Gradle project in `apps/android` (wrapper included) that opens in Android Studio with no manual fixes. Implement every screen from Part 2 in Compose with the shared tokens, a Retrofit client for the API, and a Room cache so the last results and crop list work offline with a visible 'last updated' banner. Use GPS with a permission rationale and a manual fallback, an osmdroid map with colored pins, TextToSpeech in Marathi, Hindi and English (check voice availability and show a friendly prompt to install the voice if missing), SpeechRecognizer on the Ask screen, a Navigate button that opens Google Maps through a geo intent, instant language switching, and a sell-or-wait chip, freshness badges and the disclaimer on result screens.

**Connection config:** `BASE_URL` comes from `local.properties` or a Gradle property, default `http://10.0.2.2:8000/api/v1` for the emulator; physical phones use the computer's LAN IP. Cleartext traffic is allowed in debug only through a debug network-security-config; release builds require HTTPS. The app never recomputes prices; it only displays backend results.

**Tests:** unit tests for mappers, repositories (fake API) and ViewModels.

**Done when:** `./gradlew testDebugUnitTest lintDebug` passes, or you state exactly what could not run.

## PART 7: Integration and connection logic
**Goal:** the three parts behave as one product.

**Tasks:** write `scripts/contract_check.py`, which parses the Android Retrofit interface and the web API client and verifies that every path, method and field they use exists in `/openapi.json`. Implement timeouts, retry with backoff for GET only, safe handling of POST retries, the `GET /meta` compatibility check (the app shows 'please update' when below min_app_version), consistent error mapping in both clients, and verified CORS for the web origin. Make sure language codes (en, mr, hi) and units are identical across all three parts.

**Done when:** the contract check passes and every mismatch was fixed at its source.

## PART 8: Docker and agent handoff
**Tasks:** `backend/Dockerfile` (slim, non-root, healthcheck); `apps/web/Dockerfile` (multi-stage, nginx, runtime `config.js` for the API URL); `docker-compose.yml` (db, backend, web; healthchecks; named volumes; health-based `depends_on`; dev override); auto-migrate and idempotent seed on first start; Makefile targets; a GitHub Actions workflow.

Write `DOCKER_README.md` with: quick start, services and ports, an env vars table, common commands, troubleshooting, and a section **AGENT HANDOFF PROMPT** in a code block that I can paste into Antigravity. The handoff prompt must tell a fresh agent to: read `AGENTS.md`, `docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md` and `docs/API_CONTRACT.md` in that order; run `make up`, then `make test`, then `make e2e`; understand where each app lives, how the parts connect, what is done and what is next; and follow the rules in sections 1 and 2. Also write `AGENTS.md` with short conventions and commands.

**Done when:** `docker compose up --build` brings all services up healthy and the web dashboard loads at the documented port.

## PART 9: Full system test
**Tasks:** write `scripts/e2e_check.py`. It targets the running stack, waits for health, logs in as the demo admin, calls every endpoint, validates responses against the Pydantic schemas, independently recomputes net price for 5 sample requests and compares, checks the ranking order, checks the CORS preflight from the web origin, checks that all three languages return text, and checks error bodies. Run every suite (backend, web, Android unit tests, contract check, e2e), fix every failure at its root cause, then write `docs/TESTING.md` with the exact commands, the latest results and a manual smoke checklist (web: each page and button; Android: each screen and button).

**Done when:** everything passes, or each remaining failure is listed with its cause and impact.

## PART 10: Android build artifact
**Tasks:** run `./gradlew assembleDebug`. If it succeeds, copy the APK to `artifacts/FairFarm-debug.apk`, print its size and verify it with `aapt` or `apkanalyzer` if available. If the SDK is missing, do NOT claim a build; write precise steps instead. Write `apps/android/README.md` covering requirements, opening in Android Studio, setting the backend URL (emulator vs real phone), running, building the APK, installing with `adb install -r`, permissions used, and troubleshooting (cleartext, 10.0.2.2, firewall, same Wi-Fi, missing TTS voice data).

**Done when:** the APK exists and you built it, or the README plus an honest status explains what I must do.

## PART 11: Final polish and README
**Tasks:** write the root `README.md` (what and why, feature list, architecture diagram, quick start with Docker and manual, a 3-minute demo script, screenshots if you can capture them, API overview, testing, data and demo-data disclaimer, roadmap: MSP check, export price signals, drought and weather risk link, officer alerts). Remove dead code, check that no secrets are committed, finalize `docs/PROGRESS.md`, and run the complete test set one last time.

**Final report:** what works, what I must verify myself, demo login, URLs, commands to start everything, and known limitations.

## PROMPT END