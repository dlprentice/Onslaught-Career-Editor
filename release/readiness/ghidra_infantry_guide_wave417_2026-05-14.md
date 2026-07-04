# Ghidra InfantryGuide Wave417

Status: public-safe static RE evidence
Date: 2026-05-14

This note records a serialized headless Ghidra dry/apply/read-back pass for the InfantryGuide lifecycle, vtable, target-selection, and event-recheck tranche. It is public-safe: it contains addresses, saved names/signatures, command summaries, counts, and claim boundaries, but not raw decompile excerpts, private paths, screenshots, frames, copied executables, saves, or private runtime proof.

## Saved Ghidra Corrections

| Address | Saved name | Saved signature | Result |
| --- | --- | --- | --- |
| `0x0048a3c0` | `CInfantryGuide__ctor` | `void * __thiscall CInfantryGuide__ctor(void * this, void * owner_unit)` | Corrected the constructor-like label to the InfantryGuide constructor, with owner-unit stack argument and guide/monitor setup context. |
| `0x0048a4b0` | `SharedGuide__GetField24Block_0048a4b0` | `void * __fastcall SharedGuide__GetField24Block_0048a4b0(void * this)` | Created a compact shared vtable-slot helper returning the field block at `this+0x24`; both CInfantryGuide and CGroundVehicleGuide vtable evidence point here. |
| `0x0048a4c0` | `CInfantryGuide__scalar_deleting_dtor` | `void * __thiscall CInfantryGuide__scalar_deleting_dtor(void * this, byte flags)` | Corrected the generic vfunc label to a scalar-deleting destructor wrapper. |
| `0x0048a4e0` | `CInfantryGuide__dtor` | `void __fastcall CInfantryGuide__dtor(void * this)` | Hardened the destructor body signature/comment around reader unregister, owned pointer frees, and monitor shutdown. |
| `0x0048a570` | `CInfantryGuide__UpdateGuidanceState_0048a570` | `void __fastcall CInfantryGuide__UpdateGuidanceState_0048a570(void * this)` | Created the CInfantryGuide vtable slot-3 update/guidance-state body after vtable and instruction read-back found a real function boundary. |
| `0x0048ac70` | `CInfantryGuide__HandleTargetRecheckEvent` | `void __thiscall CInfantryGuide__HandleTargetRecheckEvent(void * this, void * event)` | Moved the stale `0x0048ac80` mid-body function to the true prologue at `0x0048ac70`; the body gates event id `2000`, calls target selection, and reschedules the next recheck. |
| `0x0048ace0` | `CInfantryGuide__SelectNearestTargetReader` | `void __fastcall CInfantryGuide__SelectNearestTargetReader(void * this)` | Hardened the target-reader selection helper signature/comment around nearby map-who scans, filters, and nearest-target selection. |

## Evidence Summary

- Stuart's available source snapshot does not include matching InfantryGuide source bodies, so this is retail-static Ghidra evidence rather than exact source-body confirmation.
- `0x0048ac80` is no longer a saved function entry after this wave. It is inside `CInfantryGuide__HandleTargetRecheckEvent` at the true `0x0048ac70` boundary.
- CInfantryGuide vtable `0x005dbfa8` now resolves slot `0` to `0x0048ac70`, slot `1` to `0x0048a4c0`, slot `3` to `0x0048a570`, and slot `9` to `0x0048a4b0`.
- CGroundVehicleGuide vtable evidence also points slot `9` to `0x0048a4b0`, so the helper is intentionally shared/owner-neutral.
- CInfantryGuide vtable slots `4` through `8` still point at addresses that do not yet have saved function objects in this tranche; they remain future queue work.
- Refreshed whole-project queue telemetry reports `6039` total functions, `1624` commented functions, `4415` commentless functions, `1890` undefined signatures, and `1823` `param_N` signatures. Current confirmation proxies are comment-backed `1624/6039 = 26.89%` and strict clean-signature `1561/6039 = 25.85%`; both are telemetry only, not milestones.

## Validation

- Focused tests: `py -3 tools\ghidra_infantry_guide_wave417_probe_test.py` passed `4/4`.
- Python compile: `py -3 -m py_compile tools\ghidra_infantry_guide_wave417_probe.py tools\ghidra_infantry_guide_wave417_probe_test.py` passed.
- Headless dry run: `ApplyInfantryGuideWave417.java dry` reported `updated=0 skipped=5 created=0 would_create=2 boundary_moved=0 would_boundary_move=1 renamed=0 would_rename=3 missing=0 bad=0` with `REPORT: Save succeeded`.
- Headless apply run: `ApplyInfantryGuideWave417.java apply` reported `updated=7 skipped=0 created=2 would_create=0 boundary_moved=1 would_boundary_move=0 renamed=2 would_rename=0 missing=0 bad=0` with `REPORT: Save succeeded`.
- Read-back exports verified `7` metadata rows plus one missing stale `0x0048ac80` guard, `7` tag rows, `9` xref rows, `1183` instruction rows, `7` decompile exports, and `32` vtable-slot rows across the checked CInfantryGuide and CGroundVehicleGuide vtable contexts.
- Package wrapper: `cmd.exe /c npm run test:ghidra-infantry-guide-wave417` passed with focused probe status `PASS`.
- Queue refresh: headless `ExportFunctionQualitySnapshot.java` and `py -3 tools\ghidra_static_reaudit_queue_probe.py --check --json` passed with the `6039`-function telemetry above.
- Actual Ghidra project backup: copied `BEA.gpr` and `BEA.rep` to `[maintainer-local-ghidra-backup-root]\BEA_20260514_131457_post_wave417_infantry_guide_verified` and verified `19` files, `154962823` bytes, and `HashDiffCount=0`.

## Not Proven

This tranche does not prove runtime InfantryGuide target selection, runtime movement/guidance behavior, exact source-body identity, concrete InfantryGuide or target-entry layouts, local-variable/type recovery, CInfantryGuide vtable slots `4` through `8`, BEA launch behavior, game patching, packaged app behavior, or rebuild parity.
