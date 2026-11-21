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

