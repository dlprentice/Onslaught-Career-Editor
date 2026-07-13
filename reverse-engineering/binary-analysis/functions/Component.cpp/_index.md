# Component.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0044e640` → `CFenrirMainGunAI__ScanListsAndSelectSupportTarget` (was `CSquadNormalReader__ScanListsAndSelectSupportTarget_0044e640`). Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Source File: Component.cpp | Binary: BEA.exe
> Debug Path: 0x006247f8

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Component system implementation for game entities. Handles creation and initialization of sub-components attached to units, particularly weapon systems like Fenrir guns and Carrier health pads. Uses a factory pattern to create different component types based on string matching.

Wave 324 re-read the saved Ghidra cluster and corrected this note from a three-function factory summary into a ten-target Component-family signature/comment/tag record. The current source snapshot does not contain matching `Component.cpp` bodies, so these are retail-binary Ghidra findings rather than exact source-body identity proof.

Wave1132 (`wave1132-component-ai-current-risk-review`) re-read and tag-normalized the component/active-reader UnitAI residual cluster with fresh Ghidra export evidence and no rename, signature, comment, function-boundary, or executable-byte change. Component-owned anchors are `0x00427b80 CComponent__VFunc_09_00427b80`, `0x00427f90 CComponentBomberAI__scalar_deleting_dtor`, `0x00427fb0 CComponentBomberAI__dtor_base`, `0x00428050 CFenrirMainGunAI__scalar_deleting_dtor`, and `0x00428070 CFenrirMainGunAI__dtor_base`; related UnitAI/Unit anchors are `0x00428710 CUnitAI__GetRenderPosFromActorOrCache`, `0x00428770 CUnitAI__GetRenderOrientationFromActorOrCache`, `0x00428c70 CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action`, `0x00428d50 CUnitAI__PlayActivateAnimationOrFinalizeActivated`, and `0x00428e80 CComponentAI__ClearReaderIfTargetDestroyedThenForward`. Wave1132 covers `10 rows`; current focused accounting is `178/1179 = 15.10%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1001; static debt remains `0 / 0 / 0`; the wave is the component/active-reader UnitAI residual cluster; fresh Ghidra export; tag-only normalization; 91 tags. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-093432_post_wave1132_component_ai_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-090018_post_wave1131_heightfield_current_risk_review_verified`. Runtime Component/UnitAI behavior, exact layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

