from __future__ import annotations

import json
from pathlib import Path

from easy_config.errors import SchemaNotFoundError
from easy_config.paths import easy_config_repo_root
from easy_config.skill_resolver import SkillTarget, resolve_skill, resolve_write_target


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_candidates(skill_root: Path, skill_name: str) -> list[Path]:
    repo = easy_config_repo_root()
    return [
        skill_root / "easy-config-schema.json",
        skill_root / "config" / "easy-config-schema.json",
        repo / "registry" / f"{skill_name}.easy-config-schema.json",
    ]


def find_schema_file(skill_root: Path, skill_name: str) -> Path | None:
    for path in _schema_candidates(skill_root, skill_name):
        if path.is_file():
            return path
    return None


def parse_skill_target(skill_name: str) -> SkillTarget:
    skill_root = resolve_skill(skill_name)
    schema_path = find_schema_file(skill_root, skill_name)
    if schema_path is None:
        raise SchemaNotFoundError(
            f"no easy-config-schema.json for skill {skill_name!r}; "
            "see references/skill-author-guide.md"
        )

    schema = _load_json(schema_path)
    ext = schema.get("x-easy-config")
    if not isinstance(ext, dict):
        raise SchemaNotFoundError("missing x-easy-config block in schema")

    write_rel = ext.get("writeTarget")
    config_format = ext.get("format")
    if not write_rel or not config_format:
        raise SchemaNotFoundError("x-easy-config requires writeTarget and format")

    write_target = resolve_write_target(skill_root, str(write_rel))
    secrets_raw = ext.get("secrets") or []
    secrets = tuple(str(s) for s in secrets_raw) if isinstance(secrets_raw, list) else ()

    return SkillTarget(
        name=skill_name,
        root=skill_root,
        schema_path=schema_path,
        schema=schema,
        write_target=write_target,
        config_format=str(config_format),
        reload_hint=str(
            ext.get("reloadHint") or f"请回到聊天窗口，发送：重新加载 {skill_name}"
        ),
        secrets=secrets,
    )
