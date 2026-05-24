from __future__ import annotations

from easy_config.errors import InvalidTokenError, SessionClosedError, SessionExpiredError
from easy_config.lifecycle import session_is_expired, touch_session
from easy_config.session import SessionContext


def authorize_session(session: SessionContext | None, token: str | None) -> SessionContext:
    if session is None:
        raise InvalidTokenError("no active session")
    if not token or token != session.token:
        raise InvalidTokenError("invalid or missing token")
    if session.submitted:
        raise SessionClosedError("session already saved")
    if session_is_expired(session):
        raise SessionExpiredError("session expired due to inactivity")
    touch_session(session)
    return session
