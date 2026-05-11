# ConsultaACE

Stack: Python 3.13, [Reflex](https://reflex.dev) 0.8.28+ (web framework), oracledb, uv.

## Dev commands

```sh
uv run reflex run          # dev server with hot reload
uv run reflex run --prod   # production build
uv sync                    # install dependencies from uv.lock
```

## Structure

- `ConsultaACE/ConsultaACE.py` — real app entrypoint (Reflex State + pages). `main.py` at root is a stub and not the entrypoint.
- `rxconfig.py` — Reflex config (app name `ConsultaACE`, plugins: TailwindV4, Sitemap).
- `.web/` — generated build artifacts (gitignored, auto-created by `reflex run`).
- `.states/` — Reflex state pickle persistence (gitignored).

## Gotchas

- **No tests, no linter, no formatter, no CI** configured. Committing changes is up to the developer.
- **Hardcoded Oracle credentials** live in `ConsultaACE/ConsultaACE.py:19-22`. Be aware when editing — do not commit real credentials.
- **`main.py` is unused** — the app runs entirely through Reflex's CLI.
- README is empty; no additional documentation exists.
- `uv` is the only package manager available (no pip, no poetry).
