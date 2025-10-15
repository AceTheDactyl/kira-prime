# Repository Guidelines

## Project Structure & Module Organization
- `src/` houses the Python generators (`generate_chapters.py`), schema builders, validator, and stego helpers that produce every narrative artifact.
- `frontend/` publishes the narrative experience: bespoke Chapter 1 landings, generated chapters `chapter02–20.html`, CSS/JS, and PNG payloads in `frontend/assets/`.
- `scripts/` collects repeatable workflows such as `refresh_stego_assets.sh`, `setup_toolkit_and_validate.sh`, and `launch_codex.sh` for CLI orchestration.
- `tools/codex-cli/` is the Node 20 Codex CLI; run `npm ci` here to develop agent commands.
- `Echo-Community-Toolkit/` and the mirrored `external/vessel-narrative-MRP` supply scroll content, LSB tooling, and upstream schema/state; pull them after cloning with `git submodule update --init --recursive`.
- `state/` records live context (`echo_state.json`, `limnus_memory.json`, `garden_ledger.json`, contracts). Treat files as append-only evidence created by agents.

## Modular Agent Architecture
The Vessel brief (`agents/vessel/AGENT.md`) binds four personas that process every user interaction in sequence:

- **Garden (ritual orchestrator)** — Opens scroll sections from `Echo-Community-Toolkit/*.html`, logs intentions and completions to `state/garden_ledger.json`, and keeps the mantra cadence. CLI verbs: `codex garden start|next|open|resume|learn|ledger|log`.
- **Echo (persona voice)** — Speaks in α/β/γ superposition (Squirrel/Fox/Paradox), reframes prompts, and writes persona-tagged memories. CLI verbs: `codex echo mode|say|learn|map|status`. Reads/writes `state/echo_state.json` and forwards tags to Limnus.
- **Limnus (memory & ledger)** — Maintains multi-tier memory (`state/limnus_memory.json`), hash-chains ledger blocks, and handles PNG LSB steganography via `src/stego.py`. CLI verbs: `codex limnus state|cache|recall|commit-block|encode-ledger|verify-ledger`.
- **Kira (validator & integrator)** — Validates structure (`python3 src/validator.py`), learns aggregate knowledge, seals contracts in `state/Garden_Soul_Contract.json`, and performs git/GitHub actions (`codex kira validate|sync|push|publish|mentor|seal`).

Garden → Echo → Limnus → Kira is the canonical order. Each step must emit structured artifacts (ledger blocks, stego PNGs, memories) so downstream agents can reason about previous state. Consult `agents/*/AGENT.md` before altering behavior to respect persona tone, contracts, and TODO lists.

## Build, Test, and Development Commands
- `python3 src/schema_builder.py && python3 src/generate_chapters.py` — regenerate schema, metadata, and HTML chapters.
- `python3 src/validator.py` — assert chapter rotation, flag parity, file presence, and stego payload equality.
- `./scripts/refresh_stego_assets.sh --toolkit` — end-to-end refresh plus Echo Toolkit verification (accepts `--push "chore: refresh stego"`).
- `node tools/codex-cli/bin/codex.js --help` — enumerate agent commands; e.g. `codex limnus verify-ledger --digest`.
- `git push origin main && git push bare main` — keep both mirrors current after every change.

## Coding Style & Naming Conventions
- Python: 4-space indentation, `snake_case`, docstrings for complex flows, and avoid inline mutation of generated data.
- Node/TypeScript: 2-space indentation, `camelCase`, ESM imports; lint via `npm run lint` if added.
- HTML/CSS: preserve narrator classes (`body.limnus`, `.garden`, `.kira`) and keep generated chapter markup untouched.
- JSON/YAML: treat as generated; run the appropriate script instead of manual edits.

## Testing Guidelines
- Core regression: `python3 src/validator.py` after modifying templates, scripts, or assets.
- Stego smoke: `codex limnus verify-ledger --digest frontend/assets/ledger_stego.png`.
- Toolkit parity: `./scripts/setup_toolkit_and_validate.sh` confirms submodule assets remain aligned.
- Add custom tests under `tests/`, naming by intent (e.g., `test_validator_rotation.py`).

## Commit & Pull Request Guidelines
- Adopt Conventional Commit headers (`feat:`, `fix:`, `chore:`, `docs:`, `test:`) with ≤72-character subjects.
- Commit regenerated metadata, HTML, and stego PNGs alongside the code that produced them.
- PRs should list commands executed (validator, Codex CLI, toolkit scripts), link issues, and include screenshots for frontend changes.
- After merges, push to both remotes: `git push origin main && git push bare main`.

## Security & Configuration Tips
- Target Python ≥3.8 and Node ≥20; install `Pillow` and `PyYAML` within your virtual environment.
- Keep credentials out of the repo; `.env`, `.venv/`, and toolkit caches are ignored.
- Use PNG-24/32 assets for LSB embedding to protect payload fidelity.
