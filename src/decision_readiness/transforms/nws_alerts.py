from datetime import datetime
from typing import Any

from decision_readiness.models.alert import (
    SEVERITY_RANKS,
    AlertCountyRecord,
    normalize_same_code,
    parse_nws_timestamp,
)


def require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def normalize_alerts(payload: dict[str, Any], retrieved_at: datetime) -> list[AlertCountyRecord]:
    if retrieved_at.tzinfo is None:
        raise ValueError("retrieved_at must include a timezone")
    features = payload.get("features")
    if not isinstance(features, list):
        raise TypeError("NWS payload must contain a features list")

    records: list[AlertCountyRecord] = []
    for feature_index, feature in enumerate(features):
        if not isinstance(feature, dict):
            raise TypeError(f"features[{feature_index}] must be an object")
        properties = feature.get("properties")
        if not isinstance(properties, dict):
            raise TypeError(f"features[{feature_index}].properties must be an object")

        alert_id = require_text(feature.get("id") or properties.get("id"), "alert id")
        event = require_text(properties.get("event"), "event")
        severity = require_text(properties.get("severity", "Unknown"), "severity")
        certainty = require_text(properties.get("certainty", "Unknown"), "certainty")
        urgency = require_text(properties.get("urgency", "Unknown"), "urgency")
        area_description = require_text(properties.get("areaDesc"), "areaDesc")
        geocode = properties.get("geocode") or {}
        same_codes = geocode.get("SAME") or [] if isinstance(geocode, dict) else []
        if not isinstance(same_codes, list):
            raise TypeError(f"SAME codes for {alert_id} must be a list")

        for same_code in same_codes:
            if not isinstance(same_code, str):
                raise TypeError(f"SAME codes for {alert_id} must be strings")
            records.append(
                AlertCountyRecord(
                    alert_id=alert_id,
                    county_fips=normalize_same_code(same_code),
                    event=event,
                    severity=severity,
                    severity_rank=SEVERITY_RANKS.get(severity, 0),
                    certainty=certainty,
                    urgency=urgency,
                    area_description=area_description,
                    effective_at=parse_nws_timestamp(properties.get("effective"), "effective"),
                    expires_at=parse_nws_timestamp(properties.get("expires"), "expires"),
                    retrieved_at=retrieved_at,
                    source_url=alert_id,
                )
            )
    return records
