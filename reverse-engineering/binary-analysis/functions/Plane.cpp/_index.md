# Plane.cpp Functions

Wave1219 final current-risk closure note: `CPlane__Hit_CheckFatalDamageAndDie` remains mapped to the plane fatal-hit/death dispatch path; verified backup `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`. Runtime hit/death behavior, exact layout, and rebuild parity remain separate proof.

> Source File: Plane.cpp | Binary: BEA.exe
> Debug Path: 0x00631630 (`C:\dev\ONSLAUGHT2\Plane.cpp`)

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Retail static evidence places `CPlane` in the aircraft family under `CAirUnit`. Wave483 hardened the saved Ghidra signature/comment for the init entry and corrected two stale doc claims: the `0x80` write is to `init_thing+0x80`, not `this+0x80`, and the random roll field is set to `+/-0.8`, not `+0.8/-5.5`. Wave484 then corrected the adjacent `CPlaneAI` destructor pair from generic/ctor-like labels to a vtable-backed scalar-deleting destructor wrapper plus destructor body. Wave485 corrected the next CPlane hit/death gate and launch/wing/attack animation helpers from stale `CUnitAI` / `CExplosionInitThing` owners to CPlane-local labels.

The current Stuart source snapshot does not contain a `Plane.cpp`, `CPlane`, or `CWarspite` source body, so these notes are retail-binary evidence only.

