from __future__ import annotations


class EasyConfigError(Exception):
    code: str = "easy_config_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


class SkillNotFoundError(EasyConfigError):
    code = "skill_not_found"


class SchemaNotFoundError(EasyConfigError):
    code = "schema_not_found"


class ValidationError(EasyConfigError):
    code = "validation_error"


class WriteForbiddenError(EasyConfigError):
    code = "write_forbidden"


class InvalidTokenError(EasyConfigError):
    code = "invalid_token"


class SessionExpiredError(EasyConfigError):
    code = "session_expired"


class SessionClosedError(EasyConfigError):
    code = "session_closed"
