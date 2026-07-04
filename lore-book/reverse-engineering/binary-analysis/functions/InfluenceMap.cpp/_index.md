
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

# InfluenceMap.cpp - Function Analysis

**Retail evidence scope**: Wave418 and Wave455 saved-Ghidra static re-audits, 2026-05-14 and 2026-05-16
**Status**: DOCUMENTED / current static correction, not runtime-certified

## Current Boundary

Wave418 re-audited the active CInfluenceMap / CInfluenceMapManager cluster from fresh retail Ghidra metadata, decompile, xref, instruction, vtable, string, and tag exports. Wave455 then re-audited the older InfluenceMap-flavored follow-up entries and corrected stale owners where the retail evidence pointed to CUnit or CPolyBucket instead. Wave754 added saved static read-back comments/tags/signatures for adjacent InfluenceMap.cpp unwind cleanup callbacks. The current repo snapshot of Stuart's source does not include a directly matching InfluenceMap source body; historical debug-path strings and prior notes are useful hints, not source-body proof.

This page is bounded to saved static Ghidra evidence. It does not prove runtime InfluenceMap AI behavior, exact source-body identity, concrete class layouts, local variable/type recovery, BEA launch behavior, game patching, or rebuild parity.

## Wave754 InfluenceMap.cpp Unwind Continuation (0x005d2f30-0x005d2fa0)

Wave754 static read-back (`unwind-continuation-wave754`, `wave754-readback-verified`) hardened adjacent InfluenceMap.cpp unwind callbacks as `void __cdecl Unwind@...(void)` without renames, function-boundary changes, or executable-byte changes. Evidence includes the InfluenceMap.cpp debug path at `0x0062d61c`, DATA scope-table xrefs, `OID__FreeObject_Callback` rows, `CComplexThing__dtor_base`, and `CSPtrSet__Clear`. Exact anchors include `0x005d2f30 Unwind@005d2f30`, `0x005d2f54 Unwind@005d2f54`, and `0x005d2fa0 Unwind@005d2fa0`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-102949_post_wave754_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

| Address | Scope-table xref | Static read-back evidence |
| --- | --- | --- |
| `0x005d2f30` | `0x0061bd1c` | `OID__FreeObject_Callback(*(EBP-0x3d0))` with line token `0x20` and allocation/type value `0x74`. |
| `0x005d2f49` | `0x0061bd24` | `CComplexThing__dtor_base(*(EBP-0x3d0))`. |
| `0x005d2f54` | `0x0061bd2c` | `CSPtrSet__Clear((*(EBP-0x3d0))+0x7c)`. |
| `0x005d2f62` | `0x0061bd04` | `OID__FreeObject_Callback(*(EBP-0x3d0))` with line token `0x20` and allocation/type value `0x46`. |
| `0x005d2f7b` | `0x0061bd0c` | `CComplexThing__dtor_base(*(EBP-0x3d0))`. |
| `0x005d2f86` | `0x0061bd14` | `CSPtrSet__Clear((*(EBP-0x3d0))+0x7c)`. |
| `0x005d2fa0` | `0x0061bd54` | `OID__FreeObject_Callback(*(EBP-0x10))` with line token `0x20` and allocation/type value `0x1a6`. |

## Wave418 Functions

