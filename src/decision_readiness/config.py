import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    nws_user_agent: str
    nws_area: str
    raw_data_dir: Path
    curated_data_dir: Path
    facilities_path: Path


def load_settings() -> Settings:
    user_agent = os.getenv("NWS_USER_AGENT")

    if not user_agent:
        raise ValueError(
            "NWS_USER_AGENT is required. Set it to an application name and contact address."
        )

    return Settings(
        nws_user_agent=user_agent,
        nws_area=os.getenv("NWS_AREA", "NC"),
        raw_data_dir=Path(os.getenv("RAW_DATA_DIR", "data/raw")),
        curated_data_dir=Path(os.getenv("CURATED_DATA_DIR", "data/curated")),
        facilities_path=Path(os.getenv("FACILITIES_PATH", "data/sample/facilities.csv")),
    )
