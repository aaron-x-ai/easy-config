from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from easy_config.lifecycle import session_is_expired
from easy_config.server.app import create_app
from easy_config.session import create_session


def test_session_expired(skills_root) -> None:
    session = create_session("demo-skill", idle_seconds=60)
    session.last_activity = datetime.now(timezone.utc) - timedelta(seconds=120)
    assert session_is_expired(session) is True


def test_expired_session_rejected(skills_root) -> None:
    session = create_session("demo-skill", idle_seconds=60)
    session.last_activity = datetime.now(timezone.utc) - timedelta(seconds=120)
    client = TestClient(create_app(session=session))
    res = client.get("/api/session", headers={"X-Easy-Config-Token": session.token})
    assert res.status_code == 403
    assert res.json()["detail"]["error"] == "session_expired"


def test_closed_after_submit(client: TestClient) -> None:
    token = client.app.state.session.token
    client.post(
        "/api/config",
        headers={"X-Easy-Config-Token": token},
        json={"max_results": 12},
    )
    res = client.get("/api/session", headers={"X-Easy-Config-Token": token})
    assert res.status_code == 409
    assert res.json()["detail"]["error"] == "session_closed"
