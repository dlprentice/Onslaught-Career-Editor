# Destroyable Segments Static Contract

Status: active static contract map
Last updated: 2026-06-07

Saved Ghidra metadata, xrefs, instructions, and decompile read-back support the
five segment/controller anchors described below. This is a static subsystem map,
not runtime damage, break, rubble, pickup, layout, patch, or rebuild proof.

## Static Contract

The retail static evidence maps destroyable segments as a vtable-driven damage/break/rubble subsystem under `DestructableSegmentsController.cpp`. The source-file inventory contains the debug path name, but the matching Stuart source body is not present in the current reference tree, so source-body identity remains unproven.

Observed field roles stay conservative:

| Offset / input | Static role |
| --- | --- |
| `this+0x0c` | Current damage/health-scale state used by damage, break, stage, and controller paths. |
| `this+0x10` | Total/reference damage-scale state used by scale and stage helpers. |
| `this+0x14` | Last damage time or global tick snapshot from `DAT_00672fd0`. |
| `this+0x18` | Last raw damage amount. |
| `this+0x20` | Parent segment pointer for parent-gate checks. |
| `this+0x24` | Child `CSPtrSet` head used by child registration and core-child destroyed checks. |
| `this+0x34` | Segment value/scale input used by scale recompute and rubble count paths. |
| `this+0x3c` | Controller/config context used by pickup and end-segment scale paths. |
| `scaleFactor`, `divisor` | Slot-11 damage-scale recompute inputs. |

Do not promote these to final C++ field names until exact layout proof exists.

## Damage And Break Flow

| Path | Static contract |
| --- | --- |
| Child registration | `0x00442700 CDestructableSegment__RegisterChild` adds child segments to the parent child `CSPtrSet` at `this+0x24`; Wave1205 confirms controller init/process callers without treating this as global monitor membership. |
| Core-child state gate | `0x004433f0 CDestroyableCoreSegment__AreCoreChildrenDestroyed` walks the core child list, preserves the missing-first-child warning path, and returns false while a child still reports the checked vfunc-slot state and field `+0x38` remains clear. |
| Controller dispatch | `CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold` is the indexed controller entry; Wave1067 ties it to controller threshold/callback state. |
| Base damage | `0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage` subtracts damage from `+0x0c`, records `+0x18/+0x14`, and clamps below-zero state. |
| Core damage | `0x004435f0 CDestroyableCoreSegment__VFunc_03_ApplyDamage` handles the core/primary variant, ignores ordinal 1, records damage/time, then dispatches break/rubble slots when depleted. |
| Swap damage | `0x00443780 CDestroyableSwapSegment__VFunc_03_ApplyDamage` compares damage-stage state before and after applying damage, then runs swap/rubble and child-destruction side effects on transition. |
| Base break | `0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak` marks broken, clears `+0x0c`, updates controller/link state, and dispatches child destruction. |
| Swap break | `0x00443810 CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak` runs one-shot swap/rubble side effects while `+0x44` is clear, then delegates to the base break handler. |
| Parent gate | `0x004435c0 CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate` checks core `+0x4c` and parent `+0x20` before parent slot `+0x18`. |
| Damage telemetry getters | `0x004442d0` and `0x00444300` are CUnit-facing indexed getters for segment fields `+0x14` and `+0x18`; runtime/UI semantics remain separate proof. |
| Bulk active refresh | `0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric` writes field `+0x1c` across the controller segment array and refreshes cached metric `this+0x18` from `CDestroyableSegment__SumActiveValueRecursive(root)`. |

## Rubble, Pickup, And Variants

`0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects` resolves rubble/mesh/effect context, derives spawn count from `this+0x34`, applies landscape damage, and can reach the configured pickup bridge. Wave1133 ties `0x00442710 CDestroyableSegment__SpawnConfiguredPickup` to `CWorldPhysicsManager__CreatePickup`, `DAT_008553f8`, controller/config context through `this+0x3c`, and config field `+0xe8`.

`0x00443a20 CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects` adds end-segment setup before the base rubble path. `0x00443830 CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex` derives a clamped stage index from `+0x0c`, `+0x10`, and `+0x40`.

Variant vtable anchors to preserve:

| Variant | Static anchors |
| --- | --- |
| Base | `0x005db038`, `0x005db04c`, `0x005db054`, `0x005db058`. |
| Core/primary | `0x005db078`, `0x005db084`, `0x005db088`, `0x005db098`. |
| Component | `0x005db0cc` component break owner-callback context from Wave1065. |
| End/leaf/standard | `0x005db0d8`, `0x005db0ec`, `0x005db10c`, `0x005db120`, `0x005db13c`, `0x005db140`, `0x005db154`, `0x005db158`, `0x005db168`, `0x005db170`, and `0x005db174`. |

## Evidence Boundary

This map is static retail Ghidra evidence. It is suitable for independent reconstruction planning and patch candidate scoping, but it does not prove runtime destructable-segment damage/break/rubble/cascade/pickup behavior, exact event payload schema, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
