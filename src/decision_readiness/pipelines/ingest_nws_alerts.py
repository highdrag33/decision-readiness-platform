import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from decision_readiness.clients.nws import NWSClient
from decision_readiness.config import load_settings


def build_output_path(
    raw_data_dir: Path,
    retrieved_at: datetime,
) -> Path:
    timestamp = retrieved_at.strftime("%Y%m%dT%H%M%SZ")
    return raw_data_dir / "nws_alerts" / f"alerts_{timestamp}.json"


def write_raw_response(
    payload: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = output_path.with_suffix(".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    temporary_path.replace(output_path)


def main() -> None:
    settings = load_settings()
    retrieved_at = datetime.now(UTC)

    with NWSClient(settings.nws_user_agent) as client:
        payload = client.get_active_alerts(settings.nws_area)

    output_path = build_output_path(
        settings.raw_data_dir,
        retrieved_at,
    )
    write_raw_response(payload, output_path)

    alert_count = len(payload.get("features", []))

    print(f"Retrieved {alert_count} alerts")
    print(f"Raw response written to {output_path}")


if __name__ == "__main__":
    main()
