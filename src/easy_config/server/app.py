from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


def _static_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "static"


def create_app(*, dev: bool = False) -> FastAPI:
    app = FastAPI(
        title="Easy Config",
        version="0.1.0",
        docs_url="/docs" if dev else None,
        redoc_url=None,
    )
    static_dir = _static_dir()

    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    @app.get("/config")
    def config_page() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    if static_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=static_dir), name="assets")

    return app
