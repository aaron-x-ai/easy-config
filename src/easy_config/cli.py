from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import typer
import uvicorn

from easy_config import __version__
from easy_config.doctor import run_doctor
from easy_config.errors import EasyConfigError
from easy_config.paths import easy_config_repo_root
from easy_config.server.app import create_app
from easy_config.session import create_session

app = typer.Typer(
    name="easy-config",
    help="Easy Config — visual configuration for Hermes skills.",
    no_args_is_help=True,
)


def app_entry() -> None:
    app()


def _repo_root():
    return easy_config_repo_root()


def _pick_port(preferred: int) -> int:
    import socket

    if preferred > 0:
        return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@app.command("doctor")
def doctor_cmd(
    skill: str | None = typer.Option(None, "--skill", help="Optional skill directory name."),
) -> None:
    skill_dir = None
    if skill:
        from easy_config.skill_resolver import resolve_skill

        skill_dir = resolve_skill(skill)
    issues = run_doctor(skill_dir=skill_dir, repo_root=_repo_root())
    if issues:
        for item in issues:
            typer.echo(f"[FAIL] {item}", err=True)
        raise typer.Exit(code=1)
    typer.echo("[OK] Easy Config doctor passed.")


@app.command("validate-schema")
def validate_schema_cmd(
    file: str = typer.Option(..., "--file", help="Path to easy-config-schema.json"),
) -> None:
    from pathlib import Path

    import json

    from jsonschema import Draft202012Validator

    path = Path(file).expanduser().resolve()
    schema = json.loads(path.read_text(encoding="utf-8"))
    meta_path = _repo_root() / "schemas" / "easy-config-protocol.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    Draft202012Validator(meta).validate(schema)
    typer.echo(f"[OK] schema valid: {path}")


@app.command("serve")
def serve_cmd(
    skill: str = typer.Option(..., "--skill", help="Target skill name."),
    port: int = typer.Option(0, "--port", help="Listen port; 0 = auto."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print URL JSON and exit."),
) -> None:
    """Start the temporary local configuration web server."""
    try:
        session = create_session(skill)
    except EasyConfigError as exc:
        typer.echo(json.dumps({"status": "error", "error": exc.code, "message": str(exc)}), err=True)
        raise typer.Exit(code=1) from exc

    chosen_port = _pick_port(port)
    base_url = f"http://127.0.0.1:{chosen_port}"
    payload = {
        "status": "ready",
        "url": f"{base_url}/config?skill={skill}&token={session.token}",
        "expires_at": session.expires_at.astimezone().isoformat(),
        "skill": skill,
        "config_path": str(session.config_path),
        "session_dir": str(session.session_dir),
    }
    typer.echo(json.dumps(payload, ensure_ascii=False))

    if dry_run:
        return

    host = os.environ.get("EASY_CONFIG_HOST", "127.0.0.1")
    if host not in {"127.0.0.1", "localhost"}:
        typer.echo("[warn] EASY_CONFIG_HOST should stay on localhost for security.", err=True)
    uvicorn.run(
        create_app(
            session=session,
            dev=os.environ.get("EASY_CONFIG_DEV", "0") == "1",
            enable_lifecycle=True,
        ),
        host=host,
        port=chosen_port,
        log_level="info",
    )


@app.callback()
def main_callback(
    version: bool = typer.Option(False, "--version", "-V", help="Show version."),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()


if __name__ == "__main__":
    app_entry()
