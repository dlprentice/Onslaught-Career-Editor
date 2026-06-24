# PhysicsScript Schema/Parser Proof Plan

Status: active public-safe proof plan, not runtime proof
Last updated: 2026-06-08
Scope: PhysicsScript schema/parser planning from the saved static contract

This plan is the next selected slice from `roadmap/static-to-proof-rebuild-transition-backlog.md` after the texture/mesh copied-corpus and material sidecar proof results. It converts the static `physics-script-static-contract.md` evidence into a parser/spec checklist and copied-corpus requirement list. It does not launch BEA, mutate Ghidra, mutate the installed game, parse private corpus bytes in committed output, start visual QA, start Godot work, or claim rebuild parity.

Follow-up result: `physics-script-copied-corpus-parser-proof.md` implements the copied-corpus shallow parser/census proof for `data/default physics.dat`. It proves stream framing and aggregate record counts only, not runtime behavior, serialized completeness, exact layouts, complete nested enum semantics, or rebuild parity.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

The percentage front door remains `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and `reverse-engineering/binary-analysis/static-reaudit-progress.json`. This proof plan does not create a new static RE percentage.

Primary static contract source: `reverse-engineering/binary-analysis/physics-script-static-contract.md`, tag `physics-script-static-contract-wave1103`.

Relevant retained evidence:

- Manager rows: `5` rows covering `CPhysicsScript__Create`, `CPhysicsScript__Destroy`, `CPhysicsScript__Load`, `CPhysicsScript__Update`, and `CPhysicsScript__CreateStatement`.
- Top-level statement families: `9` observed type ids, `1..9`.
- Statement/value-list load rows: `18` rows from Wave1043.
- Create/recurse rows: `9` rows from Wave1047.
- Wave1169 loader-tail current-risk review: `12` rows, `30` xref rows, and `1134` instruction rows.
- Wave1183 value-list/registry/lifetime current-risk review: `21` rows, `120` xref rows, `404` instruction rows, and `21` decompile rows.
- Wave1203 registry/apply residual current-risk review: `7` rows, `10` xref rows, `902` instruction rows, and `7` decompile rows.

## Static Parser Anchors

The proof plan is built around the saved Ghidra contract, not source guesses:

| Surface | Static anchor |
| --- | --- |
| Manager load | `0x0042e950 CPhysicsScript__Load` reads stream header/token value `0x12`, loops statement type ids until `-1`, creates statements, invokes load slot `+0xc`, and skips unknown payload bytes when creation returns null. |
| Statement factory | `0x0042eb90 CPhysicsScript__CreateStatement` dispatches observed top-level statement type ids `1..9`, allocates `0x110` byte statement objects, initializes common fields, and returns null outside the known range. |
| Nested factories | `CPhysicsScriptStatements__CreateStatementType2` through `CPhysicsScriptStatements__CreateStatementType10` are the saved nested factory anchors in the current static contract; future parser evidence may discover or reject additional value ids without promoting them to complete semantic enums. |
| Load rows | `CUnitStatement__LoadFromMemBuffer` through `CPhysicsHazardValueList__LoadFromMemBuffer` cover the `18` paired statement/value-list loader rows. |
| Create/recurse | `CUnitStatement__CreateUnitAndRecurse` through `CHazardStatement__CreateHazardAndRecurse` cover the `9` create/recurse rows and `CStatementChain__InvokeVFunc04OnNodes`. |
| Registry roots | `DAT_008553f4`, `DAT_008553f8`, `DAT_00855400`, `DAT_00855404`, `DAT_00855408`, and `DAT_008553fc` bind statement creation/apply paths to default-record lists. |
| Lifetime | Statement child/list pointer `+0x10c`, base statement vtable `0x005d9894`, and `CDXMemoryManager__Free(&DAT_009c3df0, this)` value-list/leaf free patterns bound ownership planning without proving concrete serialized layouts. |

## Parser Proof Checklist

The first implementation artifact should be a read-only parser/spec checker that consumes copied/app-owned script/resource evidence and emits public-safe aggregates only.

| Row | Planned proof item | Required evidence | Public-safe result |
| --- | --- | --- | --- |
| 1 | Corpus census | Enumerate copied data/resource roots for PhysicsScript binary payload candidates, including the private copied `data/default physics.dat` file shape. | File count, byte count, and hash summary in private evidence; only sanitized filename/count totals in public docs. |
| 2 | Stream framing | Validate the `0x12` stream header/token, top-level statement loop, and `-1` terminator behavior against copied bytes. | Aggregate pass/fail, byte-consumption totals, and exact stop reason. |
| 3 | Top-level statement ids | Count observed top-level ids against the static factory ids `1..9`; preserve unknown ids as raw/skipped records instead of rejecting them by default. | Counts by type id and unknown/skipped id count. |
| 4 | Loader/value-list pairing | Tie top-level ids to the `18` statement/value-list loader rows and record which payload regions are parsed, raw-preserved, or skipped. | Counts by statement family and value-list family. |
| 5 | Nested factory/value ids | Record nested `CPhysicsScriptStatements__CreateStatementType*` dispatch ids as observed values, not complete semantic enums. | Counts by nested factory/value id and unknown-value payload bytes. |
| 6 | String/scalar observations | Record bounded observations for strings, scalar widths, zero/nonzero flag offsets, and obvious list lengths only when byte-consumption evidence supports them. | Provisional schema fields and unknown-field byte ranges. |
| 7 | Recursive structure | Track maximum nesting depth, child-chain count, and parent/child byte ranges without promoting exact C++ object layout. | Aggregate hierarchy shape only. |
| 8 | Raw preservation | Preserve raw byte slices for unknown or layout-sensitive payloads in ignored private evidence. | Public docs report byte counts, not raw data. |
| 9 | Boundary check | Probe rejects runtime, mission-outcome, exact-layout, patching, Godot, rebuild, and no-noticeable-difference wording. | No mission outcome or serialized completeness claim until corpus proof exists. |

## Corpus Requirement List

Required copied/app-owned inputs:

- A copied/private PhysicsScript binary corpus candidate, including `data/default physics.dat` where present. Current private/copy roots show this file shape at `175603` bytes; raw bytes, strings, AST dumps, and absolute paths stay out of public git.
- A copied data-root/resource census that records exact file spelling. Use `default physics.dat` when the copied file uses that spelling; treat older `default_physics.dat` wording as a possible doc/source alias until a census proves otherwise.
- A manifest of every PhysicsScript candidate file found under copied/app-owned data roots, with file size and SHA-256 stored in ignored evidence.
- A public-safe synthetic fixture for parser edge tests. Synthetic fixtures can test parser failures and unknown-skip paths, but they never prove retail corpus coverage.

Out-of-corpus boundaries:

- `MissionScripts/*.msl` are MissionScript text inputs, not PhysicsScript binary parser input.
- Stuart source can explain architecture and names, but it is not parser authority for retail bytes.
- Runtime-generated memory, save files, screenshots, frames, and patched executables are outside this parser proof plan.

## Not Claimed

This plan is a Schema/parser proof checklist and corpus requirement list only. It proves planning readiness for copied/app-owned script/resource evidence.

It does not prove:

- Runtime PhysicsScript behavior.
- MissionScript or resource-script outcome behavior.
- Serialized physics-script file-format completeness.
- Exact statement/value-list/concrete record layouts.
- Exact source-body identity.
- Gameplay outcomes.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

No mission outcome or serialized completeness claim until corpus proof exists.

No runtime PhysicsScript behavior, exact layouts, mission/resource-script outcomes, BEA patching behavior, rebuild parity, or no-noticeable-difference parity claim.

## Exit Gate For This Planning Slice

This planning slice is complete only when:

- This document and its lore-book mirror match.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `reverse-engineering/binary-analysis/_index.md`, and `reverse-engineering/RE-INDEX.md` point to this plan.
- `release/readiness/physics_script_schema_parser_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/physics_script_schema_parser_proof_plan_probe.py --check` passes.
- `tools/physics_script_static_contract_probe.py --check` passes with current `6411/6411` and Wave1203 contract context.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.

After that, the next executable slice can build the copied-corpus parser/census under an ignored/app-owned output root such as `subagents/physics_script_schema_parser_proof_2026-06-08/`.
