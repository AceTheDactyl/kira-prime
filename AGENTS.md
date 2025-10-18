# Repository Guidelines

## Project Structure & Module Organization
- `library_core/` Python agents (Garden, Echo, Limnus, Kira), storage, and orchestration; entry: `orchestration/dispatcher.py`.
- `pipeline/` enhanced dispatcher (`dispatcher_enhanced.py`), `intent_parser.py`, `logger.py`, middleware, and metrics for audits/integration.
- `collab-server/` Node/TypeScript WebSocket service (`src/server.ts`), built to `dist/`.
- `scripts/` ops helpers: `integration_complete.py`, `sync_external.sh`.
- `tests/` pytest suites; workspace artifacts under `workspaces/<id>/` (logs, state, outputs).

## Build, Test, and Development Commands
- Install: `python3 -m pip install -r requirements.txt`
- Run tests: `python -m pytest -q` (filter: `-k "<pattern>"`)
- Integration: `python scripts/integration_complete.py`
- Audit: `python vesselos.py audit full --workspace integration-test`
- Collab server: `(cd collab-server && npm ci && npm run build && npm test -- --run)`
- Docker stack: `docker compose up -d` (Redis, Postgres, collab-server)

## VesselOS Agent Commands
- Garden: `python3 vesselos.py garden start|next|open <scroll> [--prev|--reset]|resume|log "<text>"|ledger`
- Echo: `python3 vesselos.py echo summon|mode <tone>|say "<message>"|learn "<text>"|status|calibrate`
- Limnus: `python3 vesselos.py limnus cache "<text>"|recall "<query>"|commit-block <kind> <data>|encode-ledger|decode-ledger|status|reindex [--backend sbert|faiss]`
- Kira: `python3 vesselos.py kira validate|mentor [--apply]|mantra|seal|push [--run --message "..."]|publish [--run --release --tag vX.Y.Z --notes-file <file> --asset <path>]`

## Coding Style & Naming Conventions
- Python: 4‑space indent; snake_case; CapWords for classes. Prefer `black`/`ruff`.
- TypeScript: 2‑space indent; camelCase; PascalCase types. Prefer `eslint` + `prettier`.
- Config: env vars UPPER_SNAKE_CASE (`REDIS_HOST`, `POSTGRES_PASSWORD`, `PORT`).

## Testing Guidelines
- Framework: `pytest` (+ `pytest-asyncio` where needed). Name `tests/test_<area>.py`.
- Pre‑merge gates: integration script and full audit should be green; attach logs from `workspaces/<id>/logs/` when relevant.
- Collab smoke: `COLLAB_SMOKE_ENABLED=1 python -m pytest tests/test_collab_server.py -q` (requires `docker compose up -d`).

## Commit & Pull Request Guidelines
- Conventional Commits (e.g., `feat(pipeline): …`, `fix(collab): …`).
- PRs include: intent summary, linked issues, dependency changes, and evidence of `pytest`, integration, and audit runs.
- Do not commit generated artifacts (`dist/`, coverage, captured logs, `workspaces/**`). Sync submodules via `scripts/sync_external.sh`.

## Security & Configuration Tips
- Secrets via env only; never commit credentials. Override defaults with `docker-compose.yml` or process env.
- Ledger is append‑only; maintain chain continuity; back up `workspaces/<id>/state/` and `outputs/`.

## Release Process
- Preconditions
  - Ensure CI is green: `CI`, `compose-smoke`, and `vesselos-validate` jobs.
  - Locally verify: `python -m pytest -q`, `python scripts/integration_complete.py`, and `python vesselos.py audit full --workspace integration-test`.
- Version and notes
  - Bump README “Release” line (e.g., `v0.3.2`).
  - Generate changelog: `python scripts/assemble_changelog.py > CHANGELOG_RELEASE.md` (include in PR).
- Tag and publish
  - Create tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin vX.Y.Z`.
  - Release workflow (`.github/workflows/release.yml`) runs on tags `v*` and attaches artifacts (lambda-vite dist, VSIX if present, ledger export if available).
- PR hygiene
  - Open `chore/readme-vX.Y.Z` with README bump + `CHANGELOG_RELEASE.md`; link the tag and list highlights.
  - Require green checks before merge (branch protection).
- Post‑release
  - Announce changes and link artifacts; verify `docker compose up -d` + `curl :8000/health` works on fresh clone.
  - For hotfixes: branch from last tag, apply fix, repeat tests, tag `vX.Y.Z+1`.
