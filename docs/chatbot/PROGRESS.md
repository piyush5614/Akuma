# FairFarm Saathi progress

- [x] Part 0 - Discovery and design doc
- [ ] Part 1 - Contract, schemas, glossary and knowledge base
- [ ] Part 2 - Language layer
- [ ] Part 3 - Orchestrator, providers, tools, grounding and safety
- [ ] Part 4 - API endpoints, sessions and limits
- [ ] Part 5 - Android chat feature
- [ ] Part 6 - Dashboard add-on
- [ ] Part 7 - Evaluation, integration and docs

## Part 0 result

The repository was inspected before feature implementation. The backend has
the required domain route families and a minimal rules chat provider, while
Android has Retrofit, Room/osmdroid dependencies, and a Compose shell but no
chat UI, persistence wiring, Hilt setup, or voice integration. The web app has
no Saathi admin page or chat analytics.

The feature prompt's requested chat contract is broader than the existing
`POST /api/v1/chat` contract, so Parts 1-4 must update schemas, OpenAPI,
backend behavior, and client integrations as one traced change. Current
trend, seasonality, crop-profit, and recommendation data are demo/in-memory
services and must remain explicitly labeled.
