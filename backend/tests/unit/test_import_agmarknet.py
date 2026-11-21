import sqlite3

import pytest

from scripts.import_agmarknet import import_csv
from scripts.seed_demo import seed


def test_import_rejects_changed_structure(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("crop_id,mandi_id\nonion,pune\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        import_csv(csv_path, tmp_path / "db.sqlite")


def test_import_preserves_demo_and_marks_real_data(tmp_path):
    database_path = tmp_path / "demo.db"
    with sqlite3.connect(database_path) as database:
        seed(database)
    csv_path = tmp_path / "real.csv"
    csv_path.write_text("crop_id,mandi_id,reported_on,modal_price_inr\nonion,pune,2026-11-21,2500\n", encoding="utf-8")
    assert import_csv(csv_path, database_path) == 1
    with sqlite3.connect(database_path) as database:
        row = database.execute("SELECT record_type, is_demo FROM price_reports WHERE id = 'AGMARKNET-2'").fetchone()
    assert row == ("AGMARKNET", 0)
