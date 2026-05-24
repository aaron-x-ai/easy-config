from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator

from easy_config.errors import ValidationError


def validate_payload(schema: dict[str, Any], payload: dict[str, Any]) -> None:
    field_schema = {k: v for k, v in schema.items() if k != "x-easy-config"}
    validator = Draft202012Validator(field_schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
    if errors:
        first = errors[0]
        path = ".".join(str(p) for p in first.path) or "(root)"
        raise ValidationError(f"{path}: {first.message}")
