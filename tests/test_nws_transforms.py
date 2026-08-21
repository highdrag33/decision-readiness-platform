import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from decision_readiness.transforms.nws_alerts import normalize_alerts

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "nws_alerts.json"


def test_normalize_alerts_creates_county_record() -> None:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    retrieved_at = datetime(2026, 8, 9, 16, 30, tzinfo=UTC)

    records = normalize_alerts(payload, retrieved_at)

    assert len(records) == 1
    assert records[0].county_fips == "37183"
    assert records[0].event == "Flood Warning"
    assert records[0].severity_rank == 3
    assert records[0].retrieved_at == retrieved_at


def test_normalize_alerts_rejects_missing_features() -> None:
    with pytest.raises(TypeError, match="features list"):
        normalize_alerts({}, datetime(2026, 8, 9, tzinfo=UTC))
