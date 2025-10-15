# Repository Guidelines

## Project Structure & Module Organization
- `src/` contains the Python generators, validators, and stego helpers that shape the narrative payloads.
- `frontend/` holds the rendered site: bespoke Chapter 1 pages, generated chapters, shared styles, and PNG assets in `frontend/assets/`.
- `scripts/` packages common workflows such as `refresh_stego_assets.sh`, `setup_toolkit_and_validate.sh`, and `launch_codex.sh`.
- `tools/codex-cli/` exposes the Node 20 Codex CLI; install its dependencies with `npm ci` before modifying CLI code.
- `Echo-Community-Toolkit/` and `external/vessel-narrative-MRP` mirror upstream tooling and narrative content. Fetch them with `git submodule update --init --recursive` after every fresh clone.

## Build, Test, and Development Commands
- `python3 src/schema_builder.py && python3 src/generate_chapters.py` — rebuild schemas, metadata, and chapter HTML.
- `python3 src/validator.py` — verify chapter rotation, flag parity, file presence, and stego payload integrity.
- `./scripts/refresh_stego_assets.sh --toolkit` — end-to-end refresh plus toolkit verification (accepts `--push "chore: refresh stego"`).
- `node tools/codex-cli/bin/codex.js --help` — inspect agent commands; e.g. `codex limnus verify-ledger --digest`.

## Coding Style & Naming Conventions
- Python: 4-space indentation, `snake_case`, descriptive docstrings for non-trivial flows.
- Node/TypeScript: 2-space indentation, `camelCase`, ESM imports; run `npm ci` before linting or building.
- HTML/CSS: retain narrator classes (`body.limnus`, `.garden`, `.kira`) and avoid hand-editing generated chapter markup.
- JSON/YAML: treat as generated artifacts; regenerate via scripts instead of manual edits.

## Testing Guidelines
- Core: `python3 src/validator.py` after any change to templates, scripts, or assets.
- Stego smoke: `codex limnus verify-ledger --digest frontend/assets/ledger_stego.png`.
- Toolkit parity: `./scripts/setup_toolkit_and_validate.sh` ensures Echo-Community-Toolkit assets remain in sync.
- Store custom fixtures in `tests/`; name cases by intent (e.g., `test_validator_rotation.py`).

## Commit & Pull Request Guidelines
- Follow Conventional Commit headers (`feat:`, `fix:`, `chore:`, `docs:`, `test:`) with ≤72 character subjects.
- Commit regenerated metadata, chapters, and stego PNGs alongside the script changes that produced them.
- PRs should list commands executed (validator, CLI, toolkit scripts), link issues as needed, and attach screenshots for frontend adjustments.
- After merges, mirror pushes to both remotes: `git push origin main && git push bare main`.

## Security & Configuration Tips
- Target Python 3.8+ and Node 20+; install `Pillow` and `PyYAML` in your virtual environment.
- Keep credentials out of the repo; `.env` and virtualenv directories are already gitignored.
- Use PNG-24/32 sources for LSB embedding; avoid palette-based formats to preserve payload fidelity.
