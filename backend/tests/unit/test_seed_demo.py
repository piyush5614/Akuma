import sqlite3

from scripts.seed_demo import seed


def test_demo_seed_is_deterministic_and_idempotent(tmp_path):
    database_path = tmp_path / "demo.db"
    with sqlite3.connect(database_path) as database:
        first = seed(database)
        second = seed(database)
        counts = database.execute("SELECT COUNT(*) FROM price_reports WHERE is_demo = 1").fetchone()[0]
        mandis = database.execute("SELECT COUNT(*) FROM mandis WHERE is_demo = 1").fetchone()[0]
    assert first == second
    assert first["crops"] == 8
    assert first["mandis"] == 25
    assert counts == first["prices"]
    assert mandis == 25
