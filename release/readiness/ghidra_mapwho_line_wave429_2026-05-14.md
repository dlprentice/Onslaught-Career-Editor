# Ghidra CMapWho Wave429 Line Query Static Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-14
Scope: saved retail `BEA.exe` Ghidra signature/comment/tag correction

## Summary

Wave429 serialized headless dry/apply/read-back hardened thirteen saved `CMapWho` / `CMapWhoEntry` functions at `0x00492110` through `0x00492ca0`. The pass covered the line-query iterator helpers, world-to-sector conversion, sector sorting, debug draw helpers, and entry position/owner helpers after Wave428 handled the neighboring init/radius-query cluster.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof. The retail debug string names `[maintainer-local-source-export-root]\mapwho.cpp`, but `mapwho.cpp` is absent from the current Stuart source snapshot, so this wave is binary-led rather than source-body parity.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x00492110` | `void * __thiscall CMapWho__GetFirstEntryWithinLine(void * this, float line_start_x, float line_start_y, float line_start_z, float line_start_w, float line_end_x, float line_end_y, float line_end_z, float line_end_w)` | `RET 0x20`; clips a line, stores start/end context, and seeds the line-query iterator. |
| `0x004922f0` | `int __fastcall CMapWho__SetupLineLevel(void * this)` | Sets up the current line level, major axis, step deltas, sample budget, and sector seed. |
| `0x004924b0` | `int __fastcall CMapWho__AdvanceLineIterator(void * this)` | Advances the line iterator through perpendicular probes and sample steps, returning `0` when exhausted. |
| `0x004925a0` | `void * __fastcall CMapWho__GetNextEntryWithinLine(void * this)` | Continues an active line query and warns when called before setup. |
| `0x00492670` | `void * __thiscall CMapWho__WorldToSector(void * this, void * sector_coord, void * position, int level)` | `RET 0xc`; rounds/clamps x/y by level metadata and returns the output sector pointer through `EAX`. |
| `0x004926e0` | `void __fastcall CMapWho__Sort(void * this)` | Walks level grids, validates sector coordinates, and moves entries with owner flag `0x2000000` toward sector tails. |
| `0x00492860` | `void __thiscall CMapWho__DebugDrawSector(void * this, int packed_sector_coord, int level)` | `RET 0x8`; unpacks sector x/y and draws a debug volume with level-specific color. |
| `0x00492950` | `void __fastcall CMapWho__DebugDraw(void * this)` | Iterates sectors, filters via `CMapWhoEntry__GetOwner`, and calls the sector debug draw helper. |
| `0x00492ba0` | `void __thiscall CMapWhoEntry__SetPosition(void * this, void * position, void * owner, float explicit_radius)` | `RET 0xc`; derives radius, selects a level, converts position to sector fields, and adds the entry to the global mapwho singleton. |
| `0x00492c60` | `void __fastcall CMapWhoEntry__Invalidate(void * entry)` | Marks the entry level field at `+0x0c` as invalid. |
| `0x00492c70` | `void __fastcall CMapWhoEntry__RemoveFromMap(void * entry)` | Removes a valid entry from the global mapwho singleton. |
| `0x00492c90` | `void * __fastcall CMapWhoEntry__GetOwner(void * entry)` | Returns the owning object pointer as `entry - 0x0c`. |
| `0x00492ca0` | `int __thiscall CMapWhoEntry__UpdatePosition(void * this, void * position)` | `RET 0x4`; recomputes sector fields, returns `0` when unchanged, otherwise removes/re-adds the entry and returns `1`. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 tools\ghidra_mapwho_line_wave429_probe_test.py` before implementation | FAIL, expected red | Missing probe module. |
| `py -3 tools\ghidra_mapwho_line_wave429_probe_test.py` | PASS | Focused tests passed `4/4`. |
| Headless `ApplyMapWhoLineWave429.java` dry run | PASS | `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`; dry logic made no metadata mutation. |
| Headless `ApplyMapWhoLineWave429.java` apply | PASS after read-back correction | Final apply reported `updated=13 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. A first apply exposed a `__thiscall` hidden-`this` read-back nuance on two entry methods; the script/probe were corrected and rerun serially. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `13` metadata rows, `13` tag rows, `57` xref rows, `5473` instruction rows, and `13` target decompile exports. |
| `cmd.exe /c npm run test:ghidra-mapwho-line-wave429` | PASS | Focused probe accepted saved signatures, comments, tags, xrefs, instruction terminators, and proof-boundary wording. |
| `py -3 -m py_compile tools\ghidra_mapwho_line_wave429_probe.py tools\ghidra_mapwho_line_wave429_probe_test.py` | PASS | Both focused Python files compile. |
| Headless whole-database quality snapshot | PASS | `total_functions=6043`; `commented_functions=1717`. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6043` functions, `4326` commentless functions, `1833` undefined signatures, `1792` `param_N` signatures, and zero broad uncertain/helper/wrapper debt. |
| Live Ghidra project backup | PASS | Private post-mutation backup verified `19` files, `155356039` bytes, `MissingCount=0`, and `HashDiffCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue now reports:

- Total function objects: `6043`
- Functions with non-empty function comments: `1717`
- Commentless function objects: `4326`
- `undefined` signatures: `1833`
- Signatures still using `param_N`: `1792`
- Comment-backed telemetry proxy: `1717/6043 = 28.41%`
- Strict clean-signature telemetry proxy: `1655/6043 = 27.39%`

These are triage proxies only. They are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime line-query behavior, runtime entry tracking behavior, runtime debug rendering behavior, exact concrete `CMapWho` or `CMapWhoEntry` layout beyond observed offsets, exact local variable names/types, exact source-body identity, source-to-retail rebuild parity, BEA launch behavior, game patching, or runtime gameplay behavior.
