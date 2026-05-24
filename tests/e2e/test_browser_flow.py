from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.mark.e2e
def test_browser_save_config(skills_root: Path, demo_skill_dir: Path) -> None:
    playwright = pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright

    port = _free_port()
    env = os.environ.copy()
    env["EASY_CONFIG_SKILLS_ROOT"] = str(skills_root)
    env["EASY_CONFIG_SHUTDOWN_DELAY_SEC"] = "3"
    env["EASY_CONFIG_IDLE_TIMEOUT_SEC"] = "600"

    py = sys.executable
    proc = subprocess.Popen(
        [py, "-m", "easy_config", "serve", "--skill", "demo-skill", "--port", str(port)],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    url = ""
    try:
        assert proc.stdout is not None
        line = proc.stdout.readline()
        payload = json.loads(line)
        assert payload["status"] == "ready"
        url = payload["url"]

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as exc:  # noqa: BLE001
                pytest.skip(f"Playwright browser unavailable: {exc}")
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            page.fill("#max_results", "18")
            page.click('button[type="submit"]')
            page.wait_for_selector("#success", state="visible", timeout=10000)
            assert "配置已保存" in page.inner_text("#success")
            browser.close()

        time.sleep(0.5)
        cfg = (demo_skill_dir / "config" / "config.yaml").read_text(encoding="utf-8")
        assert "max_results: 18" in cfg
        assert list((demo_skill_dir / "config").glob("config.yaml.bak_*"))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
