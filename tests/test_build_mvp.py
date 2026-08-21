import csv
from pathlib import Path

import duckdb

from decision_readiness.pipelines.build_mvp import build_mvp

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "nws_alerts.json"
FACILITIES_PATH = Path(__file__).parents[1] / "data" / "sample" / "facilities.csv"


def test_build_mvp_creates_queryable_risk_output(tmp_path: Path) -> None:
    raw_path = tmp_path / "alerts_20260809T163000Z.json"
    raw_path.write_text(FIXTURE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    database_path = tmp_path / "decision_readiness.duckdb"
    risk_path = tmp_path / "facility_risk.csv"

    alert_count, facility_count = build_mvp(
        raw_alerts_path=raw_path,
        facilities_path=FACILITIES_PATH,
        database_path=database_path,
        risk_output_path=risk_path,
    )

    assert alert_count == 1
    assert facility_count == 5
    assert database_path.exists()
    assert risk_path.exists()

    with duckdb.connect(str(database_path), read_only=True) as connection:
        raleigh = connection.execute(
            "SELECT active_alert_count, highest_severity, risk_band "
            "FROM facility_risk WHERE facility_id = 'FAC-001'"
        ).fetchone()

    assert raleigh == (1, "Severe", "MEDIUM")
    with risk_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 5
