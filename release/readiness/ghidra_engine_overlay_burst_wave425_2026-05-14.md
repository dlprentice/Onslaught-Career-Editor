# Ghidra Engine Burst Overlay Wave425 Static Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-14
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave425 serialized headless dry/apply/read-back corrected and hardened six engine burst-overlay helper functions from `0x00490220` through `0x00490780`. The pass replaces two older generic helper labels, tightens three calling conventions that were leaking decompiler artifacts into callers, and records comments/tags for the candidate-list and active-overlay-slot flow used by the engine render tail.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Previous saved state | Current saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x00490220` | `CEngine__ClearNearbyProjectileBurstSlots` | `void __fastcall CEngine__ClearBurstOverlaySlotPayloads(void * burst_overlay_state)` | Clears six active overlay slot payload blocks with a `0x74` stride under the engine `+0x18` burst-overlay state. |
| `0x00490280` | `CEngine__ResetBurstTrackingState` | `int __fastcall CEngine__ResetBurstOverlayState(void * burst_overlay_state)` | Resets candidate count `+0x1c0`, clears `0xae` dwords from `+0x1c4`, and returns `1` for the `CEngine__Init` success gate. |
| `0x004902b0` | `CEngine__TrackBurstEventIfNearby` with generic/incorrect signature debt | `void __thiscall CEngine__TrackBurstEventIfNearby(void * this, void * position, void * gamut, int burst_type, float intensity_scale)` | `CEngine__TrackBurstEventFromPreset` passes engine `+0x18` state, a position pointer, engine `+0x470` gamut pointer, and two burst parameters. Body evidence gates candidates below `16`, computes nearest global tracker distance, appends a `0x1c` candidate record, and scales intensity. |
| `0x004903a0` | `CDXEngine__BuildOverlaySlotFromSortedEntry` with an extra decompiler argument | `void __thiscall CDXEngine__BuildOverlaySlotFromSortedEntry(void * this, int slot_index, int candidate_index)` | `RET 0x8` proves two stack arguments; the helper builds one active overlay slot from a sorted candidate, samples static-shadow height, mirrors slot payload into `DAT_009c65c0`, and marks overlay dirty/enabled flags. |
| `0x004905f0` | `CDXEngine__UpdateOverlaySlotsFromCandidateList` with generic `param_1` debt | `void __fastcall CDXEngine__UpdateOverlaySlotsFromCandidateList(void * burst_overlay_state)` | ECX-only update decays six active overlay slots, mirrors payloads into global render-state tables, ranks active slots/new candidates through `Sort__QuickSortGeneric`, calls the slot builder, and clears candidate count. |
| `0x00490780` | `CDXEngine__SetOverlaySlotsEnabledForActiveViews` with an extra decompiler argument | `void __thiscall CDXEngine__SetOverlaySlotsEnabledForActiveViews(void * this, int enabled)` | `RET 0x4` proves one stack argument; the helper toggles global overlay enable flags, scans active slot flags at `+0x1cc` with a `0x74` stride, and marks matching render-state slots dirty. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 tools\ghidra_engine_overlay_burst_wave425_probe_test.py` | PASS | Focused tests passed `5/5`. |
| `py -3 -m py_compile tools\ghidra_engine_overlay_burst_wave425_probe.py tools\ghidra_engine_overlay_burst_wave425_probe_test.py` | PASS | Both focused Python files compile. |
| Pre-apply `cmd.exe /c npm run test:ghidra-engine-overlay-burst-wave425` | FAIL, expected red | Probe rejected the missing post-apply artifacts before saved Ghidra apply/read-back existed. |
| Headless `ApplyEngineOverlayBurstWave425.java` dry run | PASS | `updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=2 missing=0 bad=0`, with `REPORT: Save succeeded`; dry logic made no metadata mutation. |
| Headless `ApplyEngineOverlayBurstWave425.java` apply | PASS | `updated=6 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `6` metadata rows, `6` tag rows, `6` xref rows, `1614` instruction rows, `6` target decompile exports, and `4` caller decompile exports. |
| Post-apply `cmd.exe /c npm run test:ghidra-engine-overlay-burst-wave425` | PASS | Focused probe accepted the saved names, signatures, comments, tags, caller read-back, and proof-boundary wording. |
| Headless whole-database quality snapshot | PASS | `total_functions=6043`; `commented_functions=1677`. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6043` functions, `4366` commentless functions, `1861` undefined signatures, `1803` `param_N` signatures, and zero broad uncertain/helper/wrapper debt. |
| Live Ghidra project backup | PASS | Private post-mutation backup verified `19` files, `155192199` bytes, `HashDiffCount=0`, `MissingCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue now reports:

- Total function objects: `6043`
- Functions with non-empty function comments: `1677`
- Commentless function objects: `4366`
- `undefined` signatures: `1861`
- Signatures still using `param_N`: `1803`
- Comment-backed telemetry proxy: `1677/6043 = 27.75%`
- Strict clean-signature telemetry proxy: `1612/6043 = 26.68%`

These are triage proxies only. They are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime overlay rendering, runtime projectile/burst behavior, exact player-view semantics, exact concrete state layout, exact local variable names/types, source-to-retail rebuild parity, BEA launch behavior, game patching, or runtime gameplay behavior.
