from typing import Any, Self

import httpx


class NWSClient:
    BASE_URL = "https://api.weather.gov"

    def __init__(
        self,
        user_agent: str,
        timeout_seconds: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "User-Agent": user_agent,
                "Accept": "application/geo+json",
            },
            timeout=timeout_seconds,
            transport=transport,
        )

    def get_active_alerts(self, area: str) -> dict[str, Any]:
        response = self._client.get(
            "/alerts/active",
            params={"area": area},
        )
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
