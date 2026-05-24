from __future__ import annotations

from copy import deepcopy
from typing import Any


def mask_form_data(data: dict[str, Any], secrets: tuple[str, ...]) -> dict[str, Any]:
    masked = deepcopy(data)
    for key in secrets:
        if key in masked and masked[key] not in (None, ""):
            masked[key] = {"set": True}
    return masked


def merge_submit_with_secrets(
    original: dict[str, Any],
    submitted: dict[str, Any],
    secrets: tuple[str, ...],
) -> dict[str, Any]:
    merged = deepcopy(original)
    merged.update(submitted)
    for key in secrets:
        if key not in submitted:
            continue
        value = submitted[key]
        if value is None or value == "" or value == {"set": True}:
            if key in original:
                merged[key] = original[key]
            elif key in merged:
                del merged[key]
    return merged
