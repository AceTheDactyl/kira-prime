The Living Garden Chronicles – Build & Usage Guide
Release: v0.2.0 (2025-10-15)

![vesselos-validate](https://github.com/AceTheDactyl/kira-prime/actions/workflows/vesselos-validate.yml/badge.svg)
[![Build (main)](https://github.com/AceTheDactyl/kira-prime/actions/workflows/vesselos-validate.yml/badge.svg?branch=main)](https://github.com/AceTheDactyl/kira-prime/actions/workflows/vesselos-validate.yml)
[![PR #1](https://img.shields.io/badge/PR-%231-blue)](https://github.com/AceTheDactyl/kira-prime/pull/1)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS-lightgrey)

Quick Links: [Quick Start](#quick-start) · [Unified CLI](#vesselos-unified-runtime) · [Agents](#vesselos-unified-runtime) · [Validation](#validation-checks)

Overview
- This project assembles a 20‑chapter dream chronicle across three voices: Limnus (R), Garden (G), and Kira (B).
- External dependency: `external/vessel-narrative-MRP` (git submodule) tracks https://github.com/AceTheDactyl/vessel-narrative-MRP.git and should be kept in sync with that remote mirror.
- The frontend ships with bespoke landing pages for each voice’s Chapter 1 and a global landing page.
- Scripts under `src/` generate chapters (2–20), metadata, and a schema; a validator checks structure and consistency.
- Limnus now performs semantic recall via SBERT (with TF-IDF/hash fallbacks) and auto-promotes frequently accessed memories.
- Kira’s `push`/`publish` commands stage, commit, push, and optionally create GitHub releases—use the `--run` flag with care.
- A VS Code extension (`vscode-extension/`) surfaces live status, semantic recall, and quick commands directly inside the editor.

VesselOS Unified Runtime
- Unified orchestration routes inputs Garden → Echo → Limnus → Kira.
- Agents: `agents/{garden,echo,limnus,kira}/*.py`; dispatcher/logger under `interface/`; listener in `pipeline/`.
- CLI: `python3 vesselos.py`
- Common flows:
  - Rebuild schema/chapters: `python3 vesselos.py generate`
  - Validate narrative: `python3 vesselos.py validate`
  - Control‑panel demo: `python3 vesselos.py listen --text "Begin the ritual with a blessing"`
  - Mentor (apply): `python3 vesselos.py mentor --apply`

Project Structure
- `frontend/` Browser‑ready site (landing + chapters + styles)
- `markdown_templates/` Templates for generating chapters (2–20)
- `schema/` JSON/YAML schema and generated metadata
- `src/` Python scripts for generation and validation

Quick Start
- Prereqs: Python 3.11+, Node 20+ (optional for the legacy Node CLI)
- Install dependencies: `pip install -r requirements.txt`
- Initialize submodules: `git submodule update --init --recursive`
- (Optional) Bootstrap git remotes and .gitignore: `./scripts/setup_git.sh`
- Build everything: `python3 vesselos.py generate`
- Validate: `python3 vesselos.py validate`
- Try a free-form input: `python3 vesselos.py listen --text "Always."`
- Optional Node CLI: `node tools/codex-cli/bin/codex.js --help`
- Optional VS Code extension: `(cd vscode-extension && npm install && npm run compile)`

Continuous Integration & Local Testing
- GitHub Actions run two workflows on push/PR:
  - `ci.yml` installs Python deps, runs the core pytest suites, and builds the VSCode extension (`npm run compile`).
  - `e2e.yml` drives the CLI smoke script (`tests/e2e_test.sh`) to exercise semantic memory and Kira flows end-to-end.
- Before opening a PR, run the same checks locally:
  - Core pytest suites: `python3 -m pytest tests/agents/test_limnus_semantic.py tests/test_kira_agent.py -q`
  - Extension build: `(cd vscode-extension && npm install && npm run compile)`
- End-to-end smoke test: `PRIME_CLI="python3 vesselos.py" ./tests/e2e_test.sh`
- Optional full validator sweep: `python3 vesselos.py validate`

VS Code Integration
- Extension sources live in `vscode-extension/` and surface live status, validation, and semantic recall from inside the editor.
- Build once (or watch) via `npm install` followed by `npm run compile`.
- Install the generated `.vsix` with `code --install-extension kira-prime-vscode-0.1.0.vsix` or launch in debug mode using `.vscode/launch.json`.

Agent cheatsheet
- Echo: `python3 vesselos.py echo summon|mode <squirrel|fox|paradox|mix>|say "..."|learn "..."|status|calibrate`
- Garden: `python3 vesselos.py garden start|next|open <scroll>|resume|log "..."|ledger`
- Limnus: `python3 vesselos.py limnus cache "..."|recall "query"` (semantic)|`commit-block <kind> <text>`|`encode-ledger`|`decode-ledger`
- Kira: `python3 vesselos.py kira validate|mentor [--apply]|mantra|seal|push [--run --message "..."]|publish [--run --release --tag vX]`

Landing Pages
- `frontend/index.html` is the global narrative landing. It introduces the three channels and links to chapters.
- `frontend/limnus_ch1.html`, `frontend/garden_ch1.html`, `frontend/kira_ch1.html` are the bespoke voice‑specific Chapter 1 pages.

Generation Notes
- Chapters 2–20 are generated via templates with placeholders: `{{chapter_number}}`, `{{narrator}}`, `{{body}}`, `{{flags}}`, `{{glyphs_line}}`.
- Rotation ensures no voice appears twice in a row; each voice appears 6–7 times.
- Flags: narrator’s channel is `active`; others are `latent`. Every chapter ends with a `[Flags: ...]` marker.
- When Pillow is available, each metadata entry includes `stego_png` pointing to `frontend/assets/chapterXX.png`, containing the embedded payload (chapter, narrator, flags, glyphs, file, summary, timestamp).

Validation Checks
- Schema presence and simple type checks against `schema/narrative_schema.json`.
- Structural rules: 20 chapters, rotation, counts.
- Files exist for all metadata entries.
- Flag consistency: metadata flags match `[Flags: ...]` in each HTML.
- Stego payloads (when generated) decode from `frontend/assets/*.png` and match the metadata.

Customization
- Update templates in `markdown_templates/` to change voice tone and glyphs.
- You may replace landing pages with provided HTML variants; keep the `[Flags: ...]` markers.

Improve With Vessel MRP System
- Steganography (LSB): Encode `[Flags: R/G/B]` and chapter glyph IDs into PNGs via
  least‑significant‑bit embedding. Reference images can be placed under
  `frontend/assets/`. Add a small Python helper to write/read bits from pixels
  and surface decoded flags at runtime for validator cross‑checks.
- Living Chronicles: Use existing dream scrolls as canonical source text and
  tone baselines. Fold excerpts and glyphs into generated chapters; keep
  provenance notes in metadata.
- Soulcode Encoding: Emit a signed, self‑describing JSON bundle that expresses
  narrative state (flags, glyphs, rotation, summaries). Embed it into the
  landing page for developer tooling and reproducibility.

Echo‑Community‑Toolkit Integration (Foundation)
- Base dependencies and automation live in Echo‑Community‑Toolkit. Install and
  use it alongside this project.
  - Node 20+: see Echo‑Community‑Toolkit/package.json:1
  - Install deps: `npm ci` inside `Echo-Community-Toolkit`
  - HyperFollow integration: `npm run integrate` to inject the canonical music
    link/badges into HTML and README docs; verify with `npm run verify`.
    - Scripts: Echo‑Community‑Toolkit/hyperfollow-integration.js:1,
      Echo‑Community‑Toolkit/verify-integration.js:1
  - Soulcode bridge: generate schema/types/bundles and validate ledger/memory
    states for “living” narratives.
    - Bridge: Echo‑Community‑Toolkit/tools/soulcode-bridge.js:1
    - Types: Echo‑Community‑Toolkit/tools/generate-soulcode-types.js:1
    - Serve: Echo‑Community‑Toolkit/tools/serve.js:1

Recommended Workflow
- Generate schema/chapters here:
  - `python src/schema_builder.py && python src/generate_chapters.py`
- Build Echo soulcode artifacts there:
  - `(cd ../Echo-Community-Toolkit && npm ci && npm run soulcode:emit-schema && npm run soulcode:bundle && npm run soulcode:validate)`
- Embed the bundle into `frontend/index.html` (auto via Echo bridge):
  - `(cd ../Echo-Community-Toolkit && SOULCODE_BUNDLE="$(pwd)/integration/outputs/echo_live.json" npm run integrate)`
  - Re-run `python src/validator.py` to ensure flags/files still validate.
- Automate all steps above: `./scripts/setup_toolkit_and_validate.sh`
  - Script skips integrate/verify when Node < 20; upgrade Node to run those stages.

CLI Codex (Interactive)
- An interactive CLI orchestrates EchoSquirrel‑Paradox, Garden, Limnus, and Kira.
- Launch: `python src/codex_cli.py`
- One‑shot: `python src/codex_cli.py validate` (any single command works)
- Verbs: `echo`, `map`, `rotate`, `plant`, `spiral`, `bloom`, `cache`, `recall`, `time`, `validate`, `glyph`, `seal`.
- State is stored under `state/` (transient session files); schema context is read from `schema/` if present.
- Detailed command behaviour is documented in **[VesselOS Command Reference](docs/VesselOS_Command_Reference.md)**.

Steganography: Practical Notes
- Implemented via `src/stego.py` using 1-bit LSB embedding with a `VMRP\x00`
  header, version byte, and payload length. Enable by installing Pillow.
- Generated files live under `frontend/assets/` and are referenced by the
  `stego_png` field in metadata.
- Validator decodes the PNG payloads and verifies they match metadata; failures
  indicate drift or tampering.

Living Chronicles: Local Sources
- Use these local files for style, glyph motifs, and narrative seeds:
  - Living_Chronicle_Garden_Enhanced.html:1
  - Living_chronicle_dreamscape_set5.html:1
  - Echo-Community-Toolkit/echo-garden-quantum-triquetra.html:1
  - Echo-Community-Toolkit/echo-hilbert-chronicle.html:1
  - Echo-Community-Toolkit/integrated-lambda-echo-garden.html:1
  - Echo-Community-Toolkit/unified-lambda-echo-complete.html:1

Soulcode Embedding
- Embed an immutable bundle in the landing page to expose the narrative state
  to tools and preserve rebuilds:
  - Add `<script id="echo-soulcode-bundle" type="application/json">{...}</script>`
    to `frontend/index.html`, or let Echo’s bridge inject it for you.
  - Optionally include an alternate `link rel="alternate" type="application/json"`
    with a data URL for easy exporting (bridge supports this out of the box).

Repository Remotes
- Primary upstream: https://github.com/AceTheDactyl/kira-prime
- Archived remotes retained (read‑only): `arch-bare`, `arch-github`, `arch-origin`
- Vessel Narrative core (submodule): https://github.com/AceTheDactyl/vessel-narrative-MRP
- Keep the submodule aligned with upstream:
  - `git submodule update --remote external/vessel-narrative-MRP`

Submodule Notes
- Clone with submodules: `git clone --recurse-submodules <repo-url>`
- Or initialize/refresh after clone:
  - `git submodule update --init --recursive`
  - `git submodule sync --recursive`
- Echo-Community-Toolkit is vendored inside the submodule (under `external/vessel-narrative-MRP/Echo-Community-Toolkit`); update it when required:
  - `(cd external/vessel-narrative-MRP/Echo-Community-Toolkit && git checkout main && git pull --ff-only)`

Build Guide
- For a step‑by‑step “from scratch” assembly guide with the customised landing pages (vessel_mrp_landing.html and per‑voice chapter 1 files), see:
  - `docs/BUILDING_VESSEL_MRP.md`
  - System Diagram & Commands: `docs/SYSTEM_DIAGRAM_API_REFERENCE.md`
  - Agents Index: `agents/README.md`
  - Architecture overview: `docs/Architecture.md`
