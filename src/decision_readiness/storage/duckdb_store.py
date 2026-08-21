from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import duckdb

from decision_readiness.models.alert import AlertCountyRecord
from decision_readiness.models.facility import Facility


def build_decision_database(
    database_path: Path,
    alerts: Sequence[AlertCountyRecord],
    facilities: Sequence[Facility],
    as_of: datetime,
) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database_path)) as connection:
        connection.execute("DROP TABLE IF EXISTS alerts")
        connection.execute("DROP TABLE IF EXISTS facilities")
        connection.execute("DROP TABLE IF EXISTS pipeline_run")
        connection.execute(
            """CREATE TABLE alerts (
                alert_id VARCHAR, county_fips VARCHAR, event VARCHAR, severity VARCHAR,
                severity_rank INTEGER, certainty VARCHAR, urgency VARCHAR,
                area_description VARCHAR, effective_at TIMESTAMPTZ, expires_at TIMESTAMPTZ,
                retrieved_at TIMESTAMPTZ, source_url VARCHAR
            )"""
        )
        connection.execute("CREATE TABLE pipeline_run (as_of TIMESTAMPTZ)")
        connection.execute("INSERT INTO pipeline_run VALUES (?)", [as_of])
        connection.execute(
            """CREATE TABLE facilities (
                facility_id VARCHAR PRIMARY KEY, name VARCHAR, county_fips VARCHAR,
                resource_type VARCHAR, on_hand_units INTEGER, daily_demand_units INTEGER,
                safety_stock_days DOUBLE
            )"""
        )
        if alerts:
            connection.executemany(
                "INSERT INTO alerts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [tuple(alert.as_row().values()) for alert in alerts],
            )
        if facilities:
            connection.executemany(
                "INSERT INTO facilities VALUES (?, ?, ?, ?, ?, ?, ?)",
                [tuple(facility.as_row().values()) for facility in facilities],
            )
        connection.execute(
            """
            CREATE OR REPLACE VIEW facility_risk AS
            WITH county_weather AS (
                SELECT county_fips, COUNT(DISTINCT alert_id) AS active_alert_count,
                       MAX(severity_rank) AS highest_severity_rank,
                       ARG_MAX(severity, severity_rank) AS highest_severity,
                       STRING_AGG(DISTINCT event, '; ' ORDER BY event) AS active_events
                FROM alerts
                WHERE (effective_at IS NULL OR effective_at <= (SELECT as_of FROM pipeline_run))
                  AND (expires_at IS NULL OR expires_at >= (SELECT as_of FROM pipeline_run))
                GROUP BY county_fips
            ), metrics AS (
                SELECT f.*,
                       ROUND(f.on_hand_units::DOUBLE / f.daily_demand_units, 2) AS days_of_supply,
                       COALESCE(w.active_alert_count, 0) AS active_alert_count,
                       COALESCE(w.highest_severity_rank, 0) AS highest_severity_rank,
                       COALESCE(w.highest_severity, 'None') AS highest_severity,
                       COALESCE(w.active_events, 'None') AS active_events
                FROM facilities f LEFT JOIN county_weather w USING (county_fips)
            ), scored AS (
                SELECT *,
                    LEAST(60.0, GREATEST(0.0,
                        (safety_stock_days - days_of_supply) /
                        NULLIF(safety_stock_days, 0) * 60
                    )) + highest_severity_rank / 4.0 * 40 AS raw_risk_score
                FROM metrics
            )
            SELECT * EXCLUDE (raw_risk_score),
                   CASE WHEN days_of_supply < safety_stock_days THEN 'CRITICAL'
                        WHEN days_of_supply < safety_stock_days + 2 THEN 'WATCH'
                        ELSE 'STABLE' END AS supply_status,
                   ROUND(raw_risk_score, 1) AS risk_score,
                   CASE WHEN raw_risk_score >= 60 THEN 'HIGH'
                        WHEN raw_risk_score >= 30 THEN 'MEDIUM'
                        ELSE 'LOW' END AS risk_band
            FROM scored
            """,
        )


def export_facility_risk(database_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database_path), read_only=True) as connection:
        connection.execute(
            "COPY (SELECT * FROM facility_risk ORDER BY risk_score DESC, facility_id) "
            "TO ? (HEADER, DELIMITER ',')",
            [str(output_path)],
        )
