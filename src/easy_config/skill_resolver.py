from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from easy_config.errors import SkillNotFoundError, WriteForbiddenError
from easy_config.paths import easy_config_repo_root, ensure_under, skills_root


@dataclass(frozen=True)
class SkillTarget:
    name: str
    root: Path
    schema_path: Path
    schema: dict
    write_target: Path
    config_format: str
    reload_hint: str
    secrets: tuple[str, ...]


_SKILL_NAME = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")


def resolve_skill(skill_name: str) -> Path:
    if not _SKILL_NAME.match(skill_name):
        raise SkillNotFoundError(f"invalid skill name: {skill_name!r}")
    root = skills_root()
    candidate = (root / skill_name).resolve()
    ensure_under(root, candidate)
    if not candidate.is_dir():
        raise SkillNotFoundError(f"skill not found: {skill_name} (looked in {root})")
    return candidate


def resolve_write_target(skill_root: Path, write_target_rel: str) -> Path:
    if write_target_rel.startswith("/") or ".." in Path(write_target_rel).parts:
        raise WriteForbiddenError(f"invalid writeTarget: {write_target_rel}")
    target = (skill_root / write_target_rel).resolve()
    ensure_under(skill_root, target)
    return target
