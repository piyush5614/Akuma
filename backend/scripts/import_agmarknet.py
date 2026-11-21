"""Import a documented Agmarknet CSV export without scraping the portal."""

import csv
import os
import sqlite3
import sys
from pathlib import Path

REQUIRED = {"crop_id", "mandi_id", "reported_on", "modal_price_inr"}
DB_PATH = Path(os.getenv("DATABASE_PATH", Path(__file__).parents[1] / "fairfarm.db"))


def import_csv(csv_path: Path, database_path: Path = DB_PATH) -> int:
    with csv_path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED - columns
        if missing:
            raise ValueError(f"Agmarknet CSV structure changed; missing columns: {', '.join(sorted(missing))}")
        rows = []
        for line_number, row in enumerate(reader, 2):
            try:
                price = float(row["modal_price_inr"])
                if price < 0:
                    raise ValueError("modal price cannot be negative")
                rows.append((f"AGMARKNET-{line_number}", row["crop_id"], row["mandi_id"], row["reported_on"], price, "AGMARKNET", 0))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid Agmarknet row {line_number}: {exc}") from exc
    with sqlite3.connect(database_path) as database:
        database.executemany(
            "INSERT OR REPLACE INTO price_reports (id, crop_id, mandi_id, reported_on, modal_price_inr, record_type, is_demo) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        database.commit()
    return len(rows)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python backend/scripts/import_agmarknet.py <export.csv>")
    print(f"Imported {import_csv(Path(sys.argv[1]))} AGMARKNET price reports")
