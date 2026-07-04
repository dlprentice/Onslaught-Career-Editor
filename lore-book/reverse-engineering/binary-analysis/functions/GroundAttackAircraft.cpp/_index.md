# GroundAttackAircraft.cpp Functions

> Source File: GroundAttackAircraft.cpp | Binary: BEA.exe
> Debug Path: 0x0062cadc

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Wave 391 corrected this page after fresh metadata, decompile, xref, instruction, RTTI/vtable, pointer-table, and tag read-back. The checked cluster now separates the aircraft init and bay-animation helpers from adjacent `CGroundAttackAI` and `CGroundAttackGuide` component destructor/state helpers.

Wave 432 added the adjacent `CMCGroundAttack` motion-controller correction. It creates missing vtable-slot boundaries at `0x00496540` and `0x004968a0`, corrects the constructor/destructor signatures, and narrows the nearby mesh-part token helpers to `turret` / `barrel` behavior. Wave1002 re-reviewed the GroundAttackAircraft / AI / guide / motion-controller island read-only and found the current saved evidence still coherent.

The available Stuart source corpus in this repo does not include `GroundAttackAircraft.cpp`, so the current names are grounded in retail-binary evidence, RTTI/vtable context, pointer-table ownership, debug-path strings, and behavior tokens rather than direct source-body parity.

Wave1135 (`wave1135-groundattack-gillmhead-current-risk-review`) re-read this GroundAttack/GillMHead guide lifecycle cluster with fresh Ghidra export evidence as a read-only review with no mutation. It accounts for `10 rows`, moves current focused accounting to `196/1179 = 16.62%`, keeps static closure at `6410/6410 = 100.00%`, keeps expanded static surface at `1560/1560 = 100.00%`, keeps Wave911 focused at `812/1408 = 57.67%`, keeps Wave911 top-500 at `500/500 = 100.00%`, and leaves static debt at `0 / 0 / 0`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 983. Exact anchors: `0x0047a760 CGillMHead__CreateGillMHeadAIComponent`, `0x0047a810 CGillMHeadAI__Destructor`, `0x0047a8b0 CGillMHeadAI__TryTransitionIdleToOpen`, `0x0047bab0 CGroundAttackAI__InitState`, `0x0047bbf0 CGroundAttackAircraft__Init`, `0x0047bd90 CGroundAttackAI__Destructor`, `0x0047be50 CGroundAttackGuide__Destructor`, `0x0047c040 CGroundAttackAircraft__AdvanceCloseShootAnimationState`, `0x0047e290 CGuide__ctor_base`, and `0x004964d0 CMCGroundAttack__Constructor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-104845_post_wave1134_console_current_risk_review_verified`. Runtime GroundAttack/GillMHead AI behavior, runtime guide/bay-animation/motion-controller behavior, exact layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Status |
| --- | --- | --- | --- |
| `0x0047bab0` | `CGroundAttackAI__InitState` | Clears `+0x60`, randomizes the `+0x64` timer/float, and calls `CGroundAttackAircraft__CloseBay` after `CGroundAttackAI` vtable install. | SAVED IN GHIDRA |
| `0x0047bbf0` | `CGroundAttackAircraft__Init` | Delegates to `CAirUnit__Init`, allocates/installs `CMCGroundAttack`, `CGroundAttackAI`, and `CGroundAttackGuide`, and initializes default animation/state fields. | SAVED IN GHIDRA |
| `0x0047bd70` | `CGroundAttackAI__ScalarDeletingDestructor` | `CGroundAttackAI` vtable slot-1 scalar-deleting destructor wrapper. | SAVED IN GHIDRA |
| `0x0047bd90` | `CGroundAttackAI__Destructor` | Restores the `CUnitAI` base vtable and removes tracked handles before monitor shutdown. | SAVED IN GHIDRA |
| `0x0047be30` | `CGroundAttackGuide__ScalarDeletingDestructor` | `CGroundAttackGuide` vtable slot-1 scalar-deleting destructor wrapper; supersedes the stale GillMHead label. | SAVED IN GHIDRA |
| `0x0047be50` | `CGroundAttackGuide__Destructor` | Removes linked reader/set field `+0x2c` before monitor shutdown; supersedes the stale GillMHead label. | SAVED IN GHIDRA |
| `0x0047bfa0` | `CGroundAttackAircraft__OpenBay` | Sets bay state `+0x27c` to opening and plays the open animation token when state allows. | SAVED IN GHIDRA |
| `0x0047bff0` | `CGroundAttackAircraft__CloseBay` | Sets bay state `+0x27c` to closing and plays the close animation token when state allows. | SAVED IN GHIDRA |
| `0x0047c040` | `CGroundAttackAircraft__AdvanceCloseShootAnimationState` | Advances open/shoot/close/idle animation state and writes bay state `+0x27c`; supersedes the older broad `CUnitAI` label. | SAVED IN GHIDRA |
| `0x0050ee10` | `CGroundAttackAircraft__scalar_deleting_dtor` | Wave557 primary vtable slot-1 scalar-deleting destructor wrapper; calls `CGroundAttackAircraft__Destructor_VFunc01` and optionally frees `this`. | SAVED IN GHIDRA |
| `0x0050f130` | `CGroundAttackAircraft__Destructor_VFunc01` | Wave557 primary destructor body; clears owned pointer sets, removes the global-list node, then calls `CUnit__dtor_base`. | SAVED IN GHIDRA |