Wave1215 static read-back (`wave1215-unit-targeting-combat-residual-current-risk-review`) re-read `ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640` as owner-deferred component-targeting evidence. DATA xref `0x005d96ac` points at the function boundary; the body scans state-selected list heads, compares candidate ranges/positions against owner at `this+0x08`, and conditionally dispatches `CSquadNormal__SetReaderAndRefreshSupportSelection`/`0x004ffdd0` style action context. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-090802_post_wave1215_unit_targeting_combat_residual_current_risk_review_verified`. Exact owner class, source identity, concrete target-list layout, runtime component behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00427b80 | CComponent__VFunc_09_00427b80 | Conservative virtual-slot helper; one stack init/context argument | ~336 bytes |
| 0x00427cd0 | CComponent__CreateSubComponent1 | Creates small sub-component context at this+0x70 | ~128 bytes |
| 0x00427d50 | CComponent__CreateSubComponent2 | Creates sub-component context at this+0x208 | ~128 bytes |
| 0x00427dd0 | CComponent__CreateWeaponComponent | Factory for component weapon/helper types | ~304 bytes |
| 0x00427f90 | CComponentBomberAI__scalar_deleting_dtor | Scalar-deleting destructor wrapper | ~32 bytes |
| 0x00427fb0 | CComponentBomberAI__dtor_base | Destructor-base cleanup | ~160 bytes |
| 0x00428050 | CFenrirMainGunAI__scalar_deleting_dtor | Scalar-deleting destructor wrapper | ~32 bytes |
| 0x00428070 | CFenrirMainGunAI__dtor_base | Destructor-base cleanup | ~160 bytes |
| 0x00428110 | CUnitAI__UpdateActivationStateAndSpawnPickup | Static activation/pickup helper context | ~1008 bytes |
| 0x00428500 | CUnitAI__RefreshCachedComponentTransform | Static cached transform helper context | ~112 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d19e0 | Unwind@005d19e0 | 77 (`0x4d`) | Cleanup for CreateSubComponent1; `OID__FreeObject_Callback` on `EBP-0x10`, Component.cpp debug path `0x006247f8`, memtype `0x1b` |
| 0x005d1a00 | Unwind@005d1a00 | 83 (`0x53`) | Cleanup for CreateSubComponent2; `OID__FreeObject_Callback` on `EBP-0x10`, memtype `0x17` |
| 0x005d1a20 | Unwind@005d1a20 | 92 (`0x5c`) | Cleanup for weapon component (Fenrir Bomb Launcher path); `OID__FreeObject_Callback` on `EBP-0x10`, memtype `0x16` |
| 0x005d1a36 | Unwind@005d1a36 | 94 (`0x5e`) | Cleanup for weapon component (Fenrir Main Gun path); `OID__FreeObject_Callback` on `EBP-0x10`, memtype `0x16` |
| 0x005d1a4c | Unwind@005d1a4c | 96 (`0x60`) | Cleanup for weapon component (Carrier Health Pad path); `OID__FreeObject_Callback` on `EBP-0x10`, memtype `0x16` |
| 0x005d1a62 | Unwind@005d1a62 | 99 (`0x63`) | Cleanup for weapon component (fallback path); `OID__FreeObject_Callback` on `EBP-0x10`, memtype `0x16` |
| 0x005d1a90 | Unwind@005d1a90 | n/a | Component-region monitor shutdown cleanup for pointer at `EBP-0x10` |
| 0x005d1a98 | Unwind@005d1a98 | n/a | Component-region embedded active-reader cleanup at `*(EBP-0x10)+0xc` |
| 0x005d1aa3 | Unwind@005d1aa3 | n/a | Wave746 post-Component embedded active-reader cleanup at `*(EBP-0x10)+0x24`; DATA scope-table xref `0x0061a914` |

## Function Details

### Wave 324 Saved Correction Summary

| Address | Saved signature | Ghidra tags |
| --- | --- | --- |
| 0x00427b80 | `void __thiscall CComponent__VFunc_09_00427b80(void * this, void * init)` | `component-system`, `component-wave324`, `signature-hardened`, `static-reaudit` |
| 0x00427cd0 | `void __fastcall CComponent__CreateSubComponent1(void * this)` | `component-system`, `component-wave324`, `signature-hardened`, `static-reaudit` |
| 0x00427d50 | `void __fastcall CComponent__CreateSubComponent2(void * this)` | `component-system`, `component-wave324`, `signature-hardened`, `static-reaudit` |
| 0x00427dd0 | `void __thiscall CComponent__CreateWeaponComponent(void * this, void * initOrContext)` | `component-system`, `component-wave324`, `signature-hardened`, `static-reaudit` |
| 0x00427f90 | `void * __thiscall CComponentBomberAI__scalar_deleting_dtor(void * this, byte flags)` | plus `destructor`, `owner-corrected` |
| 0x00427fb0 | `void __fastcall CComponentBomberAI__dtor_base(void * this)` | plus `destructor`, `owner-corrected` |
| 0x00428050 | `void * __thiscall CFenrirMainGunAI__scalar_deleting_dtor(void * this, byte flags)` | plus `destructor`, `owner-corrected` |
| 0x00428070 | `void __fastcall CFenrirMainGunAI__dtor_base(void * this)` | plus `destructor`, `owner-corrected` |
| 0x00428110 | `void __fastcall CUnitAI__UpdateActivationStateAndSpawnPickup(void * this)` | `component-system`, `component-wave324`, `signature-hardened`, `static-reaudit` |
| 0x00428500 | `void __fastcall CUnitAI__RefreshCachedComponentTransform(void * this)` | `component-system`, `component-wave324`, `signature-hardened`, `static-reaudit` |

Vtable RTTI read-back supports `CComponentBomberAI` at `0x005d96b4`, `CFenrirMainGunAI` at `0x005d9680`, `CRepairPadAI` at `0x005d8e08`, `CComponentGuide` at `0x005d9654`, and base `CUnitAI` at `0x005d8d1c`.

### CComponent__CreateSubComponent1 (0x00427cd0)

**Line**: 77

Allocates 0x14 (20) bytes via debug allocator and stores result at `this+0x70`. Uses `FUN_00495930` for secondary initialization if allocation succeeds.

```c
// Pseudocode
void CComponent::CreateSubComponent1() {
    void* obj = DebugAlloc(0x14, 0x1b, "Component.cpp", 77);
    if (obj) {
        this->field_70 = SomeInit(this != NULL ? this + 8 : 0);
    } else {
        this->field_70 = NULL;
    }
}
```

### CComponent__CreateSubComponent2 (0x00427d50)

**Line**: 83

Allocates 0x20 (32) bytes and stores at `this+0x208`. Calls `FUN_0047e290` for initialization and sets vtable pointer at `PTR_LAB_005d9654`.

```c
// Pseudocode
void CComponent::CreateSubComponent2() {
    void* obj = DebugAlloc(0x20, 0x17, "Component.cpp", 83);
    if (obj) {
        FUN_0047e290(this);
        obj->vtable = &vtable_005d9654;
        this->field_208 = obj;
    } else {
        this->field_208 = NULL;
    }
}
```

### CComponent__CreateWeaponComponent (0x00427dd0)

**Lines**: 92, 94, 96, 99

Factory function that creates different weapon component/helper types based on string comparison. Uses `stricmp` (0x00568390, was `FUN_00568390`) for string matching against component names. Observed paths allocate 0x60-byte objects and use `CWarspite__Init` context before storing the result at `this+0x13c`.

**String matching order**:
1. "Fenrir Bomb Launcher" (0x006248a0) - Line 92 - vtable 0x005d96b4
2. "Fenrir Main Gun" (0x00624890) - Line 94 - vtable 0x005d9680
3. "Carrier Health Pad" (0x0062487c) - Line 96 - vtable 0x005d8e08 (`CRepairPadAI`)
4. Default / non-matching path - Line 99 - allocates and clears the observed `+0x14` field after initialization

Result stored at `this+0x13c`.

```c
// Pseudocode
void CComponent::CreateWeaponComponent(param1) {
    char* typeName = *(this->field_164->field_B0);

    if (strcmp(typeName, "Fenrir Bomb Launcher") == 0) {
        void* obj = DebugAlloc(0x60, 0x16, "Component.cpp", 92);
        if (obj) {
            CWarspite::Init(this, param1);
            obj->vtable = &vtable_005d96b4;
            this->field_13c = obj;
        }
    }
    else if (strcmp(typeName, "Fenrir Main Gun") == 0) {
        // Similar with vtable_005d9680
    }
    else if (strcmp(typeName, "Carrier Health Pad") == 0) {
        // CRepairPadAI vtable_005d8e08
    }
    else {
        // Fallback path with observed field_14 clear after init
    }
}
```

## Key Observations

- **Debug allocator** - Uses `OID__AllocObject` which takes size, type, filename, and line number
- **Wave745 unwind continuation** - Saved static Ghidra comments/tags/signatures for `0x005d19e0 Unwind@005d19e0` through `0x005d1a98 Unwind@005d1a98` as the Component.cpp portion of the `unwind-continuation-wave745` tranche. The full tranche spans `0x005d1840 Unwind@005d1840` through `0x005d1a98 Unwind@005d1a98`, leaves raw commentless head `0x0042f220 CSPtrSet__Clear`, moves the high-signal head to `0x005d1aa3 Unwind@005d1aa3`, and has verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-170426_post_wave745_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.
- **Wave746 unwind continuation** - Saved static Ghidra comments/tags/signatures for `0x005d1aa3 Unwind@005d1aa3` as the post-Component active-reader lead-in to the `unwind-continuation-wave746` tranche. The full tranche spans `0x005d1aa3 Unwind@005d1aa3` through `0x005d1cc0 Unwind@005d1cc0`, leaves raw commentless head `0x0042f220 CSPtrSet__Clear`, moves the high-signal head to `0x005d1cd9 Unwind@005d1cd9`, and has verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-173500_post_wave746_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.
- **String comparison** - `stricmp` (0x00568390, was `FUN_00568390`) (returns 0 on match)
- **Warspite integration** - All weapon components are initialized via `CWarspite__Init`
- **Member offsets**:
  - `this+0x70` - SubComponent1 pointer
  - `this+0x13c` - Weapon component pointer
  - `this+0x164` - Pointer to parent/owner object
  - `this+0x208` - SubComponent2 pointer
- **VTables referenced**:
  - 0x005d9654 - CComponentGuide
  - 0x005d96b4 - CComponentBomberAI / Fenrir Bomb Launcher path
  - 0x005d9680 - CFenrirMainGunAI / Fenrir Main Gun path
  - 0x005d8e08 - CRepairPadAI / Carrier Health Pad path
  - 0x005d8d1c - CUnitAI base destructor context

## Current Boundaries

- Runtime Component, AI activation, pickup, weapon, and transform behavior remain unproven.
- Exact `Component.cpp` source-body identity remains open because matching source bodies are not present in the available source snapshot.
- Concrete object layouts, local variable names, structure types, exhaustive tags, and rebuild parity remain future work.

## Related Files

- Carrier.cpp - Carrier entity that uses health pad component
- Warspite.cpp - CWarspite class that weapon components inherit from
- Unit.cpp - Base unit class that likely contains CComponent

## Related Classes

- **CComponentBomberAI** - vtable RTTI context at 0x005d96b4
- **CFenrirMainGunAI** - RTTI at 0x00624840; vtable context at 0x005d9680
- **CRepairPadAI** - vtable context at 0x005d8e08
- **CComponentGuide** - vtable context at 0x005d9654
- **CUnitAI** - base vtable context at 0x005d8d1c
- **CFenrirBehaviourType** - RTTI at 0x00627b50
- **CCarrier** - Uses Carrier Health Pad component

---
*Initially discovered via Phase 1 xref analysis (Dec 2025); Wave 324 signature/comment/tag correction recorded 2026-05-12.*
