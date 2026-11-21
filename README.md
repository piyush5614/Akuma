# FairFarm

FairFarm compares what a farmer is likely to keep per quintal after transport,
market fees, and crop shrinkage. It provides a FastAPI backend, a React admin
dashboard, and a Kotlin/Compose Android farmer app.

All displayed numbers are deterministic `DEMO` data unless replaced with
validated Agmarknet imports. The backend is the single source of truth for
pricing, freshness, ranking, and sell-or-wait rules.

## Quick start

### Backend

From the repository root on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python backend\scripts\seed_demo.py
python -m uvicorn backend.app.main:app --reload --port 8000
```

The API is available at `http://127.0.0.1:8000/api/v1`; health is at
`/api/v1/health`. The seeded demo admin is `admin@example.com` /
`change-me` for local development only.

### Web dashboard

```powershell
Set-Location apps\web
npm ci
npm run dev
```

Open `http://localhost:5173`, then use the demo admin credentials. Set
`VITE_API_URL` when the backend is not on the default local URL.

### Android

Open [apps/android](apps/android) in Android Studio, start the backend, and run
the `app` configuration on an emulator. The checked-in wrapper also supports:

```powershell
Set-Location apps\android
.\gradlew.bat testDebugUnitTest lintDebug assembleDebug
```

The verified debug APK is copied to `artifacts/FairFarm-debug.apk`.

## Product flow

1. Select a crop, quantity, and location in the farmer app or dashboard.
2. The API ranks nearby mandis by estimated total net return.
3. Review freshness labels, distance, costs, and the sell-now-or-wait guidance.
4. Use the live OpenStreetMap India view to inspect mandi markers and
   freshness.
5. Use Saathi as a conversational chatbox for mandi, price, and sell-or-wait
   questions.

Explorer, Regions, and Saathi request the browser's current location to focus
results around the farmer. The Android app requests coarse/fine GPS permission
and sends its last known location to the same backend. If permission is
declined, the UI clearly labels the Maharashtra demo fallback.

## API and project docs

- [API contract](docs/API_CONTRACT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Testing commands and results](docs/TESTING.md)
- [Docker guide](DOCKER_README.md)
- [Delivery progress](docs/PROGRESS.md)
- [Decisions and known constraints](docs/DECISIONS.md)
- [Saathi chatbot progress](docs/chatbot/PROGRESS.md)

## Verification status

The backend tests and Ruff checks, web typecheck/lint/tests/build, OpenAPI
contract checker, and black-box E2E checker pass locally. Android
`testDebugUnitTest`, `lintDebug`, and `assembleDebug` pass with JDK 17, Android
SDK API 35, and Gradle 8.14.3. Docker image builds require a running Docker
Desktop daemon and were not claimed when that daemon was unavailable.

Saathi rules-mode evaluation is reproducible with:

```powershell
python scripts\chat_eval.py --mode fake
```

Use `--mode live --limit 20` with a running API to evaluate a bounded sample
of the deployed contract without exhausting the API rate limit.
Provider mode is selected with `CHAT_PROVIDER=rules|anthropic|openai-compatible`;
LLM provider keys belong in local environment configuration only.

## Current limitations and roadmap

- The API currently serves the deterministic in-memory store; SQLite seeding
  and Agmarknet import are persistent preparation, not yet the runtime store.
- Compose includes PostgreSQL as a deployment target, but runtime PostgreSQL
  integration is still pending.
- The demo runtime currently contains three Maharashtra market records
  (Pune, Nashik, and Satara); nearby and larger-city recommendations will
  expand as validated market data is imported.
- Production readiness requires replacing demo credentials/secrets, connecting
  real data, adding operational monitoring, and completing the map/voice
  integrations.
- Saathi chat sessions, feedback, and metrics are currently in-memory.
- Marathi and Hindi responses require native-speaker review before production;
  see [the review checklist](docs/chatbot/NATIVE_REVIEW_CHECKLIST.md).