| Address | Current saved name | Static evidence |
| --- | --- | --- |
| `0x0048afb0` | `CInfluenceMap__FreeObjectIfPresent` | Cleanup helper for manager/map-owned object sets. |
| `0x0048b010` | `CInfluenceMapManager__Load` | Versioned InfluenceMap load helper; static evidence covers map-node and neighbor-link allocation context. |
| `0x0048b5f0` | `CInfluenceMap__GetTypeName_0048b5f0` | Created active vtable `0x005dc050` slot-7 helper returning the `CInfluenceNode` string. |
| `0x0048b600` | `CInfluenceMap__GetTypeId_0048b600` | Created active vtable `0x005dc050` slot-8 helper returning type id `0x1e`. |
| `0x0048b610` | `CInfluenceMap__GetInfluenceRadius_0048b610` | Created active vtable `0x005dc050` slot-16 getter returning field `this+0x94`. |
| `0x0048b620` | `CInfluenceMap__ResetInfluence` | Resets observed influence, accumulator, distance, and display fields. |
| `0x0048b660` | `CInfluenceMapManager__SkipLoad` | Reads/discards versioned InfluenceMap data without allocating map objects. |
| `0x0048b7d0` | `CInfluenceMapManager__PropagateDistances` | Iterative distance-propagation helper with event scheduling context. |
| `0x0048b8e0` | `CInfluenceMapManager__Update` | Manager update helper covering reset, unit/nearest-map context, propagation, and event scheduling. |
| `0x0048bf70` | `CInfluenceMapManager__DecayInfluence` | Temporary influence decay helper; removes depleted records and reschedules event context. |
| `0x0048c000` | `CInfluenceMapManager__FindNearestMap` | Nearest-map helper that creates a temporary influence record from world coordinates and influence parameters. |
| `0x0048c2d0` | `CInfluenceMapManager__IsEmpty` | Manager-count predicate. |
| `0x0048c2e0` | `CInfluenceMap__scalar_deleting_dtor` | Corrected stale `CInfluenceMap__ScalarDelete` wrapper label. |
| `0x0048c300` | `CInfluenceMap__dtor` | Corrected stale destructor-body label and hardened cleanup context. |
| `0x0048c350` | `CInfluenceMap__DetachNeighborLinks_0048c350` | Created active vtable `0x005dc050` slot-2 cleanup helper for neighbor-link detachment. |
| `0x0048c390` | `CInfluenceMap__InitFromComplexThingInit_0048c390` | Corrected stale `CInfluenceMap__RemoveFromList`; static body is an init-forwarding wrapper, not list removal. |
| `0x0048c3b0` | `CInfluenceMap__CalculateInfluence` | Influence-calculation helper over observed influence/state fields. |

## Wave455 Follow-Up Functions

| Address | Current saved name | Static evidence |
| --- | --- | --- |
| `0x004ad7f0` | `CInfluenceMap__SetTrackedThingAndClearCachedObject` | BattleEngine caller sets the tracked thing-like pointer at `this+0x14` and clears/frees cached pointer `this+0x24`; `ret 0x4` confirms one stack argument. |
| `0x004bf9e0` | `OID__InitInfluenceMapObject` | OID factory init helper for an InfluenceMap-related `CInitThing` subobject; calls `CInitThing__ctor`, writes `PTR_LAB_005dc1c0`, clears `+0x3bc`, and returns the object pointer. |
| `0x004d30d0` | `CInfluenceMap__AccumulateThingFlags` | Accumulates counters at `this+0x08/+0x0c/+0x10/+0x14/+0x18` from observed flags on `thing+0x34`; category semantics remain runtime-deferred. |
| `0x004d38c0` | `CUnit__TryDestroyedCleanupAndResetDeploymentGraph` | Corrected out of InfluenceMap ownership; calls `CUnit__MarkDestroyedAndCleanupLinks`, then `CUnit__ResetDeploymentGraphAndScheduleEvent` on success. |
| `0x004d39d0` | `CPolyBucket__InitFields` | Corrected out of InfluenceMap ownership; CPolyBucket-style field initializer called by `CMeshPart__CreatePolyBucket` and `CStaticShadows__BuildShadowMaps`. |
| `0x004d3a00` | `CPolyBucket__FreeBuffers` | Corrected out of InfluenceMap ownership; CPolyBucket-style buffer cleanup called by CMeshPart, CMesh, and CStaticShadows paths. |
| `0x0050b930` | `CInfluenceMapManager__scalar_deleting_dtor` | Manager vtable `0x005dfcb4` scalar-deleting destructor wrapper; calls the manager dtor and conditionally frees `this`. |
| `0x0050b950` | `CInfluenceMapManager__dtor` | Manager destructor body for `DAT_0067a748`; restores manager vtable, frees map-owned object context, clears two `CSPtrSet` members, then shuts down `CMonitor`. |

## Corrected Stale Notes

- `0x0048c390` is no longer documented as `CInfluenceMap__RemoveFromList`. The saved Ghidra name is `CInfluenceMap__InitFromComplexThingInit_0048c390`.
- `0x0048c2e0` and `0x0048c300` now use destructor-wrapper/body naming consistent with current saved signatures.
- `0x004d38c0`, `0x004d39d0`, and `0x004d3a00` are no longer InfluenceMap-owned entries. Wave455 moved them to CUnit and CPolyBucket documentation based on caller/vtable evidence.
- `0x0048dcf0` is no longer an InfluenceMap initializer in current docs; Wave419 corrected it to `CInitThing__ctor`.
- The active vtable for this cluster is `0x005dc050`; `0x005dc1cc` appears in older notes but was not the active table used for the Wave418 slot recovery.
- Any statement that the InfluenceMap source file is fully matched or that the class layout is complete is stale. The current claim is static retail evidence only.

