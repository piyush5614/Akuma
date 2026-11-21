# FairFarm Docker

## Quick start

Copy `.env.example` to `.env`, then run:

```text
docker compose up --build
```

The web dashboard is at `http://localhost:5173`; the API is at
`http://localhost:8000/docs`. The backend seeds idempotent DEMO data on start.

| Variable | Purpose | Default |
|---|---|---|
| `JWT_SECRET` | JWT signing secret | replace in production |
| `ADMIN_PASSWORD` | Demo admin password | `change-me` |
| `POSTGRES_PASSWORD` | Postgres service password | development-only value |
| `FAIRFARM_API_URL` | Browser-visible backend URL | `http://localhost:8000/api/v1` |

## Commands

`docker compose up --build`, `docker compose down`, and
`docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`.
The backend data volume contains the local SQLite seed database; the Postgres
service is ready for the persistence migration in a later hardening pass.

## Troubleshooting

- Check `docker compose ps` and `docker compose logs backend`.
- Port 8000 or 5173 conflicts require changing the host-side mapping.
- A physical Android device must use the computer LAN IP, not `10.0.2.2`.
- Replace all development secrets before deployment.

## AGENT HANDOFF PROMPT

```text
Read AGENTS.md, docs/PROGRESS.md, docs/DECISIONS.md, docs/ARCHITECTURE.md,
and docs/API_CONTRACT.md in that order. Run `make up`, then `make test`, then
`make e2e`. Understand that backend lives in backend/, the web app lives in
apps/web/, and the Android app lives in apps/android/. The backend is the
single source of truth and clients use the v1 API contract. Follow sections 1
and 2 of docs/MASTER_PROMPT.md, report real commands/results, do not commit
secrets, and continue from the first unchecked part in docs/PROGRESS.md.
```

