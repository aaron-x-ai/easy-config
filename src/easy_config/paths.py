from __future__ import annotations

import os
from pathlib import Path


def skills_root() -> Path:
    raw = os.environ.get("EASY_CONFIG_SKILLS_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (Path.home() / ".hermes" / "skills").resolve()


def easy_config_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def cache_root() -> Path:
    return (Path.home() / ".cache" / "easy-config").resolve()


def ensure_under(root: Path, target: Path) -> Path:
    root_resolved = root.resolve()
    target_resolved = target.resolve()
    if not str(target_resolved).startswith(str(root_resolved) + os.sep) and target_resolved != root_resolved:
        raise ValueError(f"path escapes root: {target}")
    return target_resolved
