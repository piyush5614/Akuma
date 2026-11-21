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

