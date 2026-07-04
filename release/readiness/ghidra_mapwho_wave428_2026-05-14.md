# Ghidra CMapWho Wave428 Static Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-14
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave428 serialized headless dry/apply/read-back hardened twelve saved `CMapWho` / `CMapWhoEntry` spatial-query functions at `0x00491900` through `0x00492020`. The pass corrected the over-specific `CCollisionSeekingRound` owner labels for two generic MapWho iterator helpers, narrowed one bounds helper name from entry wording to sector-coordinate wording, renamed the radius-level setup helper for clarity, and replaced `undefined` / `param_N` signature debt with proof-boundary comments and tags.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof. The retail debug string names `[maintainer-local-source-export-root]\mapwho.cpp`, but `mapwho.cpp` is absent from the current Stuart source snapshot, so this wave is binary-led rather than source-body parity.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x00491900` | `void __fastcall CMapWhoEntry__Init(void * entry)` | `RET` with no stack cleanup; clears entry next/previous links. |
| `0x00491930` | `void __fastcall CMapWho__Destroy(void * this)` | `RET` with no stack cleanup; destroys/frees level arrays under `+0x90` and clears the pointer. |
| `0x004919b0` | `void __fastcall CMapWho__Init(void * this)` | Allocates five level arrays from `64x64` down to `4x4`, stores level metadata, links child sector groups, and carries the construction-warning context. |
| `0x00491c50` | `int __thiscall CMapWho__GetLevelForRadius(void * this, float radius)` | `RET 0x4`; selects a level from radius and scale-adjusted cell sizes, with too-large warning context. |
| `0x00491cd0` | `void __thiscall CMapWho__AddEntry(void * this, void * entry)` | `RET 0x4`; inserts an entry into the sector linked-list head under the level table. |
| `0x00491d20` | `void __thiscall CMapWho__RemoveEntry(void * this, void * entry)` | `RET 0x4`; unlinks next/previous entry pointers and updates the sector head when needed. |
| `0x00491d80` | `void * __thiscall CMapWho__SetIteratorFromSectorHead(void * this, void * sector_entry)` | Corrected from the stale collision-specific owner; xrefs include collision, dynamic-unit rendering, and tree geometry. |
| `0x00491d90` | `void * __fastcall CMapWho__AdvanceIteratorAndGetCurrent(void * this)` | Corrected from the stale collision-specific owner; advances the shared iterator through the current entry next pointer. |
| `0x00491da0` | `int __stdcall CMapWho__IsSectorCoordInBounds(void * sector_coord)` | `RET 0x4`; validates level `0..4` and sector x/y bounds against `64 >> (4 - level)`. |
| `0x00491df0` | `int __fastcall CMapWho__SetupNextRadiusLevel(void * this)` | Renamed from generic setup wording; decrements the active radius-query level and computes sector bounds from query radius. |
| `0x00491ea0` | `void * __thiscall CMapWho__GetFirstEntryWithinRadius(void * this, float query_x, float query_y, float query_z, float query_w, float radius)` | `RET 0x14`; seeds radius-query state and returns the first non-null sector entry found. |
| `0x00492020` | `void * __fastcall CMapWho__GetNextEntryWithinRadius(void * this)` | Continues an active radius-query iterator, warning when called before setup. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 tools\ghidra_mapwho_wave428_probe_test.py` | PASS | Focused tests passed `4/4` after the expected initial missing-module red test. |
| Pre-apply `py -3 tools\ghidra_mapwho_wave428_probe.py --check` | FAIL, expected red | Probe rejected missing post-apply artifacts before saved Ghidra apply/read-back existed. |
| Headless `ApplyMapWhoWave428.java` dry run | PASS | `updated=0 skipped=12 renamed=0 would_rename=4 missing=0 bad=0`, with `REPORT: Save succeeded`; dry logic made no metadata mutation. |
| Headless `ApplyMapWhoWave428.java` apply | PASS | `updated=12 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `12` metadata rows, `12` tag rows, `62` xref rows, `2652` instruction rows, `12` target decompile exports, and `7` caller decompile exports. |
| `cmd.exe /c npm run test:ghidra-mapwho-wave428` | PASS | Focused probe accepted saved signatures, comments, tags, xrefs, instruction terminators, and proof-boundary wording. |
| `py -3 -m py_compile tools\ghidra_mapwho_wave428_probe.py tools\ghidra_mapwho_wave428_probe_test.py` | PASS | Both focused Python files compile. |
| Headless whole-database quality snapshot | PASS | `total_functions=6043`; `commented_functions=1704`. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6043` functions, `4339` commentless functions, `1846` undefined signatures, `1792` `param_N` signatures, and zero broad uncertain/helper/wrapper debt. |
| Live Ghidra project backup | PASS | Private post-mutation backup verified `19` files, `155290503` bytes, `MissingCount=0`, and `HashDiffCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue now reports:

- Total function objects: `6043`
- Functions with non-empty function comments: `1704`
- Commentless function objects: `4339`
- `undefined` signatures: `1846`
- Signatures still using `param_N`: `1792`
- Comment-backed telemetry proxy: `1704/6043 = 28.20%`
- Strict clean-signature telemetry proxy: `1642/6043 = 27.17%`

These are triage proxies only. They are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime spatial-query behavior, runtime collision/render/tree query behavior, exact concrete `CMapWho` or `CMapWhoEntry` layout beyond observed offsets, exact local variable names/types, exact source-body identity, source-to-retail rebuild parity, BEA launch behavior, game patching, or runtime gameplay behavior.
