"""Verify the paths/methods used by both clients exist in backend OpenAPI."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app  # noqa: E402


def client_operations(path: Path) -> set[tuple[str, str]]:
    source = path.read_text(encoding="utf-8")
    operations: set[tuple[str, str]] = set()
    for method, route in re.findall(r'@(GET|POST|PUT|DELETE)\("([^"]+)"\)', source):
        operations.add((method.lower(), "/" + route.lstrip("/").split("?")[0]))
    for route, method in re.findall(r'request<[^>]+>\("([^"]+)"(?:,\s*\{[^}]*method:\s*"([A-Z]+)")?', source):
        operations.add(((method or "GET").lower(), "/" + route.lstrip("/").split("?")[0]))
    return operations


def main() -> int:
    openapi = app.openapi()
    available = {
        (method, path.removeprefix("/api/v1"))
        for path, item in openapi["paths"].items()
        for method in item
        if method in {"get", "post", "put", "delete"}
    }
    clients = {
        "android": client_operations(ROOT / "apps/android/app/src/main/java/com/fairfarm/data/FairFarmApi.kt"),
        "web": client_operations(ROOT / "apps/web/src/api/client.ts"),
    }
    used = set().union(*clients.values())
    missing = sorted(used - available)
    if missing:
        print("Missing client operations:")
        for operation in missing:
            print(f"  {operation[0].upper()} {operation[1]}")
        return 1
    print(f"Contract check passed: {len(used)} client operations are present in OpenAPI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
