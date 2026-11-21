# FairFarm testing

## Automated commands

```text
python -m pytest -q backend
python -m ruff check backend
cd apps/web && npm ci && npm run typecheck && npm run lint && npm test && npm run build
python scripts/contract_check.py
python scripts/e2e_check.py
```

The E2E command targets `FAIRFARM_API_URL` (default
`http://127.0.0.1:8000/api/v1`) and expects the stack to be running.

## Latest results

- Backend: 10 tests passed.
- Web: 2 tests passed; typecheck, lint, and build passed.
- Contract checker: passed with 6 client operations.
- Android: not run; Java/JDK and Gradle are unavailable in the current environment.
- Docker/E2E: blocked when Docker Desktop is not running.

## Manual smoke checklist

- Web: login, overview ranking, explorer freshness, regions, insights, CSV
  preview, settings save, query log, language switch, and responsive layout.
- Android: language selection, crop/quantity/location, recommendation ranking,
  freshness, sell-or-wait disclaimer, insights, ask, settings, offline banner,
  navigation intent, TTS, and speech recognition.

