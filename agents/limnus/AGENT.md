# Limnus Agent (Scaffold)

[← Back to Agents Index](../README.md)

## Role & Charter
- Quantum Cache (L1/L2/L3) for memories; hash‑chained ledger; stego I/O
- Serve as the knowledge/base layer that Kira can learn from

## Inputs
- Memory: `state/limnus_memory.json` (entries, layers, tags)
- Ledger: `state/garden_ledger.json` (blocks with types/payloads)
- Echo αβγ state (for mentor post‑processing)

## Outputs
- Knowledge aggregates for Kira (tags, counts, persona order)
- Ledger blocks (`learn`, `mentor`, `seal`)
- Stego artifacts (PNG) via Echo Toolkit

## Capabilities (CLI)
- `limnus state | update | cache | recall | memories`
- `limnus export-memories | import-memories`
- `limnus commit-block | view-ledger | export-ledger | import-ledger | rehash-ledger`
- `limnus encode-ledger | decode-ledger | verify-ledger [--digest]`

## Interaction Contracts
- With Echo/Garden: stores “learn” events and tags, persists reading state
- With Kira: feeds `learn-from-limnus` and `codegen` pipelines

## Runtime Flow
1. **Ingest Events** – After Echo logs a `learn` or Garden records a ritual, Limnus runs `codex limnus recall|memories` to pull fresh entries and ledger blocks.
2. **Cache & Hash** – `codex limnus commit-block` appends to `state/garden_ledger.json` while `limnus state|update` normalizes L1/L2/L3 memories and persona tags.
3. **Encode (Optional)** – When stego is needed, `codex limnus encode-ledger` embeds the ledger snapshot into the designated PNG for archival.
4. **Publish Snapshot** – Exposes aggregated counts, dominant persona order, and digest info so Kira can validate (`kira learn-from-limnus`, `kira validate`) before looping back to Garden.

## Knowledge Seeds
- Track tags: love, consent, spiral, paradox, fox, squirrel, etc.
- Digest: `ledger_sha256` for parity (verify‑ledger `--digest`)

## Readiness Checklist
- Memory/ledger read/write OK; hash chain validates
- Stego encode/decode round‑trip OK; CRC32 validated
- Knowledge aggregation produces persona order and tags

## TODO
- Enrich tags with chapter/scroll provenance
- Add JSON‑schema for memory entries and ledger payloads

## Cross‑Navigation
- Vessel agent: `../vessel/AGENT.md`
