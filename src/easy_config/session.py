from __future__ import annotations

import json
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from easy_config.config_io import read_config
from easy_config.settings import idle_timeout_seconds
from easy_config.paths import cache_root
from easy_config.schema_pipeline import parse_skill_target
from easy_config.skill_resolver import SkillTarget


@dataclass
class SessionContext:
    session_id: str
    session_dir: Path
    token: str
    target: SkillTarget
    config_data: dict[str, Any]
    idle_seconds: int
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    submitted: bool = False

    @property
    def config_path(self) -> Path:
        return self.target.write_target

    @property
    def expires_at(self) -> datetime:
        return self.last_activity + timedelta(seconds=self.idle_seconds)


def create_session(skill_name: str, *, idle_seconds: int | None = None) -> SessionContext:
    target = parse_skill_target(skill_name)
    config_data = read_config(target.write_target, target.config_format)
    idle = idle_seconds if idle_seconds is not None else idle_timeout_seconds()

    session_id = uuid.uuid4().hex
    token = secrets.token_urlsafe(32)
    session_dir = cache_root() / "sessions" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "token").write_text(token, encoding="utf-8")
    session_dir.chmod(0o700)
    (session_dir / "token").chmod(0o600)

    now = datetime.now(timezone.utc)
    meta = {
        "session_id": session_id,
        "skill": skill_name,
        "config_path": str(target.write_target),
        "idle_seconds": idle,
        "expires_at": (now + timedelta(seconds=idle)).isoformat(),
    }
    (session_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return SessionContext(
        session_id=session_id,
        session_dir=session_dir,
        token=token,
        target=target,
        config_data=config_data,
        idle_seconds=idle,
        last_activity=now,
    )


def write_result(session: SessionContext, *, backup_path: Path | None) -> Path:
    payload = {
        "status": "saved",
        "skill": session.target.name,
        "write_target": str(session.target.write_target.relative_to(session.target.root)),
        "backup_path": str(backup_path.relative_to(session.target.root)) if backup_path else None,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "reload_hint": session.target.reload_hint,
    }
    result_path = session.session_dir / "easy_config_result.json"
    result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return result_path