Wave1006 (`air-unit-crash-support-vfunc-review-wave1006`) normalized the saved comments/tags for the plane-family crash/support overrides. CDiveBomber, CPlane, CGroundAttackAircraft, and CBomber vtable slot 68 rows point to `0x004d20a0 CPlane__VFunc_68_CrashIfNoAirSupport`; the same vtable family slot 69 rows point to `0x0047bf60 CPlane__VFunc_69_CrashIfNoSupportModes`; slot 117 rows point to the shared `0x00403a50 CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear`. The pass made no rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation. Progress after Wave1006: `485/1408 = 34.45%`, `662/1478 = 44.79%`, `384/500 = 76.80%`, static closure `6223/6223 = 100.00%`; verified backup `G:\GhidraBackups\BEA_20260531-135619_post_wave1006_airunit_crash_support_vfunc_review_verified`. Runtime aircraft crash behavior, runtime flight/support-mode behavior, exact source virtual names, concrete `CPlane`/support-field/position/flag layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave1123 (`wave1123-airunit-plane-support-vfunc-review`) re-read `0x0047bf60 CPlane__VFunc_69_CrashIfNoSupportModes` and its CAirUnit callee `0x00403760 CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes` with a fresh read-only Ghidra export and no mutation. Evidence for the CPlane row includes the direct call to the CAirUnit slot-69 helper, unit-data `+0x11c/+0x124` support-mode checks, DATA vtable xrefs `0x005e2f34`, `0x005e2ce0`, `0x005e1a44`, and `0x005e1350`, and existing Wave1006 tags. Current focused accounting is `131/1179 = 11.11%`; verified backup `G:\GhidraBackups\BEA_20260605-052636_post_wave1123_airunit_plane_support_vfunc_review_verified`. Runtime aircraft crash behavior, runtime flight/support-mode behavior, exact source virtual names, concrete `CPlane`/support-field/position/flag layouts, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1184 (`wave1184-airunit-plane-residual-current-risk-review`) accounts for `3 AirUnit/Plane support-gate residual current-risk rows` with fresh Ghidra export evidence and no mutation. It re-read `0x00403730 CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport`, `0x00403a50 CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear`, and `0x004d20a0 CPlane__VFunc_68_CrashIfNoAirSupport`; static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `782/1179 = 66.33%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 397; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; both consults converged on exact three-row AirUnit/Plane residual slice; root rejected duplicate Wave1123 slot-69 rows; CAirUnit__Init deferred to separate lifecycle/init residual pass; no Cursor/Composer; Wave1006 provenance; air-unit support gate; plane-family slot 68; shared slot 117 predicate; `20 xref rows`; `51 instruction rows`; `3 decompile rows`; verified backup `G:\GhidraBackups\BEA_20260606-131434_post_wave1184_airunit_plane_residual_current_risk_review_verified`; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference remain the static target.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004d19d0 | [CPlane__Init](CPlane__Init.md) | Init entry; calls `CAirUnit__Init`, allocates guide/Warspite components, sets launch state, collects Engine hardpoints, and randomizes roll | ~576 bytes |
| 0x004d1c10 | [CPlaneAI__scalar_deleting_dtor](CPlaneAI__scalar_deleting_dtor.md) | CPlaneAI vtable slot 1 scalar-deleting destructor wrapper; calls the destructor body, tests scalar-delete bit 0, and optionally frees `this` | ~32 bytes |
| 0x004d1c30 | [CPlaneAI__dtor_body](CPlaneAI__scalar_deleting_dtor.md) | CPlaneAI destructor body; restores base `CUnitAI` vtable, removes linked cells, then calls `CMonitor__Shutdown` | ~224 bytes |
| 0x004d1f10 | [CPlane__Hit_CheckFatalDamageAndDie](CPlane__Hit_CheckFatalDamageAndDie.md) | CPlane-only vtable slot 39 hit gate; may trigger the plane fatal/death path before tailing to the shared CThing hit helper | ~112 bytes |
| 0x004d1f90 | [CPlane__PlayWingOpenAnimationOnce](CPlane__Hit_CheckFatalDamageAndDie.md) | CPlane wing-open helper; advances animation state `this+0x27c` from `1` to `2` after resolving `wingopen` | ~64 bytes |
| 0x004d1fd0 | [CPlane__PlayWingCloseAnimationOnce](CPlane__Hit_CheckFatalDamageAndDie.md) | CPlane wing-close helper; advances animation state `this+0x27c` from `4` to `3` after resolving `wingclose` | ~64 bytes |
| 0x004d2010 | [CPlane__UpdateAttackLaunchAnimationState](CPlane__Hit_CheckFatalDamageAndDie.md) | CPlane-only vtable slot 59 animation state updater; selects `attack` or `launch` based on `this+0x27c` | ~144 bytes |
| 0x004d20a0 | CPlane__VFunc_68_CrashIfNoAirSupport | Plane-family vtable slot 68 override; calls the CAirUnit slot-68 body, then triggers crash/death when the air-support gate is zero | ~48 bytes |
| 0x0047bf60 | CPlane__VFunc_69_CrashIfNoSupportModes | Plane-family vtable slot 69 override; calls the CAirUnit slot-69 body, then triggers crash/death when both support-mode gates are zero | ~48 bytes |
| 0x0050eeb0 | CPlane__scalar_deleting_dtor | Wave557 primary CPlane vtable slot-1 scalar-deleting destructor wrapper; calls `CPlane__Destructor_VFunc01` and optionally frees `this` | ~32 bytes |
| 0x0050f260 | CPlane__Destructor_VFunc01 | Wave557 primary CPlane destructor body; clears owned pointer sets, removes the global-list node, then calls `CUnit__dtor_base` | ~112 bytes |

## CPlane__Init Summary

**Saved signature:** `void __thiscall CPlane__Init(void * this, void * init_thing)`

Key operations from Wave483 read-back:

1. Writes `1` to `init_thing+0x80` before base initialization.
2. Calls `CAirUnit__Init(this, init_thing)`.
3. Allocates a `0x30` guide component, calls `CAirGuide__ctor`, and stores the result at `this+0x208`.
4. Allocates a `0x64` component, calls `CWarspite__Init(this, init_thing)`, installs vtable pointer `0x005de73c`, and stores it at `this+0x13c`.
5. Looks up the `launch` animation string at `0x006243f8`, then sets launch state/timer at `this+0x27c` / `this+0x280`.
6. Enumerates `Engine` hardpoints through string `0x00622cec` and appends nodes into the list at `this+0x1d4`.
7. Uses `Random__NextLCGAbs` and stores roll field `this+0x284` as `0x3f4ccccd` or `0xbf4ccccd` (`+/-0.8`).

## CPlaneAI Destructor Summary

Wave484 read-back identifies `0x004d1c10` as `CPlaneAI__scalar_deleting_dtor` because `CPlaneAI` vtable `0x005de73c` slot 1 points to it and the RTTI COL resolves that table as `CPlaneAI`.

**Saved signatures:**

- `void * __thiscall CPlaneAI__scalar_deleting_dtor(void * this, byte flags)`
- `void __fastcall CPlaneAI__dtor_body(void * this)`

Key operations from Wave484 read-back:

1. The wrapper calls `CPlaneAI__dtor_body(this)`.
2. It tests scalar-delete `flags & 1`.
3. When set, it calls `CDXMemoryManager__Free(&DAT_009c3df0, this)`.
4. The body restores the base `CUnitAI` vtable pointer `0x005d8d1c`.
5. The body removes linked cells at `this+0x28`, `this+0x24`, and `this+0x0c` through `CSPtrSet__Remove` when present.
6. The body finishes with `CMonitor__Shutdown(this)`.

## CPlane Hit And Animation Summary

Wave485 read-back identifies four adjacent helpers as CPlane-local behavior:

- `0x004d1f10` is `CPlane__Hit_CheckFatalDamageAndDie`, saved as `void __thiscall CPlane__Hit_CheckFatalDamageAndDie(void * this, void * hit_thing, void * hit_context)`.
- `0x004d1f90` is `CPlane__PlayWingOpenAnimationOnce`, saved as `void __fastcall CPlane__PlayWingOpenAnimationOnce(void * this)`.
- `0x004d1fd0` is `CPlane__PlayWingCloseAnimationOnce`, saved as `void __fastcall CPlane__PlayWingCloseAnimationOnce(void * this)`.
- `0x004d2010` is `CPlane__UpdateAttackLaunchAnimationState`, saved as `int __fastcall CPlane__UpdateAttackLaunchAnimationState(void * this)`.

Key operations from Wave485 read-back:

1. `CPlane` vtable `0x005e1930` slot 39 points to `CPlane__Hit_CheckFatalDamageAndDie`.
2. `CDiveBomber`, `CGroundAttackAircraft`, and `CBomber` use different slot-39 hit handlers.
3. The hit helper gates on `this+0x164->0x11c`, `hit_thing+0x34` flags, and `+0x138` ownership/team comparison.
4. The selected fatal path may call `hit_thing` vfunc `+0x194`, then calls `CExplosionInitThing__ctor_like_004fd230`, then dispatches `this` vfunc `+0x38`.
5. The hit helper always tails to `CThing__Hit_TriggerDieOnUnitOrTypeMask02100000(this, hit_thing, hit_context)`.
6. The wing-open helper checks state `this+0x27c == 1`, resolves `wingopen` string `0x00624420`, calls `CMesh__FindAnimationIndexByName`, dispatches `this` vfunc `+0xf0`, and sets state `2`.
7. The wing-close helper checks state `this+0x27c == 4`, resolves `wingclose` string `0x0062442c`, calls `CMesh__FindAnimationIndexByName`, dispatches `this` vfunc `+0xf0`, and sets state `3`.
8. `CPlane` vtable `0x005e1930` slot 59 points to `CPlane__UpdateAttackLaunchAnimationState`; sibling aircraft vtables use different slot-59 animation helpers.
9. The update helper checks the linked object at `this+0x8` through vfunc `+0x58`, then plays `attack` string `0x00624438` for state `2 -> 4` or `launch` string `0x006243f8` for state `3 -> 1`.

## CPlane Primary Lifecycle Summary

Wave557 read-back identifies `0x0050eeb0` as `CPlane__scalar_deleting_dtor` because CPlane primary vtable `0x005e1930` slot 1 points to it. The wrapper calls `CPlane__Destructor_VFunc01(this)`, tests `delete_flags & 1`, optionally frees `this`, returns `this`, and ends with `RET 0x4`. The body at `0x0050f260` clears the owned pointer sets at `this+0x26c` and `this+0x25c`, removes `this+0x250` from the global list, then calls `CUnit__dtor_base(this)`.

## Observed Fields

| Offset | Owner | Observed role | Notes |
|--------|-------|---------------|-------|
| 0x80 | `init_thing` | init flag | Set to `1` before `CAirUnit__Init`; exact field meaning unknown. |
| 0x0c | `CPlaneAI` | destructor linked cell | Removed through `CSPtrSet__Remove` when present; exact set semantics unknown. |
| 0x13c | `this` | CWarspite-like component pointer | Allocated at `0x64` bytes; `CWarspite__Init` remains broad and unresolved. |
| 0x164 | `this` | unit-data/profile pointer | Wave485 hit gate reads nested field `+0x11c`; exact layout unknown. |
| 0x1d4 | `this` | Engine hardpoint/effect node list | Receives nodes allocated per matched `Engine` hardpoint. |
| 0x208 | `this` | CAirGuide component pointer | Allocated at `0x30` bytes and initialized by `CAirGuide__ctor`. |
| 0x24 | `CPlaneAI` | destructor linked cell | Removed through `CSPtrSet__Remove` when present; exact set semantics unknown. |
| 0x28 | `CPlaneAI` | destructor linked cell | Removed through `CSPtrSet__Remove` when present; exact set semantics unknown. |
| 0x27c | `this` | launch/wing/attack animation state | Set during launch setup and advanced by Wave485 helpers through states `1`, `2`, `3`, and `4`. |
| 0x280 | `this` | launch timer | Set during launch animation setup. |
| 0x284 | `this` | random roll field | Set to `+/-0.8`. |
| 0x34 | `hit_thing` | hit flags | Wave485 hit gate tests bitmasks including `0x400`, `0x8`, `0x10`, and `0x02100000`. |
| 0x138 | `this` / `hit_thing` | ownership/team compare value | Wave485 compares both values before selecting the plane fatal path. |

## Related Functions

- `CAirUnit__Init` at `0x00402ad0` - base aircraft initializer.
- `CAirGuide__ctor` at `0x00402150` - guide component constructor.
- `CWarspite__Init` at `0x004fe710` - broad component initializer; exact semantics deferred.
- `CMesh__FindAnimationIndexByName` at `0x004aa630` - launch animation lookup.
- `CThing__Hit_TriggerDieOnUnitOrTypeMask02100000` at `0x00403ba0` - shared hit/death tail helper reached by `CPlane__Hit_CheckFatalDamageAndDie`.
- `0x004cb040 ParticleEffectLink__PushGlobalList` - Wave822 particle manager owner links (`particle-manager-owner-links-wave822`) corrected the old `CWorldPhysicsManager__PushNodeGlobalList` label/signature to a shared ECX-node effect/owner-link global registration helper.
- `CSPtrSet__AddToTail` at `0x004e5b20` - appends the engine-node pointer.
- `CSPtrSet__Remove` at `0x004e5bd0` - removes CPlaneAI destructor linked cells when present.
- `CDXMemoryManager__Free` at `0x00549220` - frees scalar-deleted CPlaneAI instances when wrapper flags bit 0 is set.
- `CMonitor__Shutdown` / `CMonitor__Shutdown_Core` - base shutdown path reached by the destructor body.

Wave822 also hardened `0x004caf30 CParticleManager__ClearParticleOwnerBacklinks`, `0x004cb080 CParticleManager__PruneDeadOwnerLinks`, and `0x004cbc60 CParticleManager__UpdateRenderNodesAndResetState`. Queue after Wave822 is `5626/6098 = 92.26%`; next raw commentless row is `0x004cd7a0 CWorldPhysicsManager__FindNodeByNameGE`; verified backup `G:\GhidraBackups\BEA_20260524-180249_post_wave822_particle_manager_owner_links_verified`. Exact effect-handle/link-node/render-node/owner layouts, exact source-body identity, runtime particle shutdown behavior, runtime particle/effect behavior, runtime render behavior, BEA patching, and rebuild parity remain deferred.
- `Random__NextLCGAbs` at `0x004de8d0` - roll-field branch input.

## Wave763 Plane.cpp Unwind Continuation

Wave763 static read-back (`unwind-continuation-wave763`, `wave763-readback-verified`) saved comments/tags/signatures for Plane.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d4670 Unwind@005d4670` through `0x005d46c0 Unwind@005d46c0` as `void __cdecl Unwind@...(void)` rows. Evidence includes Plane.cpp debug path `0x00631630`, DATA scope-table xrefs `0x0061cf0c`, `0x0061cf14`, `0x0061cf1c`, and `0x0061cf44`, three `OID__FreeObject_Callback(*(EBP+0x4))` rows with line/allocation tokens `0x13/0x17`, `0x14/0x16`, and `0x2a/0x10`, plus `CMonitor__Shutdown(*(EBP-0x10))` at `0x005d46c0 Unwind@005d46c0`. Verified backup: `G:\GhidraBackups\BEA_20260523-150812_post_wave763_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime Plane cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Open Boundaries

- Exact `CPlane` and `init_thing` layouts are not recovered.
- Exact `CPlaneAI` layout, linked-set semantics, allocator ownership, and runtime AI destruction behavior are not recovered.
- Exact CPlane hit/death runtime behavior and wing/attack/launch animation behavior are not proven.
- Exact CPlane primary destructor runtime behavior, concrete pointer-set layout, and source virtual name are not proven.
- `CWarspite__Init` has many callers and was not folded into Wave483.
- Runtime flight, launch, hardpoint effect behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
