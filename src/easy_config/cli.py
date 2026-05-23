from __future__ import annotations

import json
import os
import socket
import sys
from pathlib import Path
from typing import Optional

import typer
import uvicorn

from easy_config import __version__
from easy_config.doctor import run_doctor
from easy_config.server.app import create_app

app = typer.Typer(
    name="easy-config",
    help="Easy Config — visual configuration for Hermes skills.",
    no_args_is_help=True,
)


def app_entry() -> None:
    app()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _pick_port(preferred: int) -> int:
    if preferred > 0:
        return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@app.command("doctor")
def doctor_cmd(
    skill: Optional[Path] = typer.Option(
        None,
        "--skill",
        help="Optional skill directory to validate.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
) -> None:
    """Check local environment and Easy Config installation."""
    issues = run_doctor(skill_dir=skill, repo_root=_repo_root())
    if issues:
        for item in issues:
            typer.echo(f"[FAIL] {item}", err=True)
        raise typer.Exit(code=1)
    typer.echo("[OK] Easy Config doctor passed.")


@app.command("serve")
def serve_cmd(
    skill: Optional[str] = typer.Option(
        None,
        "--skill",
        help="Target skill name (P1: required for full flow).",
    ),
    port: int = typer.Option(0, "--port", help="Listen port; 0 = auto."),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print planned URL and exit without starting the server.",
    ),
) -> None:
    """Start the temporary local configuration web server."""
    chosen_port = _pick_port(port)
    token = "p0-dev-token"
    skill_name = skill or "unknown"
    base_url = f"http://127.0.0.1:{chosen_port}"

    payload = {
        "status": "ready",
        "url": f"{base_url}/config?skill={skill_name}&token={token}",
        "skill": skill_name,
        "port": chosen_port,
        "message": "P0: health-only server; configuration flow arrives in P1.",
    }
    typer.echo(json.dumps(payload, ensure_ascii=False))

    if dry_run:
        return

    if skill is None:
        typer.echo(
            "[warn] --skill not set; P0 starts health server only.",
            err=True,
        )

    host = os.environ.get("EASY_CONFIG_HOST", "127.0.0.1")
    uvicorn.run(
        create_app(dev=os.environ.get("EASY_CONFIG_DEV", "0") == "1"),
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
