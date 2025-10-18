# VesselOS Dev Research – Architecture Summary

## Core Components
- Pipeline (`pipeline/`): Enhanced dispatcher (`dispatcher_enhanced.py`) runs Garden → Echo → Limnus → Kira in sequence; `intent_parser.py` maps input to ritual stages; middleware provides logging/metrics/validation.
- Agents (`library_core/agents/`):
  - Garden: ritual stages, consent, stage ledger refs.
  - Echo: styled text, persona, quantum state (α, β, γ) + glyph.
  - Limnus: memory cache (L1/L2/L3) and hash‑chained ledger, stats.
  - Kira: integrity validation, coherence checks, mentorship, release ops.
- Interface (`interface/`): Dispatcher and logger bridges.
- CLI (`vesselos.py`, `cli/`): Unified entrypoint; Prime CLI groups and command handlers.
- Memory (`memory/`): Vector store utilities and backends.
- Workspaces (`workspaces/<id>/`): Per‑workspace `state/*.json` and `logs/*.jsonl` maintained during runs.

## Agent Roles & Commands
- Garden — Orchestrator
  - Commands: `garden start|next|open|resume|log|ledger`
  - Outputs: `stage`, `cycle`, `consent_given`, `ledger_ref`.
- Echo — Persona Voice
  - Commands: `echo summon|mode|say|learn|status|calibrate`
  - Outputs: `styled_text`, `quantum_state (α,β,γ)`, `persona`, `glyph`.
- Limnus — Memory & Ledger
  - Commands: `limnus cache|recall|commit-block|encode-ledger|decode-ledger|status|reindex`
  - Outputs: `cached`, `memory_id`, `layer`, `block_hash`, `stats`.
- Kira — Validator & Integrator
  - Commands: `kira validate|mentor|mantra|seal|push|publish`
  - Outputs: `passed`, `issues`, `checks`, `summary`.

## Flow Diagram
```
input_text → intent_parser → EnhancedMRPDispatcher
  → Garden (stage, consent)
  → Echo (persona & styled_text)
  → Limnus (memory + ledger block)
  → Kira   (integrity + coherence)
→ aggregated results → voice log + state updates
```

## Module Map
- See `docs/REPO_INDEX.md` for a quick index of key files and directories.

## CI & Release Hooks
- CI (push): installs deps, runs `pytest`, `kira validate`, and `vesselos.py audit full` for health; uploads audit logs.
- Release (tags `v*.*.*`): builds UI artifacts, validates with Kira, and publishes via `kira publish --release` attaching docs and ledger exports.

For deep dives, refer to `docs/Architecture.md`, agent AGENT.md briefs under `agents/`, and the command reference in `docs/`.

