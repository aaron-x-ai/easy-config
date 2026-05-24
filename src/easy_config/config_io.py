from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from easy_config.errors import ValidationError


def read_config(path: Path, fmt: str) -> dict[str, Any]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    if fmt == "yaml":
        data = yaml.safe_load(text) or {}
    elif fmt == "json":
        data = json.loads(text or "{}")
    elif fmt == "env":
        data = _parse_env(text)
    else:
        raise ValidationError(f"unsupported format: {fmt}")
    if not isinstance(data, dict):
        raise ValidationError(f"config root must be an object, got {type(data).__name__}")
    return data


def write_config(path: Path, data: dict[str, Any], fmt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    if fmt == "yaml":
        content = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    elif fmt == "json":
        content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    elif fmt == "env":
        content = _serialize_env(data)
    else:
        raise ValidationError(f"unsupported format: {fmt}")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def backup_config(path: Path) -> Path | None:
    if not path.is_file():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(f"{path.name}.bak_{stamp}")
    backup.write_bytes(path.read_bytes())
    return backup


def _parse_env(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip()
    return out


def _serialize_env(data: dict[str, Any]) -> str:
    lines = [f"{k}={v}" for k, v in data.items()]
    return "\n".join(lines) + "\n"
