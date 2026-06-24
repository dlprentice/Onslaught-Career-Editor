# Ghidra Shared Unit Residual Vtable Boundary Wave1085 Readiness Note

Status: complete static boundary recovery
Date: 2026-06-02
Scope: `shared-unit-residual-vtable-boundary-review-wave1085`

Wave1085 recovered and saved twenty-four previously unresolved shared unit-family residual vtable-boundary function starts. The selected `.text` pointers were repeated across ten shared unit-family vtable samples including CAirUnit, CRadar, CGillMHead, CHiveBoss, CGroundUnit, CInfantryUnit, CSimpleBuilding, CPod, CSubmarine, and CSentinel style tables. The pass created function boundaries, saved conservative behavior-shaped names, comments, tags, and clean signatures, and made no executable-byte changes, no BEA launch, no runtime/game-file mutation, and no installed-game mutation.

Representative recovered rows:

| Address | Saved name | Static evidence |
| --- | --- | --- |
| `0x00401550` | `SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550` | Writes a three-float delta from `this+0x1c/0x20/0x24` minus `this+0x8c/0x90/0x94` to the caller output vector. |
| `0x004fd440` | `SharedUnitVFunc__TestField17c19cReadiness_004fd440` | Walks `this+0x17c` / `this+0x19c` style member lists and returns a boolean-style readiness result. |
| `0x004fc3c0` | `SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0` | Checks a candidate against the `this+0x17c` list and copies fallback/vector contexts before `RET 0x14`. |
| `0x004f9220` | `SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220` | Counts non-null nested list entries under argument field `+0x3bc`, increments global `0x0083da30`, and dispatches `0x00452b60`. |
| `0x004fe4a0` | `SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0` | Copies two source-derived vectors into `this+0x114` and `this+0x120`, then calls `0x004019b0`. |
| `0x004fdd60` | `SharedUnitVFunc__PropagateNameToField18c19c_004fdd60` | Copies a supplied name into `this+0x18c` entries and dispatches slot `+0xfc` across `this+0x19c`. |
| `0x00401900` | `SharedUnitVFunc__ForwardArgToThingBridge_00401900` | Forwards the stack argument to helper `0x004f3cb0`; final rename avoids address-suffixed helper debt. |
| `0x00401910` | `SharedUnitVFunc__CopyTransformAndNotify_00401910` | Copies a caller block into `this+0x8c`, calls `0x004f3ce0`, and optionally dispatches field `this+0x38` slot `+0x14`. |
| `0x004fce00` | `SharedUnitVFunc__ForwardField208Slot10_004fce00` | Forwards five stack arguments to `this+0x208` virtual slot `+0x10` when field `0x208` exists. |
| `0x004fb270` | `SharedUnitVFunc__ReturnField114Float_004fb270` | Returns float field `this+0x114` and stops before adjacent `0x004fb280`. |

Read-back evidence:

- Pre-state metadata export: `24` targets, `0` found, `24` missing.
- Pre diagnose export: `24` rows, all `INSTRUCTION_NO_FUNCTION`.
- Pre context exports: `888` around-instruction rows, `226` long-window instruction rows, `885` wide-window instruction rows, `790` xref rows, and `1600` sampled vtable-slot rows.
- Initial dry/apply/final dry: `updated=0 skipped=0 created=0 would_create=24 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`, then `updated=24 skipped=0 created=24 would_create=0 renamed=0 would_rename=0 signature_updated=24 comment_only_updated=0 bad=0`, then `updated=0 skipped=24 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`.
- Follow-up normalization dry/apply/final dry for `0x00401900`: `would_rename=1`, then `updated=1 skipped=23 created=0 would_create=0 renamed=1 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`, then clean final dry.
- Post exports verified `24` metadata rows, `24` tag rows, `790` xref rows, `431` function-body instruction rows, `24` decompile rows, and `1600` post vtable-slot rows.
- Sampled vtable-slot improvement: pre `1244` OK / `356` `NO_FUNCTION_AT_POINTER`; post `1480` OK / `120` `NO_FUNCTION_AT_POINTER`; the selected Wave1085 targets account for `236` slot occurrences changing from no-function to OK.
- Queue closure advances to `6331/6331 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, `0` `param_N` signatures, `0` weak-name rows, `0` uncertain-owner rows, `0` helper-address rows, and `0` wrapper-address rows.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1448/1560 = 92.82%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-125900_post_wave1085_shared_unit_residual_vtable_boundary_verified`, `19` files, `174918535` bytes, `DiffCount=0`.

What this proves:

- The 24 selected `.text` pointers now resolve to saved Ghidra function rows.
- The saved function rows have bounded names, signatures, comments, tags, xrefs, instruction bodies, and decompile outputs tied to shared unit-family vtable evidence.
- The sampled vtable surface now resolves 236 additional slot occurrences through the recovered functions.

What remains separate proof:

- Exact source virtual names.
- Concrete unit-family layout semantics.
- Runtime targeting, movement, render, event, name-propagation, transform, and field-forwarding behavior.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1085; shared-unit-residual-vtable-boundary-review-wave1085; 0x00401550 SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550; 0x004fd440 SharedUnitVFunc__TestField17c19cReadiness_004fd440; 0x004fc3c0 SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0; 0x004f9220 SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220; 0x004fe4a0 SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0; 0x00401900 SharedUnitVFunc__ForwardArgToThingBridge_00401900; 0x00401910 SharedUnitVFunc__CopyTransformAndNotify_00401910; 0x004fce00 SharedUnitVFunc__ForwardField208Slot10_004fce00; 1448/1560 = 92.82%; 812/1408 = 57.67%; 500/500 = 100.00%; 6331/6331 = 100.00%; G:\GhidraBackups\BEA_20260602-125900_post_wave1085_shared_unit_residual_vtable_boundary_verified; boundary recovery.
