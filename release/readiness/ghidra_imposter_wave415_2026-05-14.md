# Ghidra CImposter Frame Metadata Wave415

Status: public-safe static RE evidence
Date: 2026-05-14

This note records a serialized headless Ghidra dry/apply/read-back pass for the CImposter imposter/frame helper tranche. It is public-safe: it contains addresses, saved names/signatures, command summaries, counts, and claim boundaries, but not raw decompile excerpts, private paths, screenshots, frames, copied executables, saves, or private runtime proof.

## Saved Ghidra Corrections

| Address | Saved name | Saved signature | Result |
| --- | --- | --- | --- |
| `0x004888f0` | `CImposter__FindOrCreate` | `void * __cdecl CImposter__FindOrCreate(char * name, int key_24, int key_40, int key_30, int key_44, int key_48, int key_34)` | Hardened the find-or-create signature/comment around the global imposter list, `stricmp`, key-field matching, and `0x4c` object allocation context. |
| `0x00488a70` | `CImposter__AddToList` | `void __thiscall CImposter__AddToList(void * this)` | Hardened the list append signature/comment for the global singly linked list. |
| `0x00488aa0` | `CImposter__GetFrameHeightForOwnerSlot` | `float __thiscall CImposter__GetFrameHeightForOwnerSlot(void * this, void * owner)` | Corrected the stale `CIBuffer__GetEntryHeightByOwnerSlot` owner/signature label to CImposter frame-height context. |
| `0x00488ac0` | `ImposterGlobals__ClearTailSlots` | `void __cdecl ImposterGlobals__ClearTailSlots(void)` | Created a missing static-init table function boundary from the `0x006223b4` data xref. |
| `0x00488ae0` | `ImposterGlobals__InitDefaultFrameData` | `void __cdecl ImposterGlobals__InitDefaultFrameData(void)` | Created a missing static-init table function boundary from the `0x006223b8` data xref. |

## Evidence Summary

- The available Stuart source snapshot does not include matching source bodies for this tranche, so the correction is retail-static/debug-path evidence rather than exact source-body confirmation.
- `0x00488aa0` is now bounded as `CImposter__GetFrameHeightForOwnerSlot`: `CDXTrees__BuildTreeGeometry` is the observed direct caller, the helper uses owner `+0x08` vtable slot `+0x6c` to choose a frame index, and it returns a frame-table float from `this+0x3c +0x10 + index*0x18`.
- `0x00488ac0` and `0x00488ae0` were real code targets referenced by the static-init table but were not formal Ghidra function objects before this wave.
- The Wave415 function-count increase is expected: two real static-init targets that already existed as code addresses are now Ghidra function objects.
- Refreshed whole-project queue telemetry reports `6037` total functions, `1607` commented functions, `4430` commentless functions, `1891` undefined signatures, and `1837` `param_N` signatures. Current confirmation proxies are comment-backed `1607/6037 = 26.62%` and strict clean-signature `1541/6037 = 25.53%`; both are telemetry only, not milestones.

## Validation

- Expected red focused test before implementation: `py -3 tools\ghidra_imposter_wave415_probe_test.py` failed with `ModuleNotFoundError`.
- Focused tests: `py -3 tools\ghidra_imposter_wave415_probe_test.py` passed `2/2`.
- Python compile: `py -3 -m py_compile tools\ghidra_imposter_wave415_probe.py tools\ghidra_imposter_wave415_probe_test.py` passed.
- Headless dry run: `ApplyImposterWave415.java dry` reported `updated=0 skipped=3 created=0 would_create=2 renamed=0 would_rename=1 missing=0 bad=0` with `REPORT: Save succeeded`.
- Headless apply run: `ApplyImposterWave415.java apply` reported `updated=5 skipped=0 created=2 would_create=0 renamed=1 would_rename=0 missing=0 bad=0` with `REPORT: Save succeeded`.
- Read-back exports verified `5` metadata rows, `5` tag rows, `6` xref rows, `285` instruction rows, and `5` decompile exports.
- Package wrapper: `cmd.exe /c npm run test:ghidra-imposter-wave415` passed with focused probe status `PASS`.
- Queue refresh: headless `ExportFunctionQualitySnapshot.java` and `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with the `6037`-function telemetry above.
- Actual Ghidra project backup: copied `BEA.gpr` and `BEA.rep` to `[maintainer-local-ghidra-backup-root]\BEA_20260514_121033_post_wave415_imposter_verified` and verified `19` files, `154930055` bytes, and `HashDiffCount=0`.

## Not Proven

This tranche does not prove runtime imposter rendering behavior, runtime tree rendering behavior, exact source-body identity, concrete CImposter/CDXTrees layouts, local-variable/type recovery, BEA launch behavior, game patching, packaged app behavior, or rebuild parity.
