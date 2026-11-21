# FairFarm Saathi progress

- [x] Part 0 - Discovery and design doc
- [x] Part 1 - Contract, schemas, glossary and knowledge base
- [x] Part 2 - Language layer
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

## Part 1 result

Added the Saathi request, response, typed card, feedback, and starter schemas
while retaining the legacy chat models until the runtime migration. Extended
the API contract with the new chat payload and starter/feedback endpoints.
Added crop/unit/market glossary entries, localized canned strings marked for
native review, and curated English, Marathi, and Hindi knowledge-base entries
for terms, screens, settings, and offline behavior. Runtime endpoint wiring is
intentionally deferred to Part 4.

## Part 2 result

Added NFC/spacing/punctuation normalization, language and script detection for
English, Marathi, Hindi, Devanagari, Latin, and mixed input, glossary-backed
crop/unit/market extraction, kg/tonne-to-quintal conversion, fuzzy alias
matching, and the rules intent router. The router covers greeting, help,
term meaning, best mandi, price, sell-or-wait, seasonality, crop choice,
out-of-scope, distress, and unknown intents.

The focused suite has 61 passing cases, including all prompt golden examples,
additional crop/intent/quantity variations, unit conversion, normalization,
and safety-priority cases. The full backend suite has 74 passing tests.
