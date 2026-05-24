from __future__ import annotations

import json
import os
import subprocess
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from easy_config import __version__
from easy_config.config_io import backup_config, write_config
from easy_config.errors import (
    EasyConfigError,
    InvalidTokenError,
    SessionClosedError,
    SessionExpiredError,
    ValidationError,
)
from easy_config.lifecycle import IdleWatcher, schedule_shutdown
from easy_config.paths import easy_config_repo_root
from easy_config.secrets import mask_form_data, merge_submit_with_secrets
from easy_config.security import authorize_session
from easy_config.session import SessionContext, write_result
from easy_config.validators import validate_payload


def _static_dir():
    from pathlib import Path

    return Path(__file__).resolve().parents[1] / "static"


def _http_error(exc: EasyConfigError, status: int) -> HTTPException:
    return HTTPException(status_code=status, detail={"error": exc.code, "message": str(exc)})


def _field_schema(schema: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in schema.items() if not k.startswith("x-")}


def create_app(
    *,
    session: SessionContext | None = None,
    dev: bool = False,
    enable_lifecycle: bool = False,
) -> FastAPI:
    app = FastAPI(
        title="Easy Config",
        version=__version__,
        docs_url="/docs" if dev else None,
        redoc_url=None,
    )
    app.state.session = session
    app.state.idle_watcher = None
    if session and enable_lifecycle:
        watcher = IdleWatcher(session)
        watcher.start()
        app.state.idle_watcher = watcher

    static_dir = _static_dir()

    def _auth(token: str | None) -> SessionContext:
        try:
            return authorize_session(app.state.session, token)
        except InvalidTokenError as exc:
            raise _http_error(exc, 403) from exc
        except SessionExpiredError as exc:
            raise _http_error(exc, 403) from exc
        except SessionClosedError as exc:
            raise _http_error(exc, 409) from exc

    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    @app.get("/config")
    def config_page() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/api/session")
    def get_session(
        x_easy_config_token: str | None = Header(default=None, alias="X-Easy-Config-Token"),
    ) -> JSONResponse:
        ctx = _auth(x_easy_config_token)
        schema = ctx.target.schema
        form_data = mask_form_data(ctx.config_data, ctx.target.secrets)
        return JSONResponse(
            {
                "skill": ctx.target.name,
                "writeTarget": str(ctx.target.write_target.relative_to(ctx.target.root)),
                "format": ctx.target.config_format,
                "schema": _field_schema(schema),
                "uiSchema": schema.get("x-easy-config", {}).get("ui", {}),
                "formData": form_data,
                "reloadHint": ctx.target.reload_hint,
            }
        )

    @app.post("/api/config")
    def post_config(
        body: dict[str, Any],
        x_easy_config_token: str | None = Header(default=None, alias="X-Easy-Config-Token"),
    ) -> JSONResponse:
        ctx = _auth(x_easy_config_token)
        try:
            merged = merge_submit_with_secrets(ctx.config_data, body, ctx.target.secrets)
            validate_payload(ctx.target.schema, merged)
            backup = backup_config(ctx.target.write_target)
            write_config(ctx.target.write_target, merged, ctx.target.config_format)
            ctx.config_data = merged
            ctx.submitted = True
            write_result(ctx, backup_path=backup)
            _maybe_reload(ctx)
            if app.state.idle_watcher:
                app.state.idle_watcher.stop()
            if enable_lifecycle:
                schedule_shutdown()
            rel_backup = str(backup.relative_to(ctx.target.root)) if backup is not None else None
            return JSONResponse(
                {
                    "status": "saved",
                    "backup_path": rel_backup,
                    "reload_hint": ctx.target.reload_hint,
                    "shutdown_in_sec": int(os.environ.get("EASY_CONFIG_SHUTDOWN_DELAY_SEC", "10")),
                }
            )
        except ValidationError as exc:
            raise _http_error(exc, 400) from exc
        except EasyConfigError as exc:
            raise _http_error(exc, 400) from exc

    if static_dir.is_dir():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app


def _maybe_reload(ctx: SessionContext) -> None:
    hook = easy_config_repo_root() / "scripts" / "reload-hook.sh"
    reload_script = ctx.target.root / "scripts" / "reload.sh"
    if reload_script.is_file() and hook.is_file():
        subprocess.run(
            [str(hook), str(ctx.target.root)],
            check=False,
            capture_output=True,
            text=True,
        )
