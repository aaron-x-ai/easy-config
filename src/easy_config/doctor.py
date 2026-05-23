from __future__ import annotations

import importlib.util
import platform
import sys
from pathlib import Path
from typing import List, Optional


def run_doctor(*, skill_dir: Optional[Path], repo_root: Path) -> List[str]:
    issues: List[str] = []

    if sys.version_info < (3, 10):
        issues.append(f"Python >= 3.10 required; found {sys.version.split()[0]}")

    if importlib.util.find_spec("fastapi") is None:
        issues.append("fastapi not installed; run: bash scripts/install.sh")

    if importlib.util.find_spec("uvicorn") is None:
        issues.append("uvicorn not installed; run: bash scripts/install.sh")

    static_index = repo_root / "src" / "easy_config" / "static" / "index.html"
    if not static_index.is_file():
        issues.append(f"missing static SPA placeholder: {static_index}")

    skills_root = Path(_env_skills_root() or (Path.home() / ".hermes" / "skills"))
    if not skills_root.is_dir():
        issues.append(
            f"skills root not found: {skills_root} "
            "(create or set EASY_CONFIG_SKILLS_ROOT)"
        )

    if skill_dir is not None:
        if not (skill_dir / "SKILL.md").is_file():
            issues.append(f"SKILL.md not found in {skill_dir}")

    if platform.system() not in {"Darwin", "Linux"}:
        issues.append(f"unsupported platform for v1: {platform.system()}")

    return issues


def _env_skills_root() -> Optional[str]:
    import os

    value = os.environ.get("EASY_CONFIG_SKILLS_ROOT", "").strip()
    return value or None
