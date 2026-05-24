from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from easy_config.config_io import read_config


def test_session_masks_secrets(client: TestClient) -> None:
    res = client.get("/api/session", headers={"X-Easy-Config-Token": client.app.state.session.token})
    assert res.status_code == 200
    body = res.json()
    assert body["skill"] == "demo-skill"
    assert body["formData"]["api_key"] == {"set": True}
    assert body["formData"]["max_results"] == 5


def test_save_config_creates_backup(client: TestClient, demo_skill_dir: Path) -> None:
    token = client.app.state.session.token
    res = client.post(
        "/api/config",
        headers={"X-Easy-Config-Token": token},
        json={"max_results": 20, "enabled": False},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "saved"
    assert data["backup_path"] is not None

    cfg_path = demo_skill_dir / "config" / "config.yaml"
    saved = read_config(cfg_path, "yaml")
    assert saved["max_results"] == 20
    assert saved["enabled"] is False
    assert saved["api_key"] == "sk-demo-original"

    backups = list((demo_skill_dir / "config").glob("config.yaml.bak_*"))
    assert backups

    result = client.app.state.session.session_dir / "easy_config_result.json"
    assert result.is_file()
    payload = json.loads(result.read_text())
    assert payload["status"] == "saved"


def test_invalid_token(client: TestClient) -> None:
    res = client.get("/api/session", headers={"X-Easy-Config-Token": "bad"})
    assert res.status_code == 403