## Observed Fields And Behavior Context

These offsets are useful static clues, not complete structure recovery:

| Offset | Observed context |
| --- | --- |
| `this+0x7c` | Neighbor-link / cleanup set context. |
| `this+0x94` | Radius-like value returned by active vtable slot 16 and used by nearest-map distance tests. |
| `this+0x9c` / `this+0xa0` | Influence accumulator context for one side/channel. |
| `this+0xa4` / `this+0xa8` | Influence accumulator context for the opposing side/channel. |
| `this+0xac` / `this+0xb0` | Distance-propagation fields seeded with large sentinel values. |
| `this+0xb4` / `this+0xb8` | Smoothed/current and target influence display context. |
| `this+0xbc` | Control/state enum-like field in influence calculation. |

## Event IDs

| ID | Hex | Static context |
| ---: | --- | --- |
| `1000` | `0x3e8` | Manager update scheduling context. |
| `1001` | `0x3e9` | Distance propagation scheduling context. |
| `1002` | `0x3ea` | Temporary influence decay scheduling context. |

## Retired Older Entries

The older InfluenceMap-flavored follow-up table has been retired. Its entries now have a current static disposition:

| Address | Saved name / older note | Current caution |
| --- | --- | --- |
| `0x0048dcf0` | `CInfluenceMap__Init` | Wave419 corrected this to `CInitThing__ctor`; the older InfluenceMap owner was stale. |
| `0x004ad7f0` | `CInfluenceMap__SetTrackedThingAndClearCachedObject` | Wave455 revalidated this as a one-argument BattleEngine handoff helper. |
| `0x004d30d0` | `CInfluenceMap__AccumulateThingFlags` | Wave455 revalidated this as a one-argument flag accumulator, with runtime category semantics still deferred. |
| `0x004d39d0` | `CInfluenceMap__ResetRuntimeState` | Wave455 corrected this to `CPolyBucket__InitFields`; the older InfluenceMap owner was stale. |
| `0x004d3a00` | `CInfluenceMap__FreeRuntimeBuffers` | Wave455 corrected this to `CPolyBucket__FreeBuffers`; the older InfluenceMap owner was stale. |

## Validation

Wave418 active cluster:

- Headless dry run: `updated=0 skipped=13 created=0 would_create=4 renamed=0 would_rename=3 missing=0 bad=0`.
- Headless apply: `updated=17 skipped=0 created=4 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back verified `17` metadata rows, `17` tag rows, `24` xref rows, `1683` instruction rows, `17` decompile exports, active vtable `0x005dc050` slot resolution, and the `CInfluenceNode` string token.
- Focused probe status: `PASS`.
- Refreshed queue: `6043` functions, `1641` commented functions, `4402` commentless functions, `1878` undefined signatures, `1822` `param_N` signatures.
- Live Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260514_135504_post_wave418_influencemap_verified`, `19` files, `155061127` bytes, `HashDiffCount=0`.

Wave455 follow-up:

- Headless dry run: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=5 missing=0 bad=0`.
- Headless apply: `updated=8 skipped=0 created=0 would_create=0 renamed=5 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry run: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back verified `8` metadata rows, `8` tag rows, `13` xref rows, `1032` focused instruction rows, `8` decompile exports, and focused probe status `PASS`.
- Refreshed queue: `6057` functions, `1997` commented functions, `4060` commentless functions, `1732` undefined signatures, `1668` `param_N` signatures.
- Current telemetry proxies: comment-backed `1997/6057 = 32.97%`; strict comment-plus-clean-signature `1934/6057 = 31.93%`. These are not certification milestones.
- Live Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-144540_post_wave455_influencemap_followup_verified`, `19` files, `156765063` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Remaining Work

- Recover concrete structures, locals, and data types only where retail evidence supports them.
- Treat runtime InfluenceMap behavior as unproven until a separate copied-profile runtime proof exists.
