# Decisions

## Part 0

- Repository root: `C:\Users\asus4\Desktop\FairFarm`.
- The requested stack and directory structure are retained from the master prompt.
- The current environment reports Git 2.56.0, Python 3.13.5, Node 22.20.0,
  Docker 29.3.1, and adb 1.0.32.
- Java/JDK and GNU Make were not found on PATH during preflight.
- Python 3.12 was requested by the product specification, but Python 3.13.5 is
  the available interpreter; compatibility must be verified when backend work begins.
- The initial scaffold uses `.gitkeep` for otherwise-empty required directories.

## Part 1

- API responses use a generic `data`, `data_as_of`, and `is_demo` envelope;
  errors use `code`, `message`, and `details`.
- Pydantic v2 schemas use `Decimal` for INR and quantity values to avoid
  floating-point money calculations.
- API contract documentation is the source of truth for the Part 3 routers;
  no client or backend route was implemented in this part.

## Part 2

- `docs/design/tokens.json` is the canonical token source; web CSS and Android
  theme values mirror it.
- The design preview is static HTML so it can be reviewed without installing
  the future web or Android applications.
- The first Android theme files are intentionally standalone until the Gradle
  project is created in Part 6.

## Part 3

- The initial backend uses a deterministic in-memory store so the API and
  domain rules can be tested before database/seeding work in Part 4.
- Pricing uses `Decimal` throughout and keeps all calculations in backend
  services; clients must not recompute results.
- JWT authentication defaults to environment configuration and retains a
  development fallback only for local tests; production deployment must set a
  strong `JWT_SECRET` and admin password.
- Async API tests use httpx ASGI transport because the installed Starlette
  TestClient is incompatible with the installed httpx release.

## Part 4

- SQLite is the local seed target and is ignored from Git; deployment can point
  `DATABASE_PATH` at a persistent database location.
- Demo generation uses fixed seed `20261121`, stable row IDs, and replaces only
  `DEMO` records so imported `AGMARKNET` records survive reseeding.
- Generated demo history intentionally contains approximately 3.5% missing
  reports to exercise `NO_REPORT` and varied freshness behavior.

## Part 5

- The web app uses Vite, React, TypeScript, TanStack Query, React Router,
  Lucide icons, and Vitest; `apps/web/package-lock.json` pins the install.
- The API base URL is supplied by `VITE_API_URL`, defaulting to the documented
  local backend URL for development.
- `npm install` reported six transitive audit findings in the current package
  graph; the dashboard build and tests pass, but dependency remediation should
  be handled before production deployment.

## Part 6

- Android uses `BuildConfig.BASE_URL`, defaulting to the emulator address in
  `gradle.properties`; release builds use an HTTPS placeholder until deployment
  configuration exists.
- The project is source-complete but not locally build-verified because the
  preflight environment still lacks Java/JDK and Gradle. Android Studio/JDK 17
  is required for the first compile.

## Part 7

- Contract verification imports the backend FastAPI OpenAPI document and
  extracts Retrofit annotations plus web client paths; query strings are
  normalized before comparison.
- Only GET requests retry, with bounded exponential backoff; POST and PUT
  requests execute once to avoid duplicate writes.
- Android compares semantic version strings from `/meta` and exposes a
  user-facing update message when the installed app is below the backend
  minimum version.

## Repair redesign visual pass

- The web redesign keeps FairFarm's agriculture domain while adopting the
  supplied reference's fixed-sidebar administration structure, pale canvas,
  cobalt identity, compact KPI cards, soft borders, and restrained status
  palette.
- Blue is the primary interactive and answer colour. Lime remains a small
  brand accent, consistent with the existing FairFarm identity.
- The existing backend and API contract remain authoritative. The redesign
  adds no client-side price or ranking calculations.

## Part 8

- Compose includes PostgreSQL as the target database service and a persistent
    SQLite volume for the current seed-backed API; switching the API runtime to
    PostgreSQL remains a database integration task.
