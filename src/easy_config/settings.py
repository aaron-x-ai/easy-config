from __future__ import annotations

import os


def idle_timeout_seconds() -> int:
    return int(os.environ.get("EASY_CONFIG_IDLE_TIMEOUT_SEC", "900"))


def shutdown_delay_seconds() -> int:
    return int(os.environ.get("EASY_CONFIG_SHUTDOWN_DELAY_SEC", "10"))
