# Repository Guidelines

## Project Structure & Module Organization
- Agents: `agents/{echo,garden,limnus,kira}/` (core logic per agent).
- Orchestration: `interface/dispatcher.py`, `pipeline/listener.py`, `interface/logger.py`.
- Runtime state: `state/` (e.g., `echo_state.json`, `garden_ledger.json`, `limnus_memory.json`, `ledger.json`).
- Site & metadata: `frontend/`, `schema/`; generators/validators in `src/`.
- Tools: `tools/codex-cli/` (optional Node CLI), CI in `.github/workflows/`.

## Build, Test, and Development Commands
- Generate: `python3 vesselos.py generate` — builds schema, chapters, soulcode bundle.
- Validate: `python3 vesselos.py validate` — structural + flags + provenance checks.
- Demo input: `python3 vesselos.py listen --text "Always."` — routes Garden → Echo → Limnus → Kira.
- Agent namespaces: e.g., `python3 vesselos.py echo mode fox`, `python3 vesselos.py garden log "note"`.
- Node CLI (optional): `node tools/codex-cli/bin/codex.js --help`.

## Coding Style & Naming Conventions
- Python: 4‑space indent, `snake_case`, small functions, docstrings for non‑trivial code.
- Node/TS: 2‑space indent, `camelCase`, ESM imports; keep CLI lightweight.
- HTML/CSS: preserve narrator classes; avoid manual edits to generated chapter markup.
- JSON/YAML: script‑generated; do not hand‑edit `schema/*` or `frontend/chapter*.html`.

## Testing Guidelines
- Smoke: `python3 vesselos.py validate` (run locally and in CI).
- Prefer `pytest`; name tests `test_*.py` under `tests/` (fixtures in `tests/fixtures/`).
- Stego parity: ensure `frontend/assets/ledger.png|json` matches `state/ledger.json`.

## Commit & Pull Request Guidelines
- Conventional Commits (e.g., `feat(limnus): encode ledger artifact`), ≤72‑char subject.
- Include regenerated artifacts with the code that produced them.
- PRs: describe changes, list commands run (generate, validate, CLI), link issues, add screenshots for UI changes.

## Security & Configuration Tips
- Python 3.11+ and Node 20+. Keep secrets in `.env` (gitignored); never commit credentials.
- Use PNG‑24/32 for LSB artifacts; avoid palette PNG/JPEG.
- Default orchestration for free‑form input: Garden → Echo → Limnus → Kira.
