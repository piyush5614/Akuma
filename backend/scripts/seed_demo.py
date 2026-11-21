"""Create deterministic DEMO data in a local SQLite database.

The script is deliberately idempotent: all DEMO rows are replaced in one
transaction, while AGMARKNET rows are preserved.
"""

import csv
import hashlib
import math
import os
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(os.getenv("DATABASE_PATH", Path(__file__).parents[1] / "fairfarm.db"))
DATA_DIR = Path(__file__).parents[2] / "data" / "demo"
SEED = 20261121
CROPS = [
    ("onion", "Onion", "कांदा", "प्याज", "high", 0.02, 85, 140, 70000),
    ("tomato", "Tomato", "टोमॅटो", "टमाटर", "high", 0.03, 100, 180, 90000),
    ("soybean", "Soybean", "सोयाबीन", "सोयाबीन", "low", 0.01, 10, 18, 32000),
    ("wheat", "Wheat", "गहू", "गेहूं", "low", 0.01, 12, 20, 28000),
    ("jowar", "Jowar", "ज्वारी", "ज्वार", "low", 0.01, 8, 14, 24000),
    ("gram", "Gram", "हरभरा", "चना", "low", 0.01, 8, 14, 30000),
    ("cotton", "Cotton", "कापूस", "कपास", "low", 0.02, 7, 12, 36000),
    ("pomegranate", "Pomegranate", "डाळिंब", "अनार", "medium", 0.03, 35, 60, 110000),
]
MANDI_NAMES = [
    ("pune", "Pune", 18.5204, 73.8567), ("nashik", "Nashik", 19.9975, 73.7898),
    ("nagpur", "Nagpur", 21.1458, 79.0882), ("solapur", "Solapur", 17.6599, 75.9064),
    ("kolhapur", "Kolhapur", 16.7050, 74.2433), ("sangli", "Sangli", 16.8524, 74.5815),
    ("satara", "Satara", 17.6805, 74.0183), ("ahmednagar", "Ahmednagar", 19.0948, 74.7480),
    ("aurangabad", "Aurangabad", 19.8762, 75.3433), ("jalgaon", "Jalgaon", 21.0077, 75.5626),
    ("akola", "Akola", 20.7002, 77.0082), ("amravati", "Amravati", 20.9374, 77.7796),
    ("beed", "Beed", 18.9891, 75.7601), ("buldhana", "Buldhana", 20.5293, 76.1842),
    ("dhule", "Dhule", 20.9042, 74.7749), ("latur", "Latur", 18.4088, 76.5604),
    ("nanded", "Nanded", 19.1383, 77.3210), ("parbhani", "Parbhani", 19.2600, 76.7760),
    ("hingoli", "Hingoli", 19.7147, 77.1420), ("washim", "Washim", 20.1110, 77.1330),
    ("yavatmal", "Yavatmal", 20.3899, 78.1307), ("wardha", "Wardha", 20.7453, 78.6022),
    ("chandrapur", "Chandrapur", 19.9615, 79.2961), ("ratnagiri", "Ratnagiri", 16.9902, 73.3120),
    ("nanded-rural", "Nanded Rural", 19.0500, 77.2500),
]


def schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS crops (
          id TEXT PRIMARY KEY, name_en TEXT NOT NULL, name_mr TEXT NOT NULL,
          name_hi TEXT NOT NULL, perishability TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS mandis (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, district TEXT NOT NULL,
          state TEXT NOT NULL, lat REAL NOT NULL, lng REAL NOT NULL,
          approximate_location INTEGER NOT NULL, is_demo INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS price_reports (
          id TEXT PRIMARY KEY, crop_id TEXT NOT NULL, mandi_id TEXT NOT NULL,
          reported_on TEXT NOT NULL, modal_price_inr REAL NOT NULL,
          record_type TEXT NOT NULL, is_demo INTEGER NOT NULL,
          UNIQUE(crop_id, mandi_id, reported_on, record_type)
        );
        CREATE TABLE IF NOT EXISTS arrival_reports (
          id TEXT PRIMARY KEY, crop_id TEXT NOT NULL, mandi_id TEXT NOT NULL,
          reported_on TEXT NOT NULL, quantity_quintal REAL NOT NULL,
          record_type TEXT NOT NULL, is_demo INTEGER NOT NULL,
          UNIQUE(crop_id, mandi_id, reported_on, record_type)
        );
        CREATE TABLE IF NOT EXISTS crop_assumptions (
          crop_id TEXT PRIMARY KEY, shrinkage_pct REAL NOT NULL,
          yield_p25 REAL NOT NULL, yield_p75 REAL NOT NULL,
          cost_per_acre REAL NOT NULL, water_need TEXT NOT NULL, source TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS users (
          email TEXT PRIMARY KEY, password_hash TEXT NOT NULL, role TEXT NOT NULL, is_demo INTEGER NOT NULL
        );
        """
    )


def stable_id(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:24]


def seed(connection: sqlite3.Connection) -> dict[str, int]:
    random.seed(SEED)
    schema(connection)
    connection.execute("DELETE FROM price_reports WHERE record_type = 'DEMO'")
    connection.execute("DELETE FROM arrival_reports WHERE record_type = 'DEMO'")
    connection.execute("DELETE FROM crops")
    connection.execute("DELETE FROM mandis")
    connection.execute("DELETE FROM crop_assumptions")
    connection.execute("DELETE FROM users WHERE is_demo = 1")
    connection.executemany("INSERT INTO crops VALUES (?, ?, ?, ?, ?)", [row[:5] for row in CROPS])
    connection.executemany("INSERT INTO mandis VALUES (?, ?, 'Maharashtra', 'Maharashtra', ?, ?, 1, 1)", [(i, n, lat, lng) for i, n, lat, lng in MANDI_NAMES])
    connection.executemany("INSERT INTO crop_assumptions VALUES (?, ?, ?, ?, ?, ?, ?)", [(r[0], r[5], r[6], r[7], r[8], "medium", "DEMO") for r in CROPS])
    connection.execute("INSERT INTO users VALUES (?, ?, 'admin', 1)", ("admin@example.com", "DEMO_PASSWORD_HASH"))
    today = date.today()
    price_rows, arrival_rows = [], []
    for crop_index, crop in enumerate(CROPS):
        crop_id = crop[0]
        base = 900 + crop_index * 450
        for mandi_index, (mandi_id, _, _, _) in enumerate(MANDI_NAMES):
            for day_offset in range(730):
                current = today - timedelta(days=729 - day_offset)
                if random.random() < 0.035:
                    continue
                seasonal = 1 + 0.16 * math.sin((current.timetuple().tm_yday + crop_index * 30) * 2 * math.pi / 365)
                noise = random.uniform(-0.06, 0.06)
                price = round(base * seasonal * (1 + noise) + mandi_index * 7, 2)
                arrival = round(max(10, (100 + random.uniform(-30, 30)) * (2 - seasonal)), 2)
                key = stable_id(crop_id, mandi_id, current.isoformat(), "DEMO")
                price_rows.append((key, crop_id, mandi_id, current.isoformat(), price, "DEMO", 1))
                arrival_rows.append((stable_id("arrival", key), crop_id, mandi_id, current.isoformat(), arrival, "DEMO", 1))
    connection.executemany("INSERT INTO price_reports VALUES (?, ?, ?, ?, ?, ?, ?)", price_rows)
    connection.executemany("INSERT INTO arrival_reports VALUES (?, ?, ?, ?, ?, ?, ?)", arrival_rows)
    connection.commit()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with (DATA_DIR / "crops.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name_en", "name_mr", "name_hi", "perishability"])
        writer.writerows([row[:5] for row in CROPS])
    with (DATA_DIR / "mandis.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "district", "state", "lat", "lng", "approximate_location", "is_demo"])
        writer.writerows([(i, n, n, "Maharashtra", lat, lng, 1, 1) for i, n, lat, lng in MANDI_NAMES])
    return {"crops": len(CROPS), "mandis": len(MANDI_NAMES), "prices": len(price_rows), "arrivals": len(arrival_rows)}


if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as database:
        counts = seed(database)
    print(f"Seeded DEMO data at {DB_PATH}: {counts}")
