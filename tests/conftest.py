import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from easy_config.server.app import create_app
from easy_config.session import create_session

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def skills_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "skills"
    root.mkdir()
    shutil.copytree(FIXTURES / "demo-skill", root / "demo-skill")
    monkeypatch.setenv("EASY_CONFIG_SKILLS_ROOT", str(root))
    return root


@pytest.fixture
def demo_skill_dir(skills_root: Path) -> Path:
    return skills_root / "demo-skill"


@pytest.fixture
def session(demo_skill_dir: Path):
    return create_session("demo-skill")


@pytest.fixture
def client(session) -> TestClient:
    return TestClient(create_app(session=session))
