# Source-to-binary crosswalk — gold-set calibration

Status: active
Date: 2026-08-22

Summary: all 1164 function definitions in the pinned `references/Onslaught` sources classified against the pristine retail specimen: 136 SOURCE_EXACT (11.7%), 337 SOURCE_ANALOG (29.0%), 651 NO_MATCH_FOUND (55.9%), 40 NOT_IN_RETAIL (3.4%).

Evidence: MEASURED — every row is a mechanical join between the pinned sources and tracked binary-side evidence (function-name table, per-function notes, evidence register, semantics TSVs); each SOURCE_EXACT/SOURCE_ANALOG row cites repo-relative evidence paths verified to exist, and every SOURCE_EXACT row carries a retail VA with no two EXACT rows sharing one.

Specimen: `BEA.exe.original.backup`, SHA-256 `74154bfa…e1e7750`, 2,506,752 bytes (verified by hash before the sweep; pristine read-only, no Ghidra session was opened, no byte of any binary was written).

## What this is

The systematic file-by-file crosswalk between Stuart Gillam's pinned reference sources (`references/Onslaught/`, read-only) and the shipped retail executable that did not previously exist. Per-function rows live in [`crosswalk.tsv`](crosswalk.tsv); this report summarizes coverage and method.

## Classification contract

| Class | Meaning | Gate applied mechanically |
| --- | --- | --- |
| `SOURCE_EXACT` | Binary-side name evidence identifies this exact function AND tracked evidence asserts source-body agreement. | Exact candidate name in the tracked name table (or a tracked note anchored to this source location) PLUS one of: a function note whose `Verified vs Source:` starts with "Yes", an exact source-line note anchor (±6 lines), or a same-VA semantics-TSV row whose `semantic_status` asserts body agreement (`SOURCE_BODY/INLINE/MACRO`, no `DIVERGENCE`). |
| `SOURCE_ANALOG` | A binary-side candidate exists but nothing tracked asserts source-body agreement. | Name-table hit without an EXACT gate, a CamelCase-prefix candidate (analog ceiling by construction), or note-only evidence. |
| `NO_MATCH_FOUND` | No binary-side evidence found under any candidate name. | Absent from the name table under exact, prefix, and variant candidates; no tracked note. |
| `NOT_IN_RETAIL` | Positive evidence retail lacks it. | Definition inside an `#if TARGET == XBOX` (or equivalent XBOX-guarded) region with no binary-side evidence. |

Known parser limits (honest negatives, each mechanically enforced):

- Candidate generation is name-shape based. A source function whose retail name differs beyond prefix-truncation (renames, merges, splits) lands in `NO_MATCH_FOUND` even when its body was compiled in.
- `NO_MATCH_FOUND` never asserts absence from the binary; only `NOT_IN_RETAIL` does, and only from Xbox-guard evidence.
- Header-defined inline functions (`*.h`) are inventoried but rarely carry separate retail symbols; their rows are dominated by `NO_MATCH_FOUND`.
- The parser rejects control-flow-led lines and ALL-CAPS macro invocations; multi-line signatures are joined.

## Per-file coverage