## Motion Controller Corrections

| Address | Name | Purpose | Status |
| --- | --- | --- | --- |
| `0x004964d0` | `CMCGroundAttack__Constructor` | Installs vtable `0x005dc330`, stores the owner aircraft at `+0x08`, and seeds cached state fields. | SAVED IN GHIDRA |
| `0x00496500` | `CMCGroundAttack__ScalarDeletingDestructor` | Vtable slot-1 scalar-deleting destructor wrapper. | SAVED IN GHIDRA |
| `0x00496520` | `CMCGroundAttack__Destructor` | Restores vtable `0x005dc330`, clears `+0x08`, and tails into the base motion-controller destructor. | SAVED IN GHIDRA |
| `0x00496540` | `CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540` | Recovered vtable slot-4 boundary; checks the `turret` token and updates transform/cached owner state. | SAVED IN GHIDRA |
| `0x004968a0` | `CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0` | Recovered vtable slot-8 boundary; compares owner motion fields against cached values at `this+0x0c/+0x10`. | SAVED IN GHIDRA |
| `0x004968f0` | `CMeshPart__NameIsNotTurret` | Mesh-part name helper for the `turret` token at `0x0062dd20`. | SAVED IN GHIDRA |
| `0x00496910` | `CMeshPart__AnySubPartNameIsTurret` | Walks child mesh parts for a `turret` child name. | SAVED IN GHIDRA |
| `0x00496f60` | `CMeshPart__NameAvoidsTurretAndBarrelPrefix` | Corrects older backwards wording: rejects `turret`, then rejects `barrel` prefix matches. | SAVED IN GHIDRA |

## Wave752 Unwind Cleanup Evidence

Wave752 saved GroundAttackAircraft.cpp-adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-continuation-wave752` and `wave752-readback-verified` tags. These rows are static retail Ghidra evidence only, saved as `void __cdecl Unwind@...(void)`, with no renames, no function-boundary changes, and no executable-byte changes.

| Address | Evidence |
| --- | --- |
| `0x005d2b00 Unwind@005d2b00` | DATA scope-table xref `0x0061b904`; calls `OID__FreeObject_Callback` with GroundAttackAircraft.cpp debug path `0x0062cadc`, line `0x1b`, allocation/type value `0x13`, pointer `*(EBP+0x4)`. |
| `0x005d2b16 Unwind@005d2b16` | DATA scope-table xref `0x0061b90c`; calls `OID__FreeObject_Callback` with GroundAttackAircraft.cpp debug path `0x0062cadc`, line `0x16`, allocation/type value `0x14`, pointer `*(EBP+0x4)`. |
| `0x005d2b2c Unwind@005d2b2c` | DATA scope-table xref `0x0061b914`; calls `CUnitAI__dtor_body_00415080` on `*(EBP+0x4)`. |
| `0x005d2b34 Unwind@005d2b34` | DATA scope-table xref `0x0061b91c`; calls `OID__FreeObject_Callback` with GroundAttackAircraft.cpp debug path `0x0062cadc`, line `0x17`, allocation/type value `0x15`, pointer `*(EBP+0x4)`. |
| `0x005d2b60 Unwind@005d2b60` through `0x005d2b90 Unwind@005d2b90` | DATA scope-table refs `0x0061b944` through `0x0061b97c`; monitor shutdown, active-reader subobject teardown at `+0xc` / `+0x24`, and `CMonitor__Shutdown_Thunk` cleanup. |

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-212829_post_wave752_unwind_continuation_verified`. Exact parent source-body identity, runtime ground-attack aircraft cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Key Evidence

- `0x005dbd4c` demangles to `CGroundAttackAI`; its vtable slot `1` points to `0x0047bd70`.
- `0x005dbd20` demangles to `CGroundAttackGuide`; its vtable slot `1` points to `0x0047be30`.
- Function table `0x005e2bf0` points slot `0` to `CGroundAttackAircraft__Init` and slot `50` to `CGroundAttackAircraft__AdvanceCloseShootAnimationState`.
- `CGroundAttackAircraft__Init` references the `GroundAttackAircraft.cpp` debug path and allocates type-`0x1b`, type-`0x16`, and type-`0x17` objects before storing them in aircraft fields.
- Bay helpers use the open token at `0x00623bb4`, the close token at `0x006289e4`, the shoot token at `0x006289ec`, and the state field at `+0x27c`.
- `CMCGroundAttack` vtable `0x005dc330` slot `4` points to the created turret-transform boundary at `0x00496540`; slot `8` points to the created cached-state predicate at `0x004968a0`.

