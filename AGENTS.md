# Repository Guidelines

## Project Structure & Module Organization
- `library_core/` houses Python agents (Garden, Echo, Limnus, Kira), orchestration helpers, dictation pipeline, and workspace utilities. Notables: `agents/`, `orchestration/dispatcher.py` (Garden→Echo→Limnus→Kira loop), `dictation/` (session + MRP bridge), `collab/` (FastAPI server).
- `pipeline/` contains dispatcher wiring, `intent_parser.py`, and logging glue referenced by the integration suite and audits.
- `collab-server/` includes the TypeScript/WebSocket service (`src/server.ts`), Node build config, and output `dist/`.
- `docker-compose.yml` (repo root) orchestrates Redis/Postgres and the collab server container for local dev.
- `scripts/` provides ops helpers: `integration_complete.py` (12 ritual checkpoints), `run_mrp_cycle.py` (20‑chapter build), `sync_external.sh` (submodule sync), deployment utilities.
- `tests/` contains pytest suites; additional tests and assets reside in submodules (`echo-community-toolkit/`, `kira-prime/`, `The-Living_Garden-Chronicles/`). Keep CI focused on top‑level `tests/`.
- Workspace artifacts land under `workspaces/<id>/` (see `logs/`, `state/`, `outputs/`, `collab/events.jsonl`).

## Build, Test, & Development Commands
- `python3 -m pip install --break-system-packages -r requirements.txt` — install core Python deps (pytest, asyncpg, redis, httpx, click).
- `python scripts/integration_complete.py` — run sequential Garden→Echo→Limnus→Kira checks (ledger/memory, personas, cache, parity).
- `python vesselos.py audit full --workspace <id>` — run health, ledger, memory, personas, consents, performance audits for a workspace.
- `python -m pytest -q` — execute unit/async tests; `python -m pytest tests/test_collab_server.py` for a focused collab smoke; `-k "<pattern>"` to filter.
- `npm ci && npm run build && npm test -- --run` (inside `collab-server/`) — validate the Node/WebSocket stack.
- `docker compose up -d` — start Redis/Postgres and the collab server using the repo‑root `docker-compose.yml`.

## Coding Style & Naming Conventions
- Python: 4‑space indentation; snake_case for functions/variables; CapWords for classes. Use `black`/`ruff` if available; keep agent docstrings concise.
- TypeScript/Node: 2‑space indentation; camelCase variables; PascalCase types; lint with `eslint` + `prettier`. Treat `collab-server/src/server.ts` as the canonical service entry.
- Markdown/YAML: aligned keys, ≤100‑col soft wrap; prefer lists/tables for rituals.
- Config: env vars are UPPER_SNAKE_CASE (`REDIS_HOST`, `POSTGRES_PASSWORD`); file keys lower‑kebab (`docker-compose.yml`).
- Naming: workspace IDs are short slugs (`integration-test`); CLI uses hyphenated flags (`--workspace`).

## Testing Guidelines
- Framework: `pytest` + `pytest-asyncio`. Name files `test_<area>.py`; add fixtures to spin temp workspaces under `workspaces/`.
- Integration: `scripts/integration_complete.py` + `python vesselos.py audit full` should be green pre‑merge; attach logs from `workspaces/<id>/logs/` in PRs when relevant.
- Collab smoke: start `docker compose up -d`, then `python -m pytest tests/test_collab_server.py`; verifies dictation hydration and MRP trigger endpoint.
- Optional FAISS: guard with `pytest.importorskip("faiss")` for portability. Mark slower checks `@pytest.mark.slow`.
- Agent changes require tests for ledger hash continuity, persona glyph↔tone mapping, consent capture, and dispatcher sequencing.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (e.g., `feat(collab): hydrate workspace events`, `fix(ledger): repair hash chain`); keep scopes aligned with directories touched.
- PRs should summarize intent, link issues, note dependency changes, and include evidence of `pytest`, integration script, and audit runs. Attach screenshots/log snippets for UI or pipeline output.
- Avoid committing generated artifacts (`dist`, coverage, captured logs) unless explicitly requested; ensure submodules are synchronized via `scripts/sync_external.sh` prior to review.
- Highlight migration steps (e.g., new environment variables, schema upgrades) in PR descriptions so operators can replicate deployments without surprises.

## Architecture & Security Notes
- Flow: Garden→Echo→Limnus→Kira via `library_core/orchestration/dispatcher.py`. Collab events are brokered by `library_core/collab/server.py` and mirrored to `workspaces/<id>/collab/events.jsonl`.
- Submodules: this repo integrates `echo-community-toolkit/`, `kira-prime/`, `The-Living_Garden-Chronicles/`, `vessel-narrative-MRP/`. Keep them synced (`scripts/sync_external.sh`).
- Secrets: use env vars or ignored `.env.local`. The stack reads `REDIS_*`, `POSTGRES_*`, and `PORT`. Override defaults via `docker-compose.yml` or process env.
- Validation: post‑deploy, run `python vesselos.py audit full --workspace <id>` to verify hydration, ledger integrity, persona normalization, and consent capture.
- Ledger: treat as append‑only; rehash only with tool support; maintain chain continuity. Back up `workspaces/<id>/state/` and `outputs/` regularly.
