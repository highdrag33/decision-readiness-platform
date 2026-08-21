import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path

from decision_readiness.config import load_settings
from decision_readiness.models.facility import Facility
from decision_readiness.storage.duckdb_store import (
    build_decision_database,
    export_facility_risk,
)
from decision_readiness.transforms.nws_alerts import normalize_alerts


def find_latest_raw_alerts(raw_data_dir: Path) -> Path:
    candidates = sorted((raw_data_dir / "nws_alerts").glob("alerts_*.json"))
    if not candidates:
        raise FileNotFoundError("No raw NWS alert files found. Run ingest-nws-alerts first.")
    return candidates[-1]


def retrieved_at_from_path(path: Path) -> datetime:
    try:
        timestamp = path.stem.removeprefix("alerts_")
        return datetime.strptime(timestamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except ValueError as error:
        raise ValueError(f"Raw alert filename has an invalid timestamp: {path.name}") from error


def load_facilities(path: Path) -> list[Facility]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {
            "facility_id",
            "name",
            "county_fips",
            "resource_type",
            "on_hand_units",
            "daily_demand_units",
            "safety_stock_days",
        }
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Facility file is missing columns: {sorted(missing)}")
        return [
            Facility(
                facility_id=row["facility_id"],
                name=row["name"],
                county_fips=row["county_fips"],
                resource_type=row["resource_type"],
                on_hand_units=int(row["on_hand_units"]),
                daily_demand_units=int(row["daily_demand_units"]),
                safety_stock_days=float(row["safety_stock_days"]),
            )
            for row in reader
        ]


def build_mvp(
    raw_alerts_path: Path,
    facilities_path: Path,
    database_path: Path,
    risk_output_path: Path,
) -> tuple[int, int]:
    with raw_alerts_path.open(encoding="utf-8") as file:
        payload = json.load(file)
    retrieved_at = retrieved_at_from_path(raw_alerts_path)
    alerts = normalize_alerts(payload, retrieved_at)
    facilities = load_facilities(facilities_path)
    build_decision_database(database_path, alerts, facilities, retrieved_at)
    export_facility_risk(database_path, risk_output_path)
    return len(alerts), len(facilities)


def main() -> None:
    settings = load_settings()
    parser = argparse.ArgumentParser(description="Build the decision-readiness MVP")
    parser.add_argument("--raw-alerts", type=Path, default=None)
    parser.add_argument("--facilities", type=Path, default=settings.facilities_path)
    parser.add_argument(
        "--database",
        type=Path,
        default=settings.curated_data_dir / "decision_readiness.duckdb",
    )
    parser.add_argument(
        "--risk-output",
        type=Path,
        default=settings.curated_data_dir / "facility_risk.csv",
    )
    args = parser.parse_args()
    raw_alerts_path = args.raw_alerts or find_latest_raw_alerts(settings.raw_data_dir)
    alert_count, facility_count = build_mvp(
        raw_alerts_path=raw_alerts_path,
        facilities_path=args.facilities,
        database_path=args.database,
        risk_output_path=args.risk_output,
    )
    print(f"Normalized {alert_count} alert-county records")
    print(f"Loaded {facility_count} synthetic facilities")
    print(f"DuckDB database written to {args.database}")
    print(f"Facility risk report written to {args.risk_output}")


if __name__ == "__main__":
    main()