## Wave1002 GroundAttackAircraft Re-Audit (2026-05-31)

Wave1002 (`ground-attack-aircraft-review-wave1002`) re-reviewed the `GroundAttackAircraft.cpp` / `CGroundAttackAI` / `CGroundAttackGuide` / `CMCGroundAttack` island with fresh metadata, tag, xref, instruction, decompile, vtable, and pointer-table exports. Exact anchor: `0x004964d0 CMCGroundAttack__Constructor`. It made no Ghidra mutation, rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.

Fresh exports verified `16` metadata rows, `16` tag rows, `18` xref rows, `691` body-instruction rows, `16` decompile rows, `512` vtable-slot rows, `4` vtable type rows, and `80` pointer-table rows. Vtable type read-back resolves `0x005dbd4c` to `CGroundAttackAI`, `0x005dbd20` to `CGroundAttackGuide`, `0x005dc330` to `CMCGroundAttack`, and `0x005e2bcc` to `CGroundAttackAircraft`. Function table `0x005e2bf0` keeps slot `0` at `0x0047bbf0 CGroundAttackAircraft__Init` and slot `50` at `0x0047c040 CGroundAttackAircraft__AdvanceCloseShootAnimationState`.

Representative vtable anchors:

| Vtable | Slot | Target |
| --- | ---: | --- |
| `0x005dbd4c` | 1 | `0x0047bd70 CGroundAttackAI__ScalarDeletingDestructor` |
| `0x005dbd20` | 1 | `0x0047be30 CGroundAttackGuide__ScalarDeletingDestructor` |
| `0x005dc330` | 1 | `0x00496500 CMCGroundAttack__ScalarDeletingDestructor` |
| `0x005dc330` | 4 | `0x00496540 CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540` |
| `0x005dc330` | 8 | `0x004968a0 CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0` |
| `0x005e2bcc` | 1 | `0x0050ee10 CGroundAttackAircraft__scalar_deleting_dtor` |
| `0x005e2bcc` | 2 | `0x00402d30 CAirUnit__dtor_base` |

Wave1002 queue/progress anchor: static closure remains `6222/6222 = 100.00%`; Wave911 focused re-audit progress remains `472/1408 = 33.52%`; expanded static surface progress is `629/1478 = 42.56%`; Wave911 top-500 risk-ranked coverage is `359/500 = 71.80%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-112128_post_wave1002_ground_attack_aircraft_review_verified`.

Proof boundary: this is static retail read-back only. Exact Stuart source-body identity, concrete `CGroundAttackAircraft`/`CGroundAttackAI`/`CGroundAttackGuide`/`CMCGroundAttack` layouts, runtime AI/guide/bay-animation/destruction/motion behavior, BEA patching, and rebuild parity remain separate proof.

## Historical Corrections

- The older `0x0047bbf0` `CGroundAttackAircraft__Constructor` label is now corrected to `CGroundAttackAircraft__Init` because the function table points to it as an init slot and the body first delegates to `CAirUnit__Init`.
- The older `0x0047be30` / `0x0047be50` GillMHead labels are now corrected to `CGroundAttackGuide` destructor paths from RTTI/vtable evidence.
- The older `0x0047c040` broad `CUnitAI__AdvanceCloseShootAnimationState` label is now corrected to `CGroundAttackAircraft__AdvanceCloseShootAnimationState` from function-table and bay-state evidence.

## Proof Boundary

Wave 391 is saved Ghidra metadata refinement. It does not prove runtime ground-attack aircraft bay animation, targeting, AI, guide, weapon, or destruction behavior; exact Stuart-source method identity; concrete layouts; local variable names; local types; complete system coverage; or rebuild parity.

Wave 432 is also saved static Ghidra evidence only. It does not prove runtime `CMCGroundAttack` transform/state behavior, exact source virtual names, complete concrete layouts, local variables/types, BEA launch, game patching, or rebuild parity.

Wave557 adds the primary `CGroundAttackAircraft__scalar_deleting_dtor` and `CGroundAttackAircraft__Destructor_VFunc01` lifecycle pair. This is static vtable/xref/decompile read-back only and does not prove runtime aircraft teardown behavior, concrete layouts, exact source virtual names, BEA launch, game patching, or rebuild parity.

## Related Files

- AirUnit.cpp - `CAirUnit` base initialization context.
- GillMHead.cpp - historical stale-label source for `0x0047be30` / `0x0047be50`; now superseded by this page.
- Unit.cpp - historical stale-label source for `0x0047c040`; now superseded by this page.

---
*Originally discovered via Phase 1 xref analysis (Dec 2025); Wave 391 correction applied 2026-05-14; Wave 432 motion-controller correction applied 2026-05-15.*