| File | Defs | EXACT | ANALOG | NO_MATCH | NOT_IN_RETAIL | EXACT+ANALOG |
| --- | --- | --- | --- | --- | --- | --- |
| `Array.h` | 2 | 0 | 0 | 2 | 0 | 0 (0%) |
| `BattleEngine.cpp` | 114 | 1 | 40 | 73 | 0 | 41 (36%) |
| `BattleEngine.h` | 2 | 0 | 0 | 2 | 0 | 0 (0%) |
| `BattleEngineConfigurations.cpp` | 5 | 0 | 0 | 5 | 0 | 0 (0%) |
| `BattleEngineDataManager.cpp` | 8 | 0 | 3 | 5 | 0 | 3 (38%) |
| `BattleEngineDataManager.h` | 25 | 0 | 0 | 25 | 0 | 0 (0%) |
| `BattleEngineJetPart.cpp` | 39 | 0 | 25 | 14 | 0 | 25 (64%) |
| `BattleEngineWalkerPart.cpp` | 41 | 0 | 26 | 15 | 0 | 26 (63%) |
| `CLIParams.cpp` | 3 | 0 | 0 | 3 | 0 | 0 (0%) |
| `Camera.cpp` | 47 | 0 | 20 | 27 | 0 | 20 (43%) |
| `Career.cpp` | 41 | 20 | 6 | 15 | 0 | 26 (63%) |
| `Controller.cpp` | 18 | 10 | 3 | 5 | 0 | 13 (72%) |
| `Controller.h` | 4 | 0 | 0 | 4 | 0 | 0 (0%) |
| `DXEngine.cpp` | 23 | 2 | 5 | 13 | 3 | 7 (30%) |
| `DXEngine.h` | 1 | 0 | 0 | 1 | 0 | 0 (0%) |
| `DXFrontend.cpp` | 4 | 0 | 1 | 3 | 0 | 1 (25%) |
| `DXGame.cpp` | 2 | 0 | 0 | 2 | 0 | 0 (0%) |
| `DXMemBuffer.cpp` | 19 | 6 | 1 | 12 | 0 | 7 (37%) |
| `DXMemoryManager.cpp` | 17 | 5 | 5 | 6 | 1 | 10 (59%) |
| `DXMemoryManager.h` | 2 | 0 | 0 | 2 | 0 | 0 (0%) |
| `EditorD3DApp.cpp` | 17 | 0 | 0 | 17 | 0 | 0 (0%) |
| `EndLevelData.cpp` | 2 | 0 | 1 | 1 | 0 | 1 (50%) |
| `FEPGoodies.cpp` | 38 | 0 | 12 | 26 | 0 | 12 (32%) |
| `FEPGoodies.h` | 1 | 0 | 0 | 1 | 0 | 0 (0%) |
| `FEPLoadGame.cpp` | 8 | 0 | 5 | 3 | 0 | 5 (62%) |
| `FEPSaveGame.cpp` | 12 | 0 | 8 | 4 | 0 | 8 (67%) |
| `FrontEnd.cpp` | 38 | 0 | 25 | 13 | 0 | 25 (66%) |
| `InitThing.cpp` | 18 | 0 | 0 | 18 | 0 | 0 (0%) |
| `InitThing.h` | 32 | 0 | 0 | 32 | 0 | 0 (0%) |
| `MemoryCard.cpp` | 1 | 0 | 0 | 1 | 0 | 0 (0%) |
| `MemoryCard.h` | 1 | 0 | 0 | 1 | 0 | 0 (0%) |
| `MemoryManager.cpp` | 39 | 0 | 19 | 20 | 0 | 19 (49%) |
| `MemoryManager.h` | 4 | 0 | 0 | 4 | 0 | 0 (0%) |
| `Music.cpp` | 27 | 5 | 4 | 18 | 0 | 9 (33%) |
| `Music.h` | 2 | 0 | 0 | 2 | 0 | 0 (0%) |
| `PCController.cpp` | 8 | 0 | 6 | 2 | 0 | 6 (75%) |
| `PCEngine.cpp` | 18 | 0 | 0 | 18 | 0 | 0 (0%) |
| `PCFrontend.cpp` | 6 | 0 | 0 | 6 | 0 | 0 (0%) |
| `PCGame.cpp` | 3 | 0 | 0 | 3 | 0 | 0 (0%) |
| `PCMemoryCard.cpp` | 1 | 0 | 0 | 1 | 0 | 0 (0%) |
| `PCMemoryCard.h` | 14 | 0 | 0 | 14 | 0 | 0 (0%) |
| `PCPlatform.cpp` | 32 | 0 | 7 | 25 | 0 | 7 (22%) |
| `PCPlatform.h` | 1 | 0 | 0 | 1 | 0 | 0 (0%) |
| `Platform.cpp` | 1 | 0 | 0 | 1 | 0 | 0 (0%) |
| `Player.cpp` | 18 | 1 | 11 | 6 | 0 | 12 (67%) |
| `ResourceAccumulator.cpp` | 9 | 0 | 0 | 9 | 0 | 0 (0%) |
| `SPtrSet.cpp` | 12 | 0 | 0 | 12 | 0 | 0 (0%) |
| `SoundManager.cpp` | 48 | 26 | 3 | 19 | 0 | 29 (60%) |
| `SoundManager.h` | 3 | 0 | 0 | 3 | 0 | 0 (0%) |
| `XBoxMemoryCard.cpp` | 36 | 0 | 0 | 0 | 36 | 0 (0%) |
| `activereader.cpp` | 1 | 0 | 1 | 0 | 0 | 1 (100%) |
| `actor.cpp` | 19 | 0 | 10 | 9 | 0 | 10 (53%) |
| `chunker.cpp` | 17 | 0 | 5 | 12 | 0 | 5 (29%) |
| `d3dapp.cpp` | 17 | 0 | 11 | 6 | 0 | 11 (65%) |
| `engine.cpp` | 34 | 1 | 15 | 18 | 0 | 16 (47%) |
| `event.cpp` | 1 | 0 | 0 | 1 | 0 | 0 (0%) |
| `eventmanager.cpp` | 14 | 8 | 0 | 6 | 0 | 8 (57%) |
| `game.cpp` | 77 | 38 | 23 | 16 | 0 | 61 (79%) |
| `game.h` | 3 | 0 | 0 | 3 | 0 | 0 (0%) |
| `ltshell.cpp` | 43 | 0 | 1 | 42 | 0 | 1 (2%) |
| `ltshell.h` | 2 | 0 | 0 | 2 | 0 | 0 (0%) |
| `pcsoundmanager.cpp` | 17 | 11 | 2 | 4 | 0 | 13 (76%) |
| `pcsoundmanager.h` | 2 | 0 | 0 | 2 | 0 | 0 (0%) |
| `scheduledevent.cpp` | 2 | 2 | 0 | 0 | 0 | 2 (100%) |
| `thing.cpp` | 47 | 0 | 33 | 14 | 0 | 33 (70%) |
| `thing.h` | 1 | 0 | 0 | 1 | 0 | 0 (0%) |

