from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Facility:
    facility_id: str
    name: str
    county_fips: str
    resource_type: str
    on_hand_units: int
    daily_demand_units: int
    safety_stock_days: float

    def __post_init__(self) -> None:
        if len(self.county_fips) != 5 or not self.county_fips.isdigit():
            raise ValueError(f"county_fips must be five digits: {self.county_fips!r}")
        if self.on_hand_units < 0:
            raise ValueError("on_hand_units cannot be negative")
        if self.daily_demand_units <= 0:
            raise ValueError("daily_demand_units must be positive")
        if self.safety_stock_days < 0:
            raise ValueError("safety_stock_days cannot be negative")

    def as_row(self) -> dict[str, Any]:
        return asdict(self)