- The web image writes `config.js` at container startup so the browser API URL
    can change without rebuilding static assets.
- CI runs backend and web checks independently; Android remains locally
    unverified until a JDK/Android SDK environment is available.

## Part 9

- The E2E checker validates the response envelope, five recommendation
    quantities, descending net-return ranking, all public/admin routes, all
    three language outputs, CORS preflight, and the common validation error body.
- FastAPI request validation now uses the documented `{code, message, details}`
    shape rather than the framework default.

## Part 10

- Android builds are verified with JDK 17, Android SDK API 35, and Gradle
  8.14.3 using the checked-in Gradle wrapper.
- `assembleDebug`, `testDebugUnitTest`, and `lintDebug` all pass. The generated
  APK is copied to `artifacts/FairFarm-debug.apk` and its package metadata was
  verified with `aapt`.
- Gradle reports an unchecked ViewModel factory cast and a native library that
  cannot be stripped; neither prevents the debug build. Docker image builds
  remain unverified when the Docker daemon is unavailable.

## Saathi Part 7

- The golden evaluation uses deterministic rules mode by default and supports
  optional live API mode without requiring provider credentials for the
  reproducible baseline.
- The evaluation includes 180 utterances across English, Marathi, and Hindi;
  its measured accuracy is reported rather than treating the golden set as a
  production accuracy claim.

## Live location and Saathi UX

- Web geolocation is requested through the browser permission API and passed
  into mandi and Saathi requests; Pune coordinates remain an explicitly
  labelled fallback when permission is denied or unavailable.
- Android uses the existing Google fused-location dependency and requests
  coarse/fine permissions on app start. The last known location is passed to
  recommendation and chat calls, with the same labelled Maharashtra fallback.
- The backend remains the source of truth for the available market set and
  ranking. The current demo runtime contains Pune, Nashik, and Satara records;
  broader city coverage requires importing or adding validated market data.
- Saathi's best-mandi tool defaults to the API's 300 km maximum so a response
  can include both nearby mandis and larger regional market centres; ranking
  still applies distance and backend net-return rules.

## Guided crop planning

- The first guided catalogue uses common Indian vegetables, grains, and fruits
  with English, Hindi, and Marathi names. It is intentionally expandable rather
  than claiming to be an exhaustive national crop database.
- Next-crop suggestions accept crop history, preferred category, and water
  availability. Results are advisory, explain their water/category/history
  reasoning, and remain based on demo assumptions until validated agronomic and
  market data is imported.
- The guided web flow uses manual latitude/longitude entry as selected for this
  feature; Android retains its existing device-location permission path and
  allows the existing fallback.

## Interface redesign

- The redesign uses warm ivory, deep forest green, lime accent, translucent
  glass-like cards, and large editorial headings across web and Android.
- Primary actions are intentionally elevated and floating: sticky inside long
  web forms and an `ExtendedFloatingActionButton` above Android navigation.
- The redesign is presentation-only; backend contracts, pricing logic, and
  recommendation ranking remain unchanged.

## Deterministic demo seeding

- Demo history uses 365 deterministic days. Repeated seeding returns the existing
  demo counts without deleting and recreating price and arrival history when
  the 25-mandi, 8-crop demo structure is already present.

## Android WebView startup

- The standalone Android application serves the bundled web build locally from
  port 4173. It no longer depends on a separately running Vite server.
- Android injects `BASE_URL` as `window.__FAIRFARM_CONFIG__.API_URL`; the
  emulator default remains `10.0.2.2:8000`, while physical phones use their
  configured LAN backend IP.
- WebView startup and HTTP/resource failures show a readable retry screen
  instead of a blank white WebView.

## Native Android app

- The standalone Android project no longer uses a WebView or bundles web assets.
- Native Compose screens call the existing FastAPI API through Retrofit and
  kotlinx.serialization; clients do not duplicate backend pricing or ranking
  calculations.

