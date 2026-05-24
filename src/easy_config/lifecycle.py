from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone

from easy_config.session import SessionContext
from easy_config.settings import shutdown_delay_seconds


def session_is_expired(session: SessionContext) -> bool:
    deadline = session.last_activity + timedelta(seconds=session.idle_seconds)
    return datetime.now(timezone.utc) > deadline


def touch_session(session: SessionContext) -> None:
    session.last_activity = datetime.now(timezone.utc)


class IdleWatcher:
    """Background thread: exit process when session idle timeout exceeded."""

    def __init__(self, session: SessionContext, *, poll_seconds: int = 15) -> None:
        self._session = session
        self._poll_seconds = poll_seconds
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="easy-config-idle", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        while not self._stop.wait(self._poll_seconds):
            if self._session.submitted:
                return
            if session_is_expired(self._session):
                _shutdown_process()
                return


def schedule_shutdown(delay_seconds: int | None = None) -> None:
    delay = shutdown_delay_seconds() if delay_seconds is None else delay_seconds
    threading.Timer(delay, _shutdown_process).start()


def _shutdown_process() -> None:
    import os
    import signal

    os.kill(os.getpid(), signal.SIGINT)
