# ConsultaACE

Stack: Python 3.13, [Reflex](https://reflex.dev) 0.8.28+ (web framework), oracledb, uv.

## Dev commands

```sh
uv run reflex run          # dev server with hot reload
uv run reflex run --prod   # production build
uv sync                    # install dependencies from uv.lock
```

`.venv/` is pre-existing — `uv sync` only needed when `pyproject.toml` or `uv.lock` change.

## Structure

- `ConsultaACE/ConsultaACE.py` — real app entrypoint (Reflex State + pages). `main.py` at root is a stub and not the entrypoint.
- `rxconfig.py` — Reflex config (app name `ConsultaACE`, plugins: TailwindV4, Sitemap).
- `ConsultaACE/db.py` — SQLAlchemy engine + Oracle connection via Pydantic Settings (`ORACLE_*` env vars). Defines `SessionLocal` and an unused `get_db()` generator — the `State` calls `SessionLocal()` directly.
- `ConsultaACE/models.py` — SQLAlchemy models mirroring `database_schema.md` tables.
- `.web/` — generated build artifacts (gitignored, auto-created by `reflex run`).
- `.states/` — Reflex state pickle persistence (gitignored).

## Guidance for AI coding agents

- **Start mode**: `default_agent` is `plan` — create a short plan before editing.
- **Shell safety**: `bash` permission is `ask` — always request permission before running terminal commands.
- **How to run**: Use `uv run reflex run` for development; `uv run reflex run --prod` for production build. Use the preexisting `.venv/`.
- **Dependency management**: Run `uv sync` only when `pyproject.toml` or `uv.lock` change.
- **Database**: The app requires Oracle access (host `VDW-FidelidadAIX:1521` by default). Use `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN` to override credentials. `.env` is gitignored — do not commit secrets.
- **Entrypoint**: Primary app module is [ConsultaACE/ConsultaACE.py](ConsultaACE/ConsultaACE.py). Do not rely on `main.py`.
- **Artifacts**: Ignore `.web/` and `.states/` — they are generated and persisted by Reflex.
- **Testing & CI**: There are no tests, linters, or CI configured. Make minimal, focused changes and suggest adding tests where appropriate.
- **Common pitfalls**: No SQLite fallback; the app will fail without Oracle network access. `uv` is the only package manager available.

## Important docs (link, do not duplicate)

- `database_schema.md` — canonical DB schema; reference, do not copy.
- `STYLE_GUIDE.md` — coding/convention guidance for this repo.
- `rxconfig.py` — Reflex configuration and plugins.

## OpenCode / opencode.json notes

- `default_agent: "plan"` — agents should produce a short plan before edits.
- `bash: "ask"` — ask before running shell commands.

## OpenCode config (`opencode.json`)

- `database_schema.md` and `STYLE_GUIDE.md` are loaded as instructions — always present, do not duplicate.
- `default_agent: "plan"` — agent starts in plan (read-only) mode by default.
- `bash: "ask"` permission — agent must ask before running commands.

## Gotchas

- **No tests, linter, formatter, typecheck, or CI** configured. Committing is manual.
- **Oracle credentials**: Dev defaults in `ConsultaACE/db.py:9-11`. Override via `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN` env vars. `.env` is gitignored — real credentials go there.
- **Requires Oracle network access** to host `VDW-FidelidadAIX:1521` (dev default). No SQLite fallback exists — the app will fail to start without connectivity.
- **`main.py` is unused** — the app runs entirely through Reflex's CLI.
- `uv` is the only package manager available (no pip, no poetry).
