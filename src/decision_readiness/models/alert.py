from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

SEVERITY_RANKS = {"Unknown": 0, "Minor": 1, "Moderate": 2, "Severe": 3, "Extreme": 4}


def parse_nws_timestamp(value: Any, field_name: str) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string or null")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{field_name} is not a valid ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include a timezone")
    return parsed


def normalize_same_code(value: str) -> str:
    """Convert six-digit SAME county codes (037183) to five-digit FIPS (37183)."""
    if len(value) == 6 and value.startswith("0") and value.isdigit():
        return value[1:]
    if len(value) == 5 and value.isdigit():
        return value
    raise ValueError(f"Unsupported SAME county code: {value!r}")


@dataclass(frozen=True)
class AlertCountyRecord:
    alert_id: str
    county_fips: str
    event: str
    severity: str
    severity_rank: int
    certainty: str
    urgency: str
    area_description: str
    effective_at: datetime | None
    expires_at: datetime | None
    retrieved_at: datetime
    source_url: str

    def as_row(self) -> dict[str, Any]:
        return asdict(self)
