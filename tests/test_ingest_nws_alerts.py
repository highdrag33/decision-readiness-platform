import json
from datetime import UTC, datetime
from pathlib import Path

from decision_readiness.pipelines.ingest_nws_alerts import build_output_path, write_raw_response


def test_build_output_path_uses_utc_timestamp() -> None:
    # Arrange
    raw_data_dir = Path("data/raw")
    retrieved_at = datetime(
        2026,
        8,
        9,
        14,
        30,
        45,
        tzinfo=UTC,
    )
    expected_path = raw_data_dir / "nws_alerts" / "alerts_20260809T143045Z.json"

    # Act
    actual_path = build_output_path(
        raw_data_dir,
        retrieved_at,
    )

    # Assert
    assert actual_path == expected_path


def test_write_raw_response_creates_json_file(tmp_path: Path) -> None:
    # Arrange
    payload = {
        "type": "FeatureCollection",
        "features": [],
    }

    output_path = tmp_path / "raw" / "nws_alerts" / "alerts.json"
    temporary_path = output_path.with_suffix(".tmp")

    # Act
    write_raw_response(payload, output_path)

    # Assert
    assert output_path.exists()
    assert not temporary_path.exists()

    with output_path.open(encoding="utf-8") as file:
        actual_payload = json.load(file)

    assert actual_payload == payload