## Priority files (brief card-gold-calibration.md)

| File | Defs | EXACT | ANALOG | NO_MATCH | NOT_IN_RETAIL |
| --- | --- | --- | --- | --- | --- |
| `Career.cpp` | 41 | 20 | 6 | 15 | 0 |
| `game.cpp` | 77 | 38 | 23 | 16 | 0 |
| `BattleEngine.cpp` | 114 | 1 | 40 | 73 | 0 |
| `actor.cpp` | 19 | 0 | 10 | 9 | 0 |

## Method and instruments

1. Inventory: a conservative C++ definition parser (comment/string stripping, brace-balanced signature joining, definition-vs-declaration discrimination, macro/call-site rejection) enumerated every function definition in the 109 reference files: 1164 rows.
2. Evidence join, cheapest authority first: tracked function-name table (8,329 named retail functions, specimen-bound), 752 per-function RE notes (122 with explicit `references/Onslaught` anchors), the Generation-31 evidence register, and the 2026-08-11 semantics/vtable TSVs with `source_anchor` columns.
3. Classification gates as tabled above; the sweep and the audit are mechanical and re-runnable (lane tools in `local-lab/hermes-kanban-campaign-2026-08-22/source-crosswalk/`, untracked).
4. Audit gate (all green): every cited evidence path exists; every SOURCE_EXACT row has a retail VA; no two EXACT rows share a VA; row count equals the inventoried definition count (1164).

## What this settles — and what it does not

Settled: which pinned-source functions have a named retail counterpart with tracked source-body-agreement evidence (136 rows), which have a named candidate without that strength (337), which are positively Xbox-only (40), and which remain open (651) with a per-row falsifier: search the pristine bytes and the live name projection for renamed/merged/split bodies.

Not settled: body-level equivalence for `SOURCE_ANALOG` rows; the `NO_MATCH_FOUND` set is a search frontier, not a proof of absence; runtime behavior is out of scope for this static pass.

## Receipt

- crosswalk.tsv rows: 1164; inventoried source definitions: 1164; equal.
- SOURCE_EXACT 136 / SOURCE_ANALOG 337 / NO_MATCH_FOUND 651 / NOT_IN_RETAIL 40.
- Audit: 0 missing evidence paths, 0 EXACT rows without VA, 0 EXACT VA collisions.
