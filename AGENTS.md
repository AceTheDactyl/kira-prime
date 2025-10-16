# Repository Guidelines

## Project Structure & Module Organization
- Core Python agents live under `agents/`, with shared utilities in `interface/`, `pipeline/`, and `src/`.
- Persisted state, ledgers, and vector artifacts reside in `state/` and `state/vector_store/`; release bundles land in `dist/`.
- Front-end work sits in `lambda-vite/` (new Vite scaffold) with a legacy viewer under `Echo-Community-Toolkit/lambda-vite/`; docs and roadmaps are under `docs/`.
- Tests are split between `tests/` (Python/pytest) and `lambda-vite/tests/` (Vitest).

## Build, Test, & Development Commands
- Install deps: `pip install -r requirements.txt` (Linux adds `faiss-cpu`) and `npm ci` inside `lambda-vite/`.
- Run all Python tests: `python -m pytest -q`.
- UI build & tests: `npm run build` then `npm test -- --run` within `lambda-vite/`.
- Release checklist: `./scripts/checklist_phase2.sh` (installs deps, builds FAISS index, runs tests, packages artifacts).
- Simulate packaging only: `python vesselos.py publish --notes-file CHANGELOG_RELEASE.md`.

## Coding Style & Naming Conventions
- Python uses 4-space indentation and snake_case for functions/variables; classes follow CapWords.
- TypeScript/React favors 2-space indentation, camelCase identifiers, PascalCase components.
- Keep Markdown and YAML tidy; run `black`, `flake8`, or `eslint/prettier` when touching corresponding files.

## Testing Guidelines
- Python suites rely on pytest; name files `test_*.py` and prefer descriptive fixture names.
- Front-end tests use Vitest with files under `lambda-vite/tests/*.test.tsx`.
- Ensure FAISS-dependent tests skip gracefully by checking `pytest.importorskip("faiss")`.
- Always run `python -m pytest` before opening a PR; UI changes should include `npm test -- --run`.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat:`, `fix:`, `chore:`). Scope modules where meaningful, e.g., `feat(limnus): add faiss backend`.
- Each PR should summarize changes, link issues, and attach screenshots for UI updates or paste changelog snippets.
- Include test evidence (`python -m pytest`, `npm test`) and mention `./scripts/checklist_phase2.sh` runs when relevant.
- Keep generated artifacts out of commits except when explicitly requested (e.g., release bundles).

## Security & Configuration Tips
- Never commit secrets; use `.env` or GitHub secrets. `kira publish --release` requires `GH_TOKEN` with `repo` scope.
- The GitHub Actions release workflow (`release.yml`) assumes `node 20` and authenticated `gh`; confirm access before toggling `--release`.
