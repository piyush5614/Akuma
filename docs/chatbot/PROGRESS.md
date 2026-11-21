# FairFarm Saathi progress

- [x] Part 0 - Discovery and design doc
- [x] Part 1 - Contract, schemas, glossary and knowledge base
- [x] Part 2 - Language layer
- [x] Part 3 - Orchestrator, providers, tools, grounding and safety
- [x] Part 4 - API endpoints, sessions and limits
- [x] Part 5 - Android chat feature
- [x] Part 6 - Dashboard add-on
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

## Part 3 result

Added rules, Anthropic, and OpenAI-compatible provider adapters; a Pydantic
validated read-only tool registry; server-owned context handling; a three-round
provider loop; eight-second timeout fallback; ten-minute TTL caching; grounding
validation; prompt-injection, out-of-scope, and distress handling; and log
redaction for phone, identity, and bank data. Rules mode remains network-free.

The focused orchestrator suite has 7 passing tests, and the full backend suite
has 81 passing tests. Public endpoint migration, sessions, rate limits, and
Android/web wiring were deferred to the following parts.

## Part 4 result

Migrated `POST /api/v1/chat` to accept the Saathi contract while retaining the
legacy request shape for existing clients. Added 30-minute in-memory sessions
that retain only crop, quantity, and last recommendation context, per-device
rate limiting with retry hints, request IDs, localized starters, and feedback
acceptance storage. The new response includes reply language/script, grounding,
fallback, tool, demo, and request metadata.

The chat API tests have 2 passing cases, the session/rate-limit tests have 3
passing cases, and the full backend suite has 86 passing tests. Persistent
session/feedback storage and dashboard analytics remain later hardening work.

## Part 5 result

Added Android Retrofit models and endpoints for chat, starters, and feedback;
repository methods; ViewModel chat state with duplicate-send protection,
session continuity, offline errors, and a 100-message in-process history; and
the Compose Ask panel with starter prompts, send, loading, and clear-chat
controls. The Android client still uses the existing manual location fallback.
Room persistence, voice input/output, native data cards, and GPS context are
explicitly deferred rather than presented as complete.

## Part 6 result

Added authenticated Saathi admin metrics and test-console endpoints backed by
in-memory chat events and feedback, including language, intent, fallback,
refusal, grounding, and rating summaries. Added the web Saathi dashboard,
navigation entry, route, typed API client methods, and localized navigation
labels. Backend API tests cover both admin endpoints.

The focused chat API suite has 3 passing tests, Ruff passes, and the web
typecheck, lint, Vitest suite, and production build pass. Metrics and chat
events remain in-memory; persistent analytics are deferred to a later
hardening step.
