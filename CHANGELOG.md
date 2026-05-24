# Changelog

## [0.3.0] - 2026-05-24

### Added

- P2: idle timeout watcher (default 15 min inactivity)
- Session expiry / closed checks on API (`session_expired`, `session_closed`)
- Post-save graceful shutdown (default 10s)
- Frontend strips token from URL after load
- Playwright e2e: `bash scripts/e2e.sh`
- Integration tests for lifecycle

## [0.2.0] - 2026-05-23

### Added

- P1: skill resolver, schema pipeline, config read/write with backup
- API: `GET /api/session`, `POST /api/config` with token auth
- Static config form UI (`static/app.js`)
- `validate-schema` CLI command
- Demo skill fixture and integration tests

## [0.1.0] - 2026-05-23

### Added

- P0 scaffold: src layout, `SKILL.md`, health endpoint, `doctor` command
- Shell scripts: `install.sh`, `launch_config_ui.sh`, `doctor.sh`
