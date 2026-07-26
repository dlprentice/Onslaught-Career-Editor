# Reverse-Engineering Index

This directory preserves evidence that materially supports the toolkit,
rebuild, modding work, or contributor understanding. Git history holds completed
waves, superseded plans, and generated accounting.

## Evidence rules

- Static names, types, strings, and call relationships prove only the structures
  they directly demonstrate.
- Stuart Gillam's source and the AYA extractor are references, not proof of the
  Steam executable's implementation or complete format support.
- Controlled copied-runtime observations establish only the measured behavior
  and specimen described by their evidence.
- Deterministic rebuild agreement does not re-prove retail behavior or establish
  gameplay, visual, or rebuild parity.
- Retail executables, saves, debugger logs, and runtime frames remain untracked
  local inputs. Retail assets and conversions are locally materialized and
  ignored. The reviewed canonical Ghidra project and narrow save fixture are
  the explicit tracked payload exceptions.

## Start here

| Area | Canonical entry point |
| --- | --- |
| Save and options formats | [Save-file index](save-file/_index.md) |
| Retail binary analysis | [Binary-analysis index](binary-analysis/_index.md) |
| Canonical Ghidra project | [Distributable database](ghidra/README.md) |
| Pinned source references | [Source-code index](source-code/_index.md) |
| Measured mechanics | [Game-mechanics index](game-mechanics/_index.md) |
| Assets and mission data | [Game-assets index](game-assets/_index.md) |
| Compact lookups | [Quick-reference index](quick-reference/_index.md) |
| Attribution and known limits | [Project metadata](project-meta/_index.md) |

## Current static authority

- [2026-07 fullpass expedition handoff (branch status)](binary-analysis/ghidra-fullpass-expedition-handoff-2026-07-25.md)
- [Name-grading ledger — every name graded by its evidence](binary-analysis/name-grading-ledger-2026-07-25.md)
- [PhysicsScript round and weapon-mode value ids — resolved](binary-analysis/physics-round-value-ids-2026-07-25.md)
- [Direct3D fog render states — `D3DFOG_EXP` slot, parameters, and far plane](binary-analysis/d3d-fog-render-state-static-contract-2026-07-25.md)
- [Player camera attach, projection FOV, and mesh `HFOV`](binary-analysis/player-camera-attach-and-mesh-hfov-2026-07-26.md)
- [Terrain shade plane — origin, ownership, and axis order](binary-analysis/terrain-shade-plane-origin-2026-07-26.md)
- [View distance, cull, and LOD constants](binary-analysis/view-distance-and-lod-constants-2026-07-25.md)


- [2026-07-13 full Ghidra re-audit closeout](binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md)
- [Per-address reviewed correction plan](binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json)
- [2026-07 fullpass discovery findings](binary-analysis/ghidra-fullpass-findings/) (waves W001–W018)
- [Battle Engine movement crosswalk](binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md)
- [Battle Engine morph observer design](binary-analysis/battleengine-morph-runtime-observer-design-2026-07-12.md)
- [Pinned reference-submodule audit](source-code/reference-submodule-audit-2026-07-12.md)

The `6,411/6,411` closeout is a metadata/export accounting result, not a claim
that every function is semantically correct. Fullpass wave notes are discovery
evidence only; they do not claim complete semantic correctness of the database.
Current per-function notes live under
[`binary-analysis/functions/`](binary-analysis/functions/_index.md).

### 2026-07 fullpass correction expedition (authority map)

| Layer | Location | Role |
| --- | --- | --- |
| Discovery findings | [`binary-analysis/ghidra-fullpass-findings/`](binary-analysis/ghidra-fullpass-findings/) | Tracked wave reviews (W001–W018) |
| Correction ops | `local-lab/ghidra-fullpass-2026-07-23/` (gitignored) | Queues, dual QC, apply logs; closeout 2026-07-25 |
| Live applied DB | Maintainer Ghidra Projects (machine-local) | Working database that may receive dual-cleared applies |
| Tracked snapshot | [`ghidra/`](ghidra/README.md) (snapshot date 2026-07-18) | Distributable reviewed snapshot; may lag the live maintainer DB |

Host install paths, headless entry, and local project layout:
[`ghidra/README.md`](ghidra/README.md). Expedition overlays stay under ignored
`local-lab/`; do not treat discovery notes as proof that the tracked snapshot
or live DB was mutated.

## Product-facing summaries

- [Save/options boundary](public-save-options.md)
- [Assets and modding boundary](public-assets-and-modding.md)
- [Static contracts](public-static-contracts.md)

Reusable read-only Ghidra exporters, guarded asset tools, parsers, and copied-
runtime helpers live under [`tools/`](../tools/README.md). Mutation of the
installed game or original `BEA.exe` is never an RE workflow.
