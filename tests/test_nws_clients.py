import json
from pathlib import Path

import httpx
import pytest

from decision_readiness.clients.nws import NWSClient

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "nws_alerts.json"


def load_alert_fixture() -> dict:
    with FIXTURE_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def test_get_active_alerts_builds_request_and_returns_json() -> None:

    expected_payload = load_alert_fixture()

    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/alerts/active"
        assert request.url.params["area"] == "NC"
        assert request.headers["user-agent"] == "decision-readiness-platform test@example.com"
        assert request.headers["accept"] == "application/geo+json"

        return httpx.Response(200, json=expected_payload)

    transport = httpx.MockTransport(handle_request)

    with NWSClient(
        user_agent="decision-readiness-platform test@example.com",
        transport=transport,
    ) as client:
        actual_payload = client.get_active_alerts("NC")

    assert actual_payload == expected_payload
    assert len(actual_payload["features"]) == 1


def test_get_active_alerts_raises_for_unsuccessful_response() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503,
            json={"detail": "Service temporarily unavailable"},
        )

    transport = httpx.MockTransport(handle_request)

    with (
        NWSClient(
            user_agent="decision-readiness-platform test@example.com",
            transport=transport,
        ) as client,
        pytest.raises(httpx.HTTPStatusError) as error,
    ):
        client.get_active_alerts("NC")

    assert error.value.response.status_code == 503
