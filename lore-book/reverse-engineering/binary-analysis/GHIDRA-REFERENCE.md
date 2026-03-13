# Ghidra Analysis Skill Reference - BEA.exe

> **Core reference for reverse engineering Battle Engine Aquila**
> **Last Updated:** 2026-03-01
> **Binary:** BEA.exe (Steam version)
> **Coverage status:** Strong semantic naming closure is tracked in `functions/FUNCTION_COVERAGE_STATE.md`; older wave-by-wave gap notes in this file are historical unless explicitly re-opened.

---

## PE/Executable Metadata

| Property | Value |
|----------|-------|
| **MD5** | `3b456964020070efe696d2cc09464a55` |
| **SHA256** | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` |
| **File Size** | 2,506,752 bytes (~2.4 MB) |
| **Loaded Memory** | ~6.1 MB (includes BSS/uninitialized data) |
| **Architecture** | x86 32-bit |
| **Functions** | 5,861 identified |
| **Format** | PE / Direct3D 9 |
| **Image Base** | 0x00400000 |

---

## DLL Dependencies

| DLL | Purpose |
|-----|---------|
| BINKW32.DLL | Bink Video (cutscenes) |
| D3D9.DLL | Direct3D 9 graphics |
| DINPUT8.DLL | DirectInput 8 controls |
| DSOUND.DLL | DirectSound audio |
| OGG.DLL / VORBIS.DLL | Ogg Vorbis codec |
| ZLIB.DLL | Compression |
| AVIFIL32.DLL | AVI handling |
| WSOCK32.DLL | Networking |

---

## Headless Semantic Wave133 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00504b40` | `CVBufTexture__UpdateTrackedPitchWithClamp` | Updates tracked pitch/value from target context when present, then clamps to configured min/max range. |
| `0x00504cf0` | `CVBufTexture__ShouldSkipUpdateByStateFlags` | State-gate predicate returning skip/deny when helper + flag combination indicates no active update path. |
| `0x00504d30` | `CVBufTexture__IsTransitionAllowedByState` | Returns transition-allowed status from helper gate or fallback state check (`+0x168 == 0`). |
| `0x005068f0` | `CEngine__AdvanceProgressIfAnySlotAssigned` | Scans slot assignment array for active entries and advances progress scalar when at least one slot is assigned. |
| `0x005078b0` | `CEngine__GetListEntryIdByIndex` | Iterates linked-list entries at `this+0x4c` and returns entry id for requested index (or zero when missing). |

## Headless Semantic Wave132 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0044adb0` | `CExplosionInitThing__ExtractYawPitchFromMatrixIfValid` | Extracts two orientation angles from matrix components (atan2 pairs) when a validity gate passes; otherwise zeroes angle outputs. |
| `0x00451a40` | `CUnitAI__FindLinkedNodeByGlobalId` | Walks AI-linked node list and returns first node whose id equals global selector `DAT_0089d94c`. |
| `0x00479f30` | `CUnitAI__ComputeTerrainClearanceNoiseScale` | Computes terrain-clearance delta from two shadow-height probes and converts it into a randomized scale factor with speed/state gates. |
| `0x0047a0b0` | `CUnitAI__ComputeLateralSlopeAlignment` | Derives lateral alignment scalar from heading (`+0x114`) and terrain normal/projection helper output. |
| `0x0047bf60` | `CUnitAI__ProcessAndCrashIfNoAirOrHoverSupport` | Runs shared AI helper, then triggers crash/death path when both support-mode gates are disabled (`unit_data +0x11c/+0x124`). |

## Headless Semantic Wave131 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x004bc2e0` | `CExplosionInitThing__ClearCostGridBoundsAndBuildPath` | Clears active rectangle in 256x256 cost grid to `0xFFFF`, resets dirty bounds trackers, then dispatches path build helper. |
| `0x004bc510` | `CExplosionInitThing__IsGridSegmentBlocked` | Bresenham-style grid-segment test against occupancy bitset; returns blocked/fail on first missing bit. |
| `0x004be1d0` | `CExplosionInitThing__BuildGridPathWithFallbackSearch` | Builds grid path: fast direct-segment accept, then fallback cost-search + traced path materialization when blocked. |
| `0x004bed30` | `CExplosionInitThing__StepToLowestCostNeighbor8` | Chooses next grid coordinate from 8-neighborhood by lowest cost entry, with edge guards. |
| `0x004beea0` | `CExplosionInitThing__SimplifyGridPathByLineOfSight` | Prunes intermediate path points by repeatedly testing segment visibility with `IsGridSegmentBlocked`. |

## Headless Semantic Wave130 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x004aede0` | `CMeshPart__LoadOldStyle_VersionA` | Old-style mesh-part loader variant selected by `CMesh__Load` version gate; reads vertices/triangles and rebuilds normals/tangents. |
| `0x004af110` | `CMeshPart__LoadOldStyle_VersionB_WithExtraBlock` | Old-style mesh-part loader variant with additional pre-vertex stream block before standard load/rebuild flow. |
| `0x004b0800` | `CMeshPart__ApplyRootTransformRecursive` | Recursively applies root/parent transform deltas across part tree and updates per-vertex/per-bone transforms. |
| `0x004b0c00` | `CMeshPart__GetBasisX` | Returns first basis axis triplet from mesh-part transform storage (`+0x04/+0x14/+0x24`). |
| `0x004b0c20` | `CMeshPart__GetBasisY` | Returns second basis axis triplet from mesh-part transform storage (`+0x08/+0x18/+0x28`). |

## Headless Semantic Wave129 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x004b4ba0` | `CMeshPart__PopulatePoseCacheRecursive` | Recursive pose-cache population pass over mesh-part hierarchy. |
| `0x004b4cd0` | `CMeshPart__RefreshCachedPoseIfStale` | Refreshes cached pose data only when cache freshness gate fails. |
| `0x004b4de0` | `CMeshPart__EvaluatePoseTransformForFrame` | Evaluates pose transform for requested frame and writes frame-local result. |
| `0x004b5330` | `CMeshPart__EvaluateAnimatedTransformCore` | Core animated-transform evaluation used by mesh-part pose update flow. |
| `0x004b5ad0` | `CMeshPart__RenderAnimatedRecursive` | Recursive animated render traversal over mesh-part tree. |

## Headless Semantic Wave128 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0048ff90` | `CMessageBox__ActivateWithFadeStep_0p1` | Activates message box and seeds fade/transition step around 0.1 increment path. |
| `0x004b7300` | `CMessageBox__scalar_deleting_dtor` | Scalar-deleting destructor wrapper for message-box object. |
| `0x004b7ea0` | `CMessageBox__StartVoiceOrFallbackTextReveal` | Starts voice playback when available; otherwise initializes fallback text-reveal mode. |
| `0x004b8020` | `CMessageBox__AdvanceRevealAndScheduleNextTick` | Advances reveal cursor/timer state and schedules next reveal tick. |
| `0x004b8800` | `CMessageBox__StopVoicePlaybackIfNotInCutscene` | Stops active voice playback when cutscene gate is not active. |

## Headless Semantic Wave127 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x004aea50` | `CMeshPart__ComputeLocalBoundsAndBoundingRadius` | Computes local AABB extents and derived bounding radius for mesh part. |
| `0x004b0c40` | `CMeshPart__FindNearestVertexIndex` | Returns nearest vertex index to query point/radius inputs. |
| `0x004b1d30` | `CMeshPart__LinkDamagedPartVariantsBySuffix` | Links damaged mesh-part variants by suffix/name matching in load/link pass. |
| `0x004b24d0` | `CMeshPart__ResolveWrappedFrameIndexAndLerp` | Resolves wrapped animation frame index and interpolation state. |
| `0x004b1eb0` | `CMeshPart__RebuildPerVertexNormalsAndTangents` | Recomputes per-vertex normals/tangent data from current mesh topology. |

## Headless Semantic Wave126 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0049bbb0` | `MathMatrix3x3__DivideByScalarInPlace` | Divides each 3x3 matrix element by scalar argument in-place. |
| `0x0049bc10` | `MathMatrix3x3__TransposeInPlace` | In-place 3x3 transpose helper. |
| `0x0049bc40` | `MathMatrix3x3__Determinant` | Computes determinant of a 3x3 matrix. |
| `0x0049bc80` | `MathMatrix3x3__BuildCofactorMatrix` | Builds cofactor matrix from source 3x3 matrix input. |
| `0x004901e0` | `MathMatrix3x4__AssignFromEightScalars` | Assigns matrix/scalar fields from eight scalar inputs in packed initializer path. |

## Headless Semantic Wave125 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00479db0` | `CExplosionInitThing__TriggerRandomGillArmSubEffect` | Chooses random Gill arm token (`Gill_M_Left_Arm` / `Gill_M_Right_Arm`) and triggers corresponding sub-effect path. |
| `0x0047a160` | `CExplosionInitThing__StartState1WithStoredMotionVector` | Enters state-1 setup using pre-stored motion-vector fields as the initial movement source. |
| `0x0047d670` | `CUnitAI__FreeOwnedObjects_10_18` | Frees owned object pointers at offsets `+0x10` and `+0x18` and clears both slots. |
| `0x0047e870` | `CUnitAI__ResetWorkGrid1024AndFlags` | Clears 1024-byte work grid and resets related control flags/state fields for reuse. |
| `0x00490e10` | `CUnitAI__InitWorkGrid1024` | Thin init wrapper that funnels into `CUnitAI__ResetWorkGrid1024AndFlags`. |

## Headless Semantic Wave124 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0048f210` | `CLandscapeVB__RebuildHeightGridVertexBuffer` | Rebuilds terrain height-grid vertex data; called by landscape VB init/update paths. |
| `0x004804c0` | `CExplosionInitThing__ApplyHBConfigField` | Applies parsed `hb_*` config keys to explosion-init config fields. |
| `0x0047cea0` | `CUnitAI__ClearLinkedThingFlagsAndResetCounter` | Clears linked-thing flags and resets local counter/state during AI cleanup path. |
| `0x0047fb00` | `CUnitAI__QueueMessageWithTimestamp` | Queues AI message/event record and stamps timing fields for deferred processing. |
| `0x00490900` | `Vec3__SubtractInPlace` | Math helper implementing in-place vector subtraction (`dest -= src`) on three float components. |

## Headless Semantic Wave123 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00480c90` | `CHLCollisionDetector__HandleCollisionEnter` | Enter-event callback in HL collision detector map/who collision dispatch flow. |
| `0x00480db0` | `CHLCollisionDetector__HandleCollisionExit` | Exit-event callback in HL collision detector map/who collision dispatch flow. |
| `0x00481060` | `CHLCollisionDetector__ProcessMapWhoCollisionSweep` | Collision sweep/update pass that drives enter/exit callbacks over map/who pairs. |
| `0x00489de0` | `CUnitAI__PromoteDieAnimationToDeadVariant` | Converts die-animation token to dead-state variant before final death transition. |
| `0x00489ef0` | `CUnitAI__ForceDeadForwardAndResetDeathState` | Forces forward dead pose/state and resets death-transition state fields. |

## Headless Semantic Wave114 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00406460` | `CBattleEngine__SwapPrimarySecondaryPartReadersForState` | Morph-state helper that swaps active reader/object pointers between `+0x30` and `+0x5ec`, toggles gate `+0x5f0`, and reparents `+0x70`/`+0x5f4` depending on state (`1/3` vs `2`). |
| `0x00406560` | `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` | Maintains tracked-target set at `+0x294`, prunes invalid/out-of-FOV entries, and emits projectiles through `CBattleEngine__AddProjectile` using resolved entry constraints. |
| `0x00406da0` | `CBattleEngine__SelectNearestForwardTargetFromGlobalSet` | Scans global target set (`DAT_008550d0`) and returns nearest in-range forward-facing candidate not already in current tracked set. |
| `0x0040e8e0` | `CUnit__IsNearGroundByTerrainProbe` | Calls terrain/shadow-height probe (`CStaticShadows__Helper_0047eb80`) and returns boolean-like near-ground result from height-threshold comparison. |
| `0x0040eeb0` | `CUnit__FinishedPlayingCurrentAnimation` | Checks current animation against `flytowalk`/`walktofly` indices and dispatches next-mode set helper (`CGillMHead__Helper_004f4560`) for transition completion. |

## Headless Semantic Wave115 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00447ac0` | `CUnitAI__PlayWingFoldedAnimationAndSetState3` | Plays `"wingfolded"` animation, clears cached-anchor flag, and sets door/wing state machine to state `3`. |
| `0x00447b10` | `CUnitAI__PlayWingUnfoldedAnimationAndSetState5` | Plays `"wingunfolded"` animation and sets door/wing state machine to state `5`. |
| `0x00447b60` | `CUnitAI__HasReachedCachedAnchorPoint` | Returns true when XY distance from current unit position to cached anchor point (`+0x280/+0x284`) is below threshold. |
| `0x00447bb0` | `CUnitAI__GetOrGenerateCachedAnchorPoint` | Returns cached anchor point or generates one with bounded random search until validation succeeds. |
| `0x00447fa0` | `CUnitAI__AdvanceDoorWingAnimationState` | Advances door/wing animation chain (`dooropening/dooropen/doorclosing/doorclosed/wing*`) and dispatches follow-up state callbacks. |

## Headless Semantic Wave116 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00445ad0` | `CUnitAI__UpdateDoorWingEngagement_CloseRange` | Close-range engagement updater that toggles open/close animation paths and movement offsets around target proximity thresholds. |
| `0x00445f40` | `CUnitAI__UpdateDoorWingEngagement_MidRange` | Mid-range engagement updater that evaluates planar distance/angle and chooses direct reposition versus helper-driven tracking update. |
| `0x00446150` | `CUnitAI__UpdateDoorWingEngagement_LongRange` | Long-range engagement updater that applies standoff thresholds, calls open/close state transitions, and updates movement target. |
| `0x00446400` | `CUnitAI__EnterDoorWingOpenTrackingState` | Enters/maintains open-tracking mode, randomizes follow distance threshold, and triggers open-animation path when target exists. |
| `0x004496e0` | `CCareer__AreSecondaryObjectivesComplete` | Scans secondary-objective status slots and returns success only when objectives exist and all are marked complete; used by `CCareer__ReCalcLinks` and end-level summary paths. |

## Headless Semantic Wave117 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00444f00` | `CUnitAI__CallIndexedEntryVFunc10` | Resolves indexed entry pointer and invokes entry vfunc slot `+0x10` when the entry exists. |
| `0x00447a40` | `CUnitAI__SetDoorWingState2AndClampYawDelta` | Writes door-wing state `2` and clamps yaw-delta field across upper/lower bounds when transition gates pass. |
| `0x004480c0` | `CUnitAI__CanContinueDoorWingTransition` | Returns continuation-eligible status from anchor/target/state gating checks in door-wing flow. |
| `0x00448110` | `CUnitAI__SetDoorWingState6` | Writes door-wing state field (`+0x27c`) to state `6`. |
| `0x00448120` | `CUnitAI__SetDoorWingState7AndMirrorYawOffset` | Writes state `7` and mirrors yaw-offset field around a constant pivot value. |

## Headless Semantic Wave118 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0044d1f0` | `CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4` | Calls shared helper `0x00402000`; if bit-flag `0x4` is set, dispatches vfunc slot `+0x38`. |
| `0x0044d210` | `CUnitAI__RenderWithStaticShadowVisibilityUpdate` | Calls `CStaticShadows__UpdateVisibility(this, 0)` then forwards to `CThing__Render`. |
| `0x00452ce0` | `CFrontEnd__RenderVideoQuadScaledToWindow` | Frontend pre-common render helper: derives default center from window dimensions and renders video quad via `CDXFrontEndVideo__Render` after state-cache setup. |
| `0x00469390` | `CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture` | Input/interaction gate: returns masked ready-state when mouse input is ready, otherwise dispatches `CVBufTexture` interaction path. |
| `0x00469550` | `CFrontEnd__ResolveLevelNameTextByCode` | Maps level/world numeric codes to localized text IDs and falls back to `"Unnamed Level"` scratch text when unmapped. |

## Headless Semantic Wave119 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00444f20` | `CUnitAI__CanUseIndexedSegmentEntry` | Indexed segment-availability predicate: resolves per-index entry pointers, checks segment/core-child state, and returns eligibility gate for follow-up behavior. |
| `0x0044cd20` | `CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200` | Decays engagement metric field (`+0xe0`), triggers vfunc slot `+0x200` below threshold when flag gate allows, and clamps to profile max. |
| `0x00444620` | `CExplosionInitThing__SetChildStateAndRefreshSegmentMetric` | Iterates attached entries and writes child state value (`+0x1c`), then refreshes cached segment metric from destroyable-segment helper. |
| `0x004691c0` | `CFrontEnd__ReleaseParticleHudWaypointResources` | Frontend cleanup path that destroys particle manager state, clears HUD-owned handles, drops waypoint/mesh transient resources, and zeroes retained pointers. |
| `0x00440b70` | `CUnitAI__ResetPrimaryAndTailSentinels` | Small reset helper that clears primary state word and a far-tail sentinel field (`+0x1588c`). |

## Headless Semantic Wave120 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x004caf30` | `CParticleManager__ClearParticleOwnerBacklinks` | Iterates effect-handle chain and clears owner backlink fields (`+0xa4/+0xa8`) for each node. |
| `0x004cb080` | `CParticleManager__PruneDeadOwnerLinks` | Walks manager list and nulls handle references when linked owner activity flag is no longer set. |
| `0x004cbc60` | `CParticleManager__UpdateRenderNodesAndResetState` | Iterates render-node list, conditionally dispatches vfunc `+0x5c(0)` for type `0xb`, then restores render state via `RenderState_Set(0xf,1)`. |
| `0x004cbff0` | `CParticleManager__DestroyParticleList` | Owner-corrected list-destruction helper: repeatedly destroys head particle node and advances until list is empty. |
| `0x004cb920` | `CParticleManager__UpdateParticleAndRecycleIfDead` | Per-particle update path: lifetime/position integration, owner-handle backlink refresh, state callback dispatch, and recycle into free-list when dead flag set. |

## Headless Semantic Wave121 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00469c20` | `CFrontEnd__ResolveEpisodeNameTextByIndex` | Owner-corrected episode-name resolver: maps episode indices (`1..8`) to localized text IDs and falls back to `"Unnamed Episode"`. |
| `0x00469cf0` | `CFrontEnd__ResolveLevelNameTextIdByCode` | Owner-corrected level/world-code to text-id resolver returning `-1` on unmapped values; paired with frontend level-name string lookup paths. |
| `0x0046a210` | `CFrontEnd__GetFallbackUnnamedLevelTextId` | Owner-corrected fallback constant helper returning sentinel text-id used by frontend level-name resolution. |
| `0x004cba30` | `CParticleManager__ProjectPointToTerrainWithRadiusClamp` | Terrain-projection helper: projects point to terrain/shadow height and outputs clamped point if within radius gate. |
| `0x004cba90` | `CParticleManager__ComputeMinCameraDistanceSqForParticle` | Computes minimum squared distance from particle (with attachment offset) to active cameras and returns large fallback when unavailable. |

## Headless Semantic Wave122 Promotions (2026-02-27)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00478160` | `Geometry__ClipSegmentAgainstAABB3D` | Owner-corrected 3D Cohen-Sutherland style segment clipper against axis-aligned bounds; mutates both endpoints and returns acceptance/rejection. |
| `0x00478c20` | `Geometry__IntersectSegmentTriangleAndStoreHit` | Owner-corrected segment/triangle intersection test with optional hit-record writeback (impact point, normal, travel fraction). |
| `0x00479d10` | `CExplosionInitThing__UpdateGroundedVerticalDrift` | Owner-corrected vertical-drift updater: probes terrain height, adjusts drift/speed fields by grounded state, then dispatches shared step helper. |
| `0x0047c040` | `CUnitAI__AdvanceCloseShootAnimationState` | Animation-state transition helper that switches between close/shoot sequences based on current animation index and updates state field `+0x27c`. |
| `0x00472ad0` | `UISelectionList__AdvanceToNextEnabledWithWrap` | Owner-corrected UI selection helper: advances to next enabled item with wrap-around and plays move SFX when selection changes. |

## Headless Semantic Wave82 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00591050` | `CFastVB__ReleaseOwnedObjectAndReset` | Releases owned sub-object via vfunc(`+0x28`) then clears local state fields (`+0x04`, `+0x14`). |
| `0x00592b00` | `CFastVB__ParserContext_Shutdown` | Parser-context shutdown path: virtual cleanup, release/reset helper call, terminal callback dispatch. |
| `0x00592c50` | `CFastVB__ParserContext_Init` | Parser-context constructor/init seeding callback slots and default `"Bogus message code"` diagnostic string. |
| `0x00599258` | `CFastVB__ComputeNodeSpanAndStride` | Recursive node-kind walk computing aggregate span/stride metrics with error return on unsupported node types. |
| `0x00599878` | `CFastVB__CloneNodeTreeWithAddRef` | Clone allocator copying node state and AddRef-cloning child/interface references with failure cleanup. |

---

## Headless Semantic Wave83 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00598a56` | `CFastVB__InitNodeType9` | Node-type 9 initializer binding vtable `0x005ef250` and default field state. |
| `0x00598f82` | `CFastVB__NodeType9_scalar_deleting_dtor` | Scalar-deleting destructor for node-type 9, restoring vtable and freeing on delete-flag. |
| `0x00598b48` | `CFastVB__InitNodeType10` | Node-type 10 initializer binding vtable `0x005ef260` and zeroing owned-child/resource pointers. |
| `0x00598b81` | `CFastVB__NodeType10_dtor` | Node-type 10 destructor body releasing child/interface pointers and base storage cleanup. |
| `0x00598fa4` | `CFastVB__NodeType10_scalar_deleting_dtor` | Scalar-deleting wrapper over node-type 10 destructor with optional free flag. |

---

## Headless Semantic Wave84 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x005988f5` | `CFastVB__CompareNodeValuesByTagAndPayload` | Typed payload comparator handling scalar, string, pointer, and wide-string payload forms by tag. |
| `0x00598873` | `CFastVB__CloneNodeChainWithAddRef` | Clones linked node chain and AddRef-copies referenced payload objects, aborting with rollback on failure. |
| `0x00598d6b` | `CFastVB__InitNodeType13` | Node-type 13 initializer binding vtable `0x005ef270` and defaulting storage fields. |
| `0x00599b13` | `CFastVB__SetParseErrorAndMarkStateDirty` | Emits parse-diagnostic text and marks parser state/error flags dirty. |
| `0x00599b69` | `CFastVB__NodeTreeHasBitFlag0x200` | Recursive node-tree predicate returning whether payload bit `0x200` is present. |

---

## Headless Semantic Wave85 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00592530` | `CFastVB__JpegParser_ReadAndValidateSOI` | Validates JPEG SOI marker and parser preconditions before frame decode flow. |
| `0x005913b0` | `CFastVB__JpegParser_ResetFrameState` | Clears parser/frame accumulators and resets component-state fields for restart. |
| `0x00591720` | `CFastVB__JpegParser_ParseSOFComponents` | Parses SOF component descriptors, sampling factors, and quant/Huffman selector fields. |
| `0x00596589` | `CFastVB__SolveScalarEndpointPairFromSamples` | Solves scalar endpoint pair from sample spans for block-compression fit path. |
| `0x005968a4` | `CFastVB__SolveVectorEndpointPairFromSamples` | Solves vector endpoint pair from weighted samples for compression endpoint fitting. |

---

## Headless Semantic Wave86 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00596e23` | `CFastVB__QuantizeScalarBlockIndices` | Quantizes scalar samples into selector indices with iterative residual distribution. |
| `0x00597a61` | `CFastVB__PackScalarBlock_4BitEndpoints` | Packs 16 scalar samples into 4-bit endpoint/index representation. |
| `0x00597b87` | `CFastVB__PackScalarBlock_InterpolatedEndpoints` | Computes/interpolates scalar endpoints and emits per-sample selector indices. |
| `0x0059c610` | `CFastVB__ReleaseOwnedObjectAndReset_Core` | Core helper releasing owned object via vfunc(+0x28) and zeroing state fields. |
| `0x0059c700` | `CFastVB__CopyBlockRows128Bytes` | Copies `param_3` rows of 128-byte block data between buffers. |

---

## Headless Semantic Wave87 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0059a21f` | `CFastVB__AreNodeTreesCompatible` | Recursively compares node trees/types with exact-vs-compatible match mode. |
| `0x0059a54d` | `CFastVB__ScoreNodeTreeMatch` | Computes match score between requested/candidate node trees under flag-gated direction rules. |
| `0x0059a71a` | `CFastVB__SelectBestNodeTreeMatch` | Scans candidate lists and selects minimal-score compatible node-tree match with tie handling. |
| `0x00598f60` | `CFastVB__NodeType8_scalar_deleting_dtor` | Scalar-deleting destructor wrapper resetting node-type-8 vtable and freeing when flagged. |
| `0x005997a5` | `CFastVB__InitNodeType17` | Initializes node-type-17 storage, clears owned fields, and binds vtable `0x005ef374`. |

---

## Headless Semantic Wave88 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00598474` | `CFastVB__InitDispatchOpsFromFeatureFlags` | Initializes dispatch-operation slots from runtime feature-flag checks and profile capabilities. |
| `0x0059f6dd` | `CFastVB__BroadcastMatrix4x4ToSIMDLanes` | Expands matrix elements into SIMD lane layout consumed by vector transform dispatch ops. |
| `0x005a2a61` | `CFastVB__DispatchOp_TransformVec2ByMatrix4` | Dispatch op that transforms 2D coordinate pairs through matrix-backed parameter blocks. |
| `0x005aa0cc` | `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar` | Scalar composition path combining optional transform inputs into destination state. |
| `0x005aa2f2` | `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD` | SIMD composition path combining optional transform inputs into destination state. |

---

## Headless Semantic Wave89 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x005a38c0` | `CFastVB__DispatchOp_TransformVec4ArrayByMatrix4` | Iterates source vectors and applies 4x4 matrix multiplication into destination buffer using configurable source/destination strides. |
| `0x005a47f2` | `CFastVB__DispatchOp_ExtractAxisAndOptionalAngle` | Copies axis-vector components and optionally computes an angle-like scalar metric via trigonometric helper path. |
| `0x005a7617` | `CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles` | Evaluates trigonometric terms and writes a 4x4 rotation matrix-style block to output. |
| `0x005a7cf0` | `CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector` | Normalizes axis-angle input and emits a 4x4 rotation matrix-style block. |

---

## Headless Semantic Wave90 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x005b3440` | `CFastVB__JpegEntropy_EncodeBlockZigZagHuffman` | Iterates zig-zag block coefficients and emits entropy-coded symbols/bits through the bitstream helper with run-length handling. |
| `0x005b35b0` | `CFastVB__JpegEntropy_WriteMarkerAndResetDcPredictors` | Emits marker bytes into entropy stream and clears per-component predictor/state accumulators. |
| `0x005b86c0` | `CFastVB__FastAcosApprox_Scalar` | Scalar trigonometric approximation kernel used in axis/angle extraction helper paths. |
| `0x005b8ca0` | `CFastVB__FastTrigPairApprox_Scalar` | Scalar trigonometric pair approximation kernel used by rotation-matrix dispatch builders. |

---

## Headless Semantic Wave91 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x005a7e09` | `CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms` | Multi-branch dispatch path composing output matrix from optional transform inputs and basis blocks. |
| `0x005ad590` | `CFastVB__JpegEntropy_CommitAndResetBlockState` | Commits entropy-buffer progress counters and resets per-block working state before next encode block. |

---

## Headless Semantic Wave92 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0055f506` | `CRT__FReadCore` | Core CRT `fread` helper dispatching buffered read logic with item-size/count parameters. |
| `0x0055f5ee` | `Win32__FindFirstFileWithMeta` | Wrapper around `FindFirstFile` path with metadata copyout into caller struct. |
| `0x0055f6bb` | `Win32__FindNextFileWithMeta` | Wrapper around `FindNextFile` path with metadata copyout into caller struct. |
| `0x0055fe26` | `CRT__LockRouteByAddress` | Routes lock/unlock path by encoded address class in CRT lock table. |
| `0x0055fe55` | `CRT__LockRouteByIndex` | Routes lock/unlock path by lock-index mode and updates CRT lock bookkeeping. |

---

## Headless Semantic Wave93 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0055f2e8` | `CRT__WcsCmp` | Compares two UTF-16 code-unit strings and returns lexical {-1,0,1} ordering. |
| `0x0055f783` | `Win32__FindCloseWithErrno` | Calls `FindClose`; on failure writes CRT errno `0x16` and returns -1. |
| `0x0055fe78` | `CRT__UnlockRouteByAddress` | Address-based unlock router pairing with `CRT__LockRouteByAddress`; dispatches to lock-bank helper or `LeaveCriticalSection`. |
| `0x0055fea7` | `CRT__UnlockRouteByIndex` | Index-based unlock router pairing with `CRT__LockRouteByIndex`; dispatches to lock-bank helper or `LeaveCriticalSection`. |
| `0x0055feec` | `CRT__FTellAdjusted` | Computes stream position with text-mode newline adjustments and seek fallback handling. |

---

## Headless Semantic Wave94 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0055eb3d` | `CRT__RoundToIntegerRespectingControlWord` | Rounds a double using current FPU control-word semantics with explicit non-finite/inexact handling branches. |
| `0x0055ec4a` | `CRT__HeapAllocBase` | CRT allocation base helper: attempts small-block heap routes under runtime heap mode and falls back to `HeapAlloc`. |
| `0x0055f085` | `CRT__FreeBase` | CRT free base helper: routes pointer release through small-block metadata when available, otherwise falls back to `HeapFree`. |
| `0x0055f0ef` | `CRT__UnlockHeapLock` | Unlock wrapper paired with heap lock acquire path (`*_00561179(9)` -> `*_005611da(9)`). |
| `0x0055f147` | `CRT__UnlockHeapLock_Alt` | Alternate unlock wrapper in the same heap-lock route family, used by a second runtime free path. |

---

## Headless Semantic Wave95 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0055da8d` | `CRT__InitFloatConversionDispatchTable` | Initializes CRT float-conversion callback dispatch pointers (`__cfltcvt`, `__fassign`, and related handlers). |
| `0x0055dccd` | `CRT__Acos` | Arccosine math helper with FPU-control handling, domain checks, and one-argument error-exit path. |
| `0x0055df28` | `CRT__OnexitTablePush` | Appends callback pointer into CRT onexit table and grows storage when capacity is exhausted. |
| `0x0055dfa6` | `CRT__RegisterOnexitFunction` | Wrapper over onexit-table push path returning CRT success/failure convention. |
| `0x0055e42a` | `Win32__CaptureSystemTimeAsFileTimeTicks` | Captures current system `FILETIME` and stores combined 64-bit tick value in global state. |

---

## Headless Semantic Wave96 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0055d6a0` | `CRT__SehPopExceptionFrameAndJump` | Pops one exception-registration frame (`ExceptionList = *ExceptionList`) and tail-jumps through the supplied callback pointer. |
| `0x0055d6db` | `CRT__SehLockUnlockAndJump` | Emits lock/unlock pair then tail-jumps to callback target in SEH frame plumbing path. |
| `0x0055d6e2` | `CRT__SehRtlUnwindAndRestoreFrame` | Calls `RtlUnwind`, clears unwind-state flag bit, and restores exception-list linkage for local unwind continuation. |
| `0x0055d767` | `CRT__SehInvokeCallSettingFrame12` | Builds temporary exception frame with callback `0x0055d7bb` and dispatches via `__CallSettingFrame_12`. |
| `0x0055d7bb` | `CRT__SehCallback_Call_005602d2` | SEH frame callback target forwarding control to `CRT__SehDispatchWithScopeTable`. |

---

## Headless Semantic Wave97 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0055da5e` | `CRT__SehStoreFrameGlobals` | Stores frame/EAX context into CRT globals consumed by subsequent runtime bridge helpers. |
| `0x0055da76` | `CRT__InitRuntimeFromStoredFrameGlobals` | Runtime bridge init helper chaining conversion/setup routines from stored frame context globals. |
| `0x0055db72` | `CRT__EhVectorDestructorIterator_IfNoException` | Calls `eh_vector_destructor_iterator` only when exception-state guard indicates normal completion path. |
| `0x0055e412` | `CRT__CallHelper_00564a0b_NoFlags` | Thin wrapper forwarding args to helper `0x00564a0b` with trailing flag fixed to zero. |
| `0x0055e45f` | `CRT__CallHelper_00564c09_WithAutoUnlock` | Acquires lock context object, dispatches helper `0x00564c09`, then unlocks through address-routed unlock helper. |

---

## Headless Semantic Wave98 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0056004d` | `CDXTexture__AsciiToLowerInPlace` | Walks C-string bytes and lowercases ASCII `A..Z` in-place, with lock-guarded fallback path when runtime mode flags are enabled. |
| `0x00560b2c` | `CTexture__InitializeThreadLocalState` | Allocates TLS slot/record, installs per-thread state, applies record defaults, and stores current thread id. |
| `0x00560b80` | `CTexture__InitializeThreadLocalRecordDefaults` | Seeds per-thread texture record defaults (`+0x50` dispatch/vtable pointer and active/default flag at `+0x14`). |
| `0x00561150` | `CTexture__InitializeGlobalCriticalSections` | Initializes the four global texture/runtime critical sections used by locking routes. |
| `0x005602ae` | `CDXTexture__ReportFatalAndExitProcess` | Executes fatal-report helper chain then terminates process via `ExitProcess(0xff)`. |

---

## Headless Semantic Wave99 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00560bfa` | `CDXTexture__InvokeTlsCleanupCallbackAndFinalize` | Invokes optional TLS-context cleanup callback (`context+0x60`) and always executes common finalize helper afterward. |
| `0x00560c5b` | `CDXTexture__InvokeGlobalCleanupCallbackAndFinalize` | Invokes global cleanup callback pointer when present, then executes shared finalize helper path. |
| `0x00560d01` | `CDXTexture__ProbeProcessorFeaturePresentOrFallback` | Resolves `IsProcessorFeaturePresent` dynamically from `KERNEL32`; when unavailable, executes fallback feature gate helper. |
| `0x0055dd7b` | `CFastVB__RunStaticInitRangesWithOptionalCallback` | Executes optional callback pointer then processes two static init-range tables through shared helper dispatch. |
| `0x0055e183` | `CFastVB__DispatchLockedRoute_6533e0` | Locks route index 1 for key `0x6533e0`, dispatches helper call, then unlocks route. |

---

## Headless Semantic Wave100 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x005602d2` | `CRT__SehDispatchWithScopeTable` | Central SEH dispatch callback that validates scope sentinel/version state and routes to handler lookup or unwind logic. |
| `0x0056036d` | `CRT__SehLookupAndInvokeScopeHandler` | Walks scope records, checks state ranges, probes callback table, and invokes matching handler path. |
| `0x00560627` | `CRT__SehUnwindToTargetState` | Iteratively unwinds scope-table states toward target index, invoking cleanup callbacks via `__CallSettingFrame_12`. |
| `0x005606c5` | `CRT__SehUnwindAndResumeSearch` | Performs cleanup/unwind continuation and resumes exception-search dispatch via returned callback target. |
| `0x00560cb1` | `CRT__InitFpuControlWord_0x10000_0x30000` | Initializes runtime FPU control configuration through helper call with fixed mask/value pair. |

---

## Headless Semantic Wave101 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x0055fc35` | `CRT__IsFloat10Integral_0055fc35` | Compares rounded floating input to original value and follows integral/non-integral branch gate logic. |
| `0x00561590` | `CRT__Exp2FromFpuCore_00561590` | Uses classic FPU `f2xm1` + `fscale` sequence to build power-of-two exponentiation result. |
| `0x005615a5` | `CRT__SetFpuControlWordMasked_005615a5` | Applies masked FPU control-word update (`(arg & 0x300) | 0x7f`) and loads it via `FLDCW`. |
| `0x005615bc` | `CRT__MapExponentFlagToClassCode_005615bc` | Maps exponent/flag bit check (`0x80000`) to runtime class code (`7` or `1`). |
| `0x00561618` | `CRT__ExtractFiniteExponentMaskOrPassThrough_00561618` | Returns exponent-mask bits for finite values and pass-through bits for infinity/NaN patterns. |

---

## Headless Semantic Wave102 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00560e28` | `CRT__FormatFloatScientificFromLongDouble` | Wrapper path that converts long-double decomposition and delegates to scientific core formatter. |
| `0x00560e89` | `CRT__FormatFloatScientificCore` | Emits sign, decimal separator, mantissa span, and `e+000` exponent suffix for scientific-format output. |
| `0x00560f4b` | `CRT__FormatFloatFixedFromLongDouble` | Wrapper path that converts long-double decomposition and delegates to fixed-format core formatter. |
| `0x00560fa0` | `CRT__FormatFloatFixedCore` | Emits fixed decimal-format float text with sign/integer/fraction padding rules. |
| `0x00561047` | `CRT__FormatFloatGeneral_SelectStyle` | General-format selector choosing scientific vs fixed path using exponent-window thresholds (`%g`-style). |

---

## Headless Semantic Wave103 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x005615a5` | `CRT__SetFpuControlWordMasked_005615a5` | Correction of prior over-broad label: disassembly shows control-word masking and `FLDCW`, not a no-op path. |
| `0x0055d731` | `CRT__SehDispatchWithScopeTable_Thunk_0055d731` | Simple thunk forwarding directly to `CRT__SehDispatchWithScopeTable`. |
| `0x0055fa62` | `CRT__PowCore_0055fa62` | Disassembly-driven promotion: includes `FYL2X` + exp2 flow and edge-case branches consistent with CRT `pow` core implementation. |
| `0x00561530` | `CRT__ReportMathErrorAndRestoreControlWord_00561530` | Wraps math-error helper dispatch (`0x00569cc1`) and restores previously saved FPU control word on return. |
| `0x00560d2a` | `CRT__InsertDecimalSeparatorBeforeExponent_00560d2a` | Formatting helper inserts locale decimal separator and shifts mantissa tail before exponent marker. |

---

## Headless Semantic Wave104 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x004ae110` | `CMeshPart__StartTriangleBucketSearch` | Calls `CPolyBucket__StartSearch` and maps returned local triangle indices into mesh-triangle pointer slots. |
| `0x004ae1a0` | `CMeshPart__GetNextTriangleFromBucketSearch` | Calls `CPolyBucket__GetNextTriangle` and maps next local triangle indices into mesh-triangle pointer slots. |
| `0x004ae220` | `CMeshPart__StartLineTriangleBucketSearch` | Calls `CPolyBucket__StartLineSearch` and maps returned local line-triangle indices into mesh-triangle pointer slots. |
| `0x004ae430` | `CMeshPart__GetNextLineTriangleFromBucketSearch` | Calls `CPolyBucket__GetNextLineTriangle` and maps next local line-triangle indices into mesh-triangle pointer slots. |
| `0x004ae640` | `CMeshPart__FreeOwnedResourcePointers_004ae640` | Frees numerous OID-owned mesh-part resource pointers/arrays and releases influence-map runtime buffers. |

---

## Headless Semantic Wave105 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00423840` | `CChunkerStream__DestroyOwnedChunkerIfPresent` | Shared loader helper called from `CMesh__Deserialize`, `CResourceAccumulator__ReadResourceFile`, and `CCutscene__Load`; conditionally runs `CChunker__Destructor` + `OID__FreeObject` on owned chunker pointer. |
| `0x00423900` | `CChunkerStream__CloseDXMemBuffer_Status0OrMinus1` | Thin close wrapper around `DXMemBuffer__Close` returning normalized status code (`0`/`-1`) used at loader teardown boundaries. |
| `0x00423990` | `CChunkerStream__SkipRemainingChunkBytes` | Chunk-stream helper that advances to end-of-chunk by skipping `chunk_size - consumed_bytes`; called from world/mesh/cutscene/texture chunk loops when unknown/ignored chunks are encountered. |
| `0x0047e8a0` | `CUnitAI__FreeOwnedObjects_24_1028` | Cleanup helper that frees two optional OID-owned pointers (`+0x24` and `+0x1028`) and nulls both fields. |
| `0x00490f40` | `CUnitAI__ReleaseOwnedObjectsAndDestroyMixerMap` | Shutdown wrapper that invokes `CUnitAI__FreeOwnedObjects_24_1028` then tail-calls `CMixerMap__Destroy`; matches sound-system teardown call chain. |

---

## Headless Semantic Wave106 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x004238c0` | `CChunkerStream__OpenReadAndGetChunker` | Shared loader-open helper called from `CMesh__Deserialize`, `CResourceAccumulator__ReadResourceFile`, and `CCutscene__Load`; clears local counters, opens DX memory buffer read context, and returns chunker pointer on success. |
| `0x0044a690` | `RenderState__Set0x89_Zero` | Thin render-state wrapper used by debug draw path; emits `RenderState_Set(0x89, 0)`. |
| `0x0044a6b0` | `CDXEngine__ApplyNavMapConsoleToggle_Thunk` | Called by `con_navmapon` / `con_navmapoff`; forwards to DX-engine navmap update helper after global toggle flag update. |
| `0x0046a1f0` | `CUnitAI__GetStringByResolvedTextIdAfter` | Resolves text id through helper `0x00469cf0` and forwards to `CText__GetStringByIdAfter`. |
| `0x0046a220` | `CUnitAI__GetMultiplayerLevelDescriptionByType` | Switch-based multiplayer description resolver returning known text IDs, with explicit `"Unknown Multiplayer Level Description"` fallback path. |

---

## Headless Semantic Wave107 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00430fa0` | `CStatementChain__InvokeVFunc04OnNodes` | Called by multiple statement vfunc-01 constructors (`Weapon/Mode/Round/Spawner/Explosion/Component/Feature/Hazard`) to walk linked nodes and invoke target vfunc slot `+0x04`. |
| `0x00415140` | `CUnitAI__HandleLandedStateTransition_00415140` | Emits `"landed"` trace once, resets transient state fields, calls landing-related virtual hooks, and sets landed-state flag to `1`. |
| `0x00408120` | `CUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120` | Returns true only when mode/state field (`+0x260`) equals `2` and global height delta check against `+0xcc` is below threshold constant. |
| `0x00421c40` | `CUnit__ApplyFlag4DampingAndScaleSpeed_00421c40` | When flag bit `0x04` is active, applies damping defaults to movement fields, scales speed at `+0x11c`, then calls follow-up movement update helper. |
| `0x004063a0` | `CBattleEngine__GetFloatAt0x118_AsDouble` | Thin accessor returning float field `+0x118` promoted to double. |

---

## Headless Semantic Wave108 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00412570` | `CBattleEngine__IsIndexedEntryUsable` | Iterates indexed entry list and evaluates per-type readiness gates (state/cooldown/comparison checks) to return usable/not-usable status for the selected entry slot. |
| `0x00412610` | `CBattleEngine__GetIndexedEntry` | Returns pointer to the currently selected indexed entry (`list[index]`) from the same entry-list structure used by `CGeneralVolume__ResolveCurrentOrFallbackEntry`. |
| `0x00414630` | `CBattleEngine__IsResolvedEntryUsable` | Resolves current/fallback entry first, then applies the same readiness checks as `CBattleEngine__IsIndexedEntryUsable`; returns boolean eligibility for resolved entry. |
| `0x0042ee90` | `CUnitAI__CreateAndRegisterByName` | Allocates a `0x1ac` AI object, initializes internal pointer sets/name storage, calls defaults init, applies Fenrir special-case flag, then adds object to global registry set. |
| `0x0042efd0` | `CUnitAI__InitDefaults` | Constructor-style defaults initializer: zeroes/sets core AI fields, allocates and stores `"m_b_rubble"` key string, initializes scalar defaults/thresholds, and resets runtime pointers/state. |

---

## Headless Semantic Wave109 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00415970` | `CUnitAI__HandleDeployUndeployAnimationCompletion` | Handles deploy/undeploy animation completion edge, resets transition state, and returns completion status used by higher-level deploy-state flow. |
| `0x00424a20` | `CUnitAI__UpdateDeployAimAndScheduleEvent` | Updates deploy-aim progression and schedules follow-up deploy event timing in the AI transition pipeline. |
| `0x00424be0` | `CUnitAI__AdvanceDeployAnimationPhase` | Advances deploy animation phase state machine to the next phase and commits phase-specific state updates. |
| `0x00425760` | `CUnitAI__OrthonormalizeMat34Axes` | Re-orthonormalizes transform basis vectors for a mat34-style block to maintain stable orientation math. |
| `0x0042f280` | `CUnitAI__ComputeRecursiveNodeSize_Base8` | Computes recursive node-size totals with base element size 8 bytes for AI-owned tree/graph memory sizing paths. |

---

## Headless Semantic Wave110 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00415780` | `CUnitAI__PlayDeployingAnimationIfState0` | If current transition state is `0`, resolves `"deploying"` animation and plays it, then sets transition state to `1`. |
| `0x004157c0` | `CUnitAI__PlayUndeployingAnimation` | Resets deploy timer field and plays `"undeploying"` animation sequence via `FindAnimationIndex`. |
| `0x00445570` | `CUnitAI__PlayOpenAnimationIfState1Or3` | When state field (`+0x280`) is `1` or `3`, sets it to `2` and plays animation string `"open"`. |
| `0x004455c0` | `CUnitAI__PlayCloseAnimationIfState0Or2` | When state field (`+0x280`) is `0` or `2`, sets it to `3` and plays animation string `"close"`. |
| `0x00445610` | `CUnitAI__AdvanceOpenCloseShootAnimationState` | Checks current animation index and advances between `"open"`, `"close"`, and `"shoot"` phases while updating state field (`+0x280`). |

---

## Headless Semantic Wave111 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00415a50` | `CUnitAI__CanCompleteDeployUndeployTransition` | Returns ready/true only when transition animation has ended and gating flags permit completion of deploy/undeploy transition. |
| `0x00424ca0` | `CUnitAI__UpdateDeployTrackingTransformTowardTarget` | Computes target-facing deploy tracking transform (including clamped angular deltas) and writes updated orientation basis. |
| `0x004250f0` | `CUnitAI__DecayDeployTrackingTransformToNeutral` | Decays deploy tracking offsets toward neutral and rebuilds orientation transform from decayed angles. |
| `0x00430b30` | `CUnitAI__ComputeRecursiveNodeSize_NodeTreeA` | Recursively accumulates node-tree memory size as `node_size + 0xC + child_size` for tree-A chain nodes. |
| `0x00431470` | `CUnitAI__ComputeRecursiveNodeSize_NodeTreeB` | Same recursive node-size accumulator pattern as wave111 tree-A helper, applied to tree-B chain nodes. |

---

## Headless Semantic Wave112 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x004015e0` | `CUnit__IntegrateVelocityAndResolveGroundCollision` | Integrates position from velocity, resolves ground contact/normal response, and updates map-entry position tracking. |
| `0x00403690` | `CUnit__ReleaseAllAttachedParticleNodes` | Releases both attached particle-node sets by removing entries, unlinking particle manager state, and freeing objects. |
| `0x00408150` | `CUnit__ProcessStateSwapAndDeathChecks` | Runs state-swap helper, processes pickup/death-path checks by flags/altitude, then executes shared unit post-step helper. |
| `0x004102a0` | `CBattleEngine__DestroySPtrSetElementsAndClear` | Iterates SPtrSet entries, removes + destroys each element via virtual dtor call, then clears the set container. |
| `0x004318c0` | `CUnitAI__ComputeRecursiveNodeSize_NodeTreeC` | Third recursive node-size accumulator variant (`node + 0xC + child`) for adjacent CUnitAI node-tree chain. |

---

## Headless Semantic Wave113 Promotions (2026-02-26)

| Address | Symbol | Behavior Evidence |
|---------|--------|-------------------|
| `0x00407310` | `CBattleEngine__IsCurrentResolvedEntry` | Resolves current entry (indexed/fallback path by state) and returns true when it matches the provided entry pointer. |
| `0x004178a0` | `CUnit__ProcessClosingAndUnshuttingAnimations` | Drives closing/unshutting animation state transitions based on timing and flag gates, including `closing`/`unshutting` animation dispatch. |
| `0x004239f0` | `CUnitAI__InitDefaults_AutoConfigTestPath` | Constructor-style defaults initializer that seeds many runtime fields and stores `c:\\beaautoconfigtest\\` path string in object state. |
| `0x00428c70` | `CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action` | Executes shared step helper and conditionally invokes flag-4 gated action callback. |
| `0x00428cf0` | `CUnitAI__ForwardCommandToAttachedNodeThenDispatch` | Forwards command to attached node when present/allowed, then executes common follow-up dispatch helper. |

---

## Section Layout (Data Sections)

### 0x0062xxxx - String Data (Debug Paths, Error Messages)

| Range | Content |
|-------|---------|
| 0x00622000-0x00624FFF | Debug paths (AirUnit.cpp - chunker.cpp) |
| 0x00625000-0x00627FFF | Debug paths (Controller.cpp - game.cpp), error strings |
| 0x00628000-0x0062AFFF | Debug paths (engine.cpp - FEPSaveGame.cpp) |
| 0x0062B000-0x0062DFFF | Debug paths (FrontEnd.cpp - Mech.cpp) |
| 0x0062E000-0x0062FFFF | Debug paths (MCMech.cpp - MeshRenderer.cpp) |
| 0x00630000-0x00633FFF | Debug paths (Mine.cpp - Unit.cpp) |
| 0x00634000-0x0063FFFF | Debug paths (vbuffer.cpp - mixermap.cpp) |

### 0x006220b0 - Init Function Pointer Table

This region is not string data; it is a small function-pointer table used during startup/static initialization.

| Address | Name | Type | Notes |
|---------|------|------|------|
| 0x006220b0 | g_InitFuncTable | pointer[16] | Table entries point at small init routines (often shown as labels like `LAB_0041b6a0`). MCP `functions_create` can fail on these targets; preferred workflow is manual CodeBrowser function creation (`F` at the first instruction), then serialized MCP rename/signature/comment with immediate read-back. |

Known entries (absolute VAs):
- `g_InitFuncTable[0]` = `0x0041b0d0`
- `g_InitFuncTable[1]` = `0x0041b5b0`
- `g_InitFuncTable[2]` = `0x0041b5d0`
- `g_InitFuncTable[3]` = `0x0041b6a0` (`CCareer__StaticInitDefaults`: global CAREER defaults initializer: nodes/links/goodies + sound/music/controller/invert-Y defaults; Steam invert-Y semantics `0=Off`, non-zero=On)
- `g_InitFuncTable[4]` = `0x00421990`
- `g_InitFuncTable[5]` = `0x004219b0`
- `g_InitFuncTable[6]` = `0x00421cc0`
- `g_InitFuncTable[7]` = `0x00421ce0`
- `g_InitFuncTable[8]` = `0x00421ea0`
- `g_InitFuncTable[9]` = `0x00421ec0`
- `g_InitFuncTable[10]` = `0x00422350`
- `g_InitFuncTable[11]` = `0x00422370`
- `g_InitFuncTable[12]` = `0x004229b0`
- `g_InitFuncTable[13]` = `0x004229d0`
- `g_InitFuncTable[14]` = `0x00422ea0`
- `g_InitFuncTable[15]` = `0x00422ec0`

### 0x0064xxxx - MissionScript & DirectX Debug Paths

| Range | Content |
|-------|---------|
| 0x0064C000-0x0064FFFF | MissionScript subfolder debug paths |
| 0x00650000-0x00652FFF | DirectX (DX*) debug paths |

### 0x0062xxxx - Cheat System Data

| Address | Size | Content |
|---------|------|---------|
| 0x00629464 | 256 | Cheat code 0: MALLOY (XOR encrypted) |
| 0x00629564 | 256 | Cheat code 1: TURKEY (XOR encrypted) |
| 0x00629664 | 256 | Cheat code 2: V3R5IOF (decoded) |
| 0x00629764 | 256 | Cheat code 3: Maladim (XOR encrypted) |
| 0x00629864 | 256 | Cheat code 4: Aurore (XOR encrypted) |
| 0x00629964 | 256 | Cheat code 5: lat\xEate (decoded, non-ASCII) |
| 0x00629a64 | 9 | XOR key: "HELP ME!!" |

**Note (Feb 2026)**: XOR decoding the cheat table in this BEA.exe build yields `V3R5IOF` at index 2, not `V3R5ION`. Index 5 also decodes to a non-ASCII string (`latête`). Both need in-game confirmation.

### 0x00625xxx - Options/UI Globals (.data)

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x006254f0 | g_Options_UnknownFloat0 | float | Options tail float (default ~0.7), no refs outside options tail |
| 0x006254f4 | g_MouseSensitivity | float | Mouse sensitivity scalar (input/camera + UI) |

### 0x00630xxx - Rendering/Options Globals (.data)

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x00630e0c | g_MeshQualityScaleFactor | float | Mesh quality scale factor (set by CRTMesh__SetQualityLevel) |
| 0x00631e88 | g_MeshLodBias | float | `cg_meshlodbias` console variable |

### 0x0066xxxx - BSS (Runtime Globals)

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x00660620 | CAREER | CCareer | Global CCareer buffer base (Steam PC port). CCareer dump size is `0x24BC` bytes (`0x92F` dwords). |
| 0x00662aa8 | CAREER_mCareerInProgress | uint32 | CCareer `+0x2488` (file `0x248A`). Raw bool/int. Defaults to 0 in `CCareer__StaticInitDefaults`. |
| 0x00662aac | CAREER_mSoundVolume | float | CCareer `+0x248C` (file `0x248E`) |
| 0x00662ab0 | CAREER_mMusicVolume | float | CCareer `+0x2490` (file `0x2492`) |
| 0x00662ab4 | g_bGodModeEnabled | BOOL | CCareer `+0x2494` (file `0x2496`). Pause-menu toggle state (cheat-gated). |
| 0x00662ab8 | CAREER_unused_2498 | uint32 | CCareer `+0x2498` (file `0x249A`). Observed 0; treat as reserved/unused padding. |
| 0x00662abc | CAREER_mInvertYFlight_P1 | uint32 | CCareer `+0x249C` (file `0x249E`). Steam stores `0=Off`, non-zero=On (verified in `FUN_00407540`). |
| 0x00662ac0 | CAREER_mInvertYFlight_P2 | uint32 | CCareer `+0x24A0` (file `0x24A2`). Steam stores `0=Off`, non-zero=On (verified in `FUN_00407540`). |
| 0x00662ac4 | CAREER_mInvertYWalker_P1 | uint32 | CCareer `+0x24A4` (file `0x24A6`). Steam stores `0=Off`, non-zero=On (verification pending on walker path). |
| 0x00662ac8 | CAREER_mInvertYWalker_P2 | uint32 | CCareer `+0x24A8` (file `0x24AA`). Steam stores `0=Off`, non-zero=On (verification pending on walker path). |
| 0x00662acc | CAREER_mVibration_P1 | uint32 | CCareer `+0x24AC` (file `0x24AE`). `0=Off`, non-zero=On (gates controller vibration calls in `FUN_0042e750`). |
| 0x00662ad0 | CAREER_mVibration_P2 | uint32 | CCareer `+0x24B0` (file `0x24B2`). `0=Off`, non-zero=On. |
| 0x00662ad4 | CAREER_mControllerConfig_P1 | uint32 | CCareer `+0x24B4` (file `0x24B6`). Passed into `CController__Init` by `CGame__LoadLevel`. |
| 0x00662ad8 | CAREER_mControllerConfig_P2 | uint32 | CCareer `+0x24B8` (file `0x24BA`). Passed into `CController__Init` by `CGame__LoadLevel`. |
| 0x00662b20 | g_bNewGoodieFlag | BOOL | New goodie unlock flag |
| 0x00662b24 | g_bNewTechFlag | BOOL | New tech unlock flag |
| 0x00662dd0 | g_FrontendState | BOOL | Frontend active flag |
| 0x00662df4 | g_bDevModeEnabled | BOOL | Dev mode flag |
| 0x00662f3e | DAT_00662f3e | BOOL | **Guard flag for -forcewindowed** |
| 0x00662a14 | g_Career_mThingsKilled | int[5] | CCareer kill counters (g_Career + 0x23F4) |
| 0x00662564 | g_Career_mGoodies | int[300] | CCareer.mGoodies array (goodie states) |
| 0x0066061c | g_D3DDeviceIndex | int | Selected D3D adapter/device index (BuildDeviceList) |
| 0x0066306c | g_TryLockableBackbuffer | int | TRY_LOCKABLE_BB flag used during D3D init |
| 0x00663070 | g_InvertXAxisFlag | BOOL | Negates X in `CSoundManager__UpdateSoundPosition` (`0x004e1360`) for sound-pan/inversion logic. |
| 0x00663074 | g_SoundEnabledFlag | BOOL | Sound enable toggle (CPCSoundManager) |
| 0x00663078 | g_SoundDeviceIndex | int | DirectSound device index |
| 0x00663080 | g_SoundSampleRateIndex | int | Sample rate/bit depth index |
| 0x00663084 | g_Sound3DMethod | int | 3D sound method selection |
| 0x006321a0 | g_MeshQualityDistance | float | Mesh quality distance scalar (CRTMesh__Get/SetQualityLevel) |
| 0x0066e99c | g_pPhysicsScript | CPhysicsScript* | Physics script singleton |
| 0x006798b0 | g_Cheat_MALLOY | BOOL | Cheat flag set by IsCheatActive(0) |
| 0x006798b4 | g_Cheat_LATETE | BOOL | Cheat flag set by IsCheatActive(5) |
| 0x00679ec1 | g_bAllCheatsEnabled | BOOL | All cheats flag |
| 0x00679ec8 | g_DevModeTimer | int | Easter egg timing counter |
| 0x00679f9c | g_CheatCheckCounter | int | Frame counter |
| 0x00679fa0 | g_CheatCheckState | int | Directory/state tracking |
| 0x00672e30 | g_LevelKillCounts | int[5] | Per-level kill counts copied into CCareer totals |
| 0x00677d70 | g_ControlSchemeIndex | int | Control scheme / input preset index |
| 0x00677868 | g_ControlRemapSlotIndex | int | Remap pipeline: selected slot index (0/1) |
| 0x0067786c | g_ControlRemapActionCode | int | Remap pipeline: current action code |
| 0x00677870 | g_ControlRemapBindingType | int | Remap pipeline: binding type/category (used to map device_code) |
| 0x00677874 | g_ControlRemapVkScanPacked | uint32 | Remap pipeline: packed key state (vk/scan) |
| 0x00677878 | g_ControlRemapCurrentBindingType | int | UI renderer: current binding type (set by Controls__DispatchRemap callback at 0x00456060) |
| 0x0067787c | g_ControlRemapCurrentEntryId | int | UI renderer: entry_id currently being displayed/read |
| 0x00677d74 | g_ControlRemapArmed | byte | Capture state flag used by remap callback |

### 0x00629xxx - UI/Controls Globals (.data)

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x006290b4 | g_ControlRemapActive | byte | UI remap “active” flag (used for highlighting/animations) |

### 0x00672xxx - Core Runtime Singletons (.data/.bss)

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x00672fc8 | EVENT_MANAGER | CEventManager | Global event-manager singleton instance (`eventmanager.cpp`: `CEventManager EVENT_MANAGER`). Rename was applied successfully after defining the address as `dword` first (`data_create` -> `data_rename`), then verified by decompile read-back (`&EVENT_MANAGER`). |

### 0x0082xxxx+ - Instance Data

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x0082b468 | g_CVar_DisallowMipMapping | CVar | CVar object (value at +0xC = g_DisallowMipMapping) |
| 0x0082b478 | g_CVar_ScreenShape | CVar | CVar object (value at +0xC = g_ScreenShape) |
| 0x0082b474 | g_DisallowMipMapping | int | CVar: RENDERSTATE_DISALLOW_MIPMAPPING (0=allow, 1=disallow) |
| 0x0082b484 | g_ScreenShape | int | 0=4:3, 1=16:9, 2=1:1 |
| 0x00856f6c | g_ProfileMultisampleType | int | Per-profile override (D3DMULTISAMPLE_*). -1 => use g_SuggestMultisampleType |
| 0x0089c0a0 | g_CVar_AllowWidescreenModes | CVar | CVar object for ALLOW_WIDESCREEN_MODES (value at +0xC) |
| 0x0089c090 | g_CVar_CopyNotFlip | CVar | CVar object for COPY_NOT_FLIP (value at +0xC) |
| 0x0089c080 | g_CVar_SuggestMultisampleType | CVar | CVar object for SUGGEST_MULTISAMPLE_TYPE (value at +0xC) |
| 0x0089c070 | g_CVar_ForceVsync | CVar | CVar object for FORCE_VSYNC (value at +0xC) |
| 0x0089c0ac | g_AllowWidescreenModes | int | Value for ALLOW_WIDESCREEN_MODES CVar (0/1) |
| 0x0089c08c | g_SuggestMultisampleType | int | Value for SUGGEST_MULTISAMPLE_TYPE CVar (D3DMULTISAMPLE_*) |
| 0x0089c07c | g_ForceVsync | int | Value for FORCE_VSYNC CVar (0/1) |
| 0x0089bc30 | g_pOptionsContext | ptr | Options menu context pointer (was `DAT_0089bc30`) |
| 0x0089c0f4 | CD3DApplication* | ptr | D3D app instance |
| 0x008a1374 | g_pSaveGame | CFEPSaveGame* | Save game instance |
| 0x008a9d38 | DAT_008a9d38 | int | Appears to be the current level number (read by `CPlayer__GotoPanView` for half-pan level exceptions) |
| 0x0083d130 | g_SPtrSet_FreeListHead | ptr | SPtrSet node pool free-list head (each node: [value, next]) |
| 0x0083d134 | g_SPtrSet_PoolBase | ptr | SPtrSet node pool base pointer / init marker (0 if pool not initialised) |
| 0x0083d138 | g_SPtrSet_PoolNodeCount | int | Initial pool node count (set by CSPtrSet__Initialise) |
| 0x0083d13c | g_SPtrSet_OverflowAllocCount_AddToHead | int | Overflow alloc count for CSPtrSet__AddToHead (pool exhausted) |
| 0x0083d140 | g_SPtrSet_OverflowAllocCount_AddToTail | int | Overflow alloc count for CSPtrSet__AddToTail (pool exhausted) |
| 0x0083d97c | g_LanguageIndex | int | Language index for localization |
| 0x0083cfe8 | g_pSoundDefinitionListHead | ptr | Head of the 0xDC-byte SoundManager definition list (SoundManager.cpp) |
| 0x008aa95c | g_LandscapeMaxLevelsUser | int | CVar value: LANDSCAPE_MAXLEVELS_USER |
| 0x008aa950 | g_CVar_LandscapeMaxLevelsUser | CVar | CVar object for LANDSCAPE_MAXLEVELS_USER (value at +0xC = g_LandscapeMaxLevelsUser) |
| 0x008aa99c | g_LandscapeLowresGeom | int | CVar value: LANDSCAPE_LOWRES_GEOM |
| 0x008aa990 | g_CVar_LandscapeLowresGeom | CVar | CVar object for LANDSCAPE_LOWRES_GEOM (value at +0xC = g_LandscapeLowresGeom) |

### 0x009cxxxx - Graphics/Texture Options

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x009c7558 | g_MeshQualityLodTable | float[] | LOD threshold table set by CRTMesh__SetQualityLevel |
| 0x009c7c54 | g_LandscapeDetailLevel2 | byte | Landscape detail enum (see LandscapeDetail_GetLevel) |
| 0x009c7c56 | g_LandscapeDetailLevel1 | byte | Landscape detail enum (see LandscapeDetail_GetLevel) |
| 0x009cc0d8 | g_CVar_UserTextureAllow32Bit | CVar | CVar object for USER_TEXTURE_ALLOW_32_BIT (value at +0xC = g_UserTextureAllow32Bit) |
| 0x009cc0e4 | g_UserTextureAllow32Bit | int | CVar value: USER_TEXTURE_ALLOW_32_BIT (0/1) |
| 0x009cc0f8 | g_CVar_UserTextureResLossShift | CVar | CVar object for USER_TEXTURE_RES_LOSS_SHIFT (value at +0xC = g_UserTextureResLossShift) |
| 0x009cc104 | g_UserTextureResLossShift | int | CVar value: USER_TEXTURE_RES_LOSS_SHIFT (resolution loss shift) |

---

## Guard Flags (Feature Enable/Disable)

| Address (VA) | File Offset | Name | Value | Effect |
|--------------|-------------|------|-------|--------|
| 0x00662f3e | 0x262F3E | DAT_00662f3e | 0x01 (current repo binaries) | Retail default 0x00; current repo binaries have **-forcewindowed guard enabled** |

### Patch to Enable -forcewindowed

1. Open BEA.exe in hex editor
2. Go to file offset **0x262F3E**
3. Change byte from **0x00** to **0x01**
4. Save and run with `-forcewindowed`

---

## Key Function Addresses

### Save/Load System

| Address | Function | Description |
|---------|----------|-------------|
| 0x004213c0 | CCareer__SaveWithFlag | Serializes career to buffer (retail save path helper; flag behavior still being mapped) |
| 0x00421200 | CCareer__Load | Deserializes buffer to career (`flag=0`: boot/defaultoptions path, applies Sound/Music and options entries/tail globals; `flag!=0`: career `.bes` load, preserves pre-load Sound/Music and skips options entries/tail apply) |
| 0x00421430 | CCareer__GetSaveSize | Calculates dynamic save size |
| 0x00420b10 | OptionsTail_Write | Writes 0x56-byte globals/options tail block |
| 0x00420d70 | OptionsTail_Read | Reads 0x56-byte globals/options tail block |
| 0x00514f80 | PCPlatform__WriteSaveFile | Generic file write wrapper (savegames folder) |
| 0x00515080 | PCPlatform__ReadSaveFile | Generic file read wrapper (savegames folder) |
| 0x00464c50 | CFEPSaveGame__CreateSave | Save-menu handler (serializes CAREER and writes `savegames\\<name>.bes`) |
| 0x00461e20 | CFEPLoadGame__DoLoad | UI handler for load menu |
| 0x00462640 | CFEPMain__Process | Main-menu process loop; recovered owner for `CCareer__Save` callsite `0x00462893` and `CFEPOptions__WriteDefaultOptionsFile` callsite `0x004628df` |
| 0x00462250 | CFEPMain__ButtonPressed | Main-menu button handler (`0x2a/0x2b/0x2c/0x36/0x37`): selection moves, activate, and language-cycle branches |
| 0x00462b70 | CFEPMain__RenderPreCommon | Main-menu pre-render transition helper (alpha/scale prepass) |
| 0x00462d40 | CFEPMain__Render | Main-menu render path (transition-weighted surface/text draw flow) |
| 0x004644d0 | CFEPMain__TransitionNotification | Main-menu transition notification/reset hook (timer reseed + `CAREER_mCareerInProgress` mirror) |

### Frontend Goodies (FEPGoodies)

| Address | Function | Description |
|---------|----------|-------------|
| 0x0045c770 | CGoodieData__ctor | Initializes one `CGoodieData` row (`Method/Method2/Number/Number2/mT1/mT2`) used by static goodies table build path |
| 0x0045cb80 | get_goodie_number | Static goodies-grid helper `(x,y) -> goodie_id`, returns `-1` for invalid/unmapped cells |
| 0x0045c870 | CFEPGoodies__Deserialise | `GDIE` resource chunk deserializer called from `CResourceAccumulator__ReadResourceFile`; loads textures/mesh for current goody payload |
| 0x0045c9f0 | CFEPGoodies__StartLoadingGoody | Starts selected-goody async load pipeline and sets goody load state |
| 0x0045cc10 | CFEPGoodies__LoadingGoodyPoll | Polls async load completion and finalizes resource read/open state |
| 0x0045cd10 | CFEPGoodies__FreeUpGoodyResources | Releases current goody mesh/textures and resets goody load state |
| 0x0045d7e0 | CFEPGoodies__Process | Main goodies page process loop (cheat flags, selection/animation/update flow) |

### Frontend Level Select Helper

| Address | Function | Description |
|---------|----------|-------------|
| 0x0045d730 | CFEPLevelSelect__UpdateMouseEdgeSlide | Mouse-edge cubic slide/clamp helper used from `CFEPLevelSelect__Process` (`state`, `float* value`, `max=1100.0f`) |

### Game Core Lifecycle / Rendering

| Address | Function | Description |
|---------|----------|-------------|
| 0x0041ad30 | CInterpolatedCamera__ctor | Interpolated camera constructor used by engine viewpoint setup (`CCamera* -> interpolated wrapper`) |
| 0x0044a020 | CEngine__SetViewpoint | Source-aligned `CEngine::SetViewpoint(viewpoint,camera,viewport,player)` (copies viewport, stores player, rebuilds wrapped camera) |
| 0x0044a1c0 | CEngine__UpdatePos | Source-aligned `CEngine::UpdatePos(CCamera*)` landscape/tile update bridge used in main-loop viewpoint pass |
| 0x0046c360 | CGame__Init | Core game startup init (engine/imposters/render queue/static shadows/interface/HUD; returns startup success) |
| 0x0046c430 | CGame__InitRestartLoop | Per-level/restart runtime init (state reset, EventManager/particles/interface setup, command/CVar registration) |
| 0x0046ca70 | CGame__ShutdownRestartLoop | Per-level/restart teardown (runtime object frees, script/event/atmospherics/reset paths) |
| 0x0046cd30 | CGame__LoadResources | Level resource loader (resource accumulator + texture/mesh resources + particle set load) |
| 0x0046cdf0 | CGame__LoadLevel | Loads world/level data and creates per-player runtime object chain |
| 0x0046d040 | CGame__PostLoadProcess | Post-load validation/setup (atmospherics/start positions/map sort), returns readiness |
| 0x0046d470 | CGame__FillOutEndLevelData | Captures end-level summary/progression snapshot fields for post-level flows |
| 0x0046d810 | Cutscene_FormatPath_WithSmallFallback | Builds `cutscenes\\%02d` and rewrites to `_small` when `data\\video\\<name>.vid` is missing |
| 0x0046d890 | CGame__RunIntroFMV | Intro FMV flow (lookup type 0, path fallback, goodie unlock, playback, input flush) |
| 0x0046d9f0 | CGame__RunOutroFMV | Conditional outro FMV flow (lookup types 1/2 + level-specific variant selection + credits triggers) |
| 0x004726b0 | CGame__RollCredits | End-credits loop invoked by final-level outro routes; creates temporary controller handlers and runs credits render/update until completion/skip |
| 0x0046dbd0 | CWaitForStart__ctor | Restart-loop local helper: sets wait-sink vtable and zeros local state field (`+0x04`) |
| 0x0046dc00 | CGame__PlayMusicForCurrentLevel | Level-music selector (level 100 => tutorial track type 2, otherwise in-game track type 4) |
| 0x0046dc30 | CGame__RestartLoopRunLevel | Inner restart-loop pass (load/post-load/prerun/main-loop/cleanup; returns per-pass quit code) |
| 0x0046e240 | CGame__RunLevel | Top-level per-level driver (init/resources, restart-loop orchestration, shutdown/final quit code) |
| 0x0046e460 | CGame__Render | Main render path: frame timing, split-screen/fullscreen viewpoint setup, engine render passes |
| 0x0046e910 | CGame__Update | Core gameplay tick/update path (EventManager/controller/state/fade/control transitions) |
| 0x0046eee0 | CGame__MainLoop | Per-frame game loop (process/update/render/audio/frame-fraction timing) |
| 0x004e1b20 | CSoundManager__UpdateStatus | Per-frame sound-event update pass (`GAME.GetCamera` sync, attenuation/fade/debug-marker maintenance) |
| 0x0042d810 | CController__InactivityMeansQuitGame | Demo inactivity timeout guard checked by game/frontend main loops |
| 0x0042e4b0 | CController__GetToControl | Source-aligned top-of-stack control-target accessor (`mToControlStack.First()->ToRead()`) |
| 0x005145f0 | CPCController__ctor | PC controller ctor wrapper used by `CGame__LoadLevel` (calls `CController__Init`, then installs vtable `0x005e48e0`) |
| 0x0042d9d0 | CController__Flush | Copies `mButtons{1,2,3} -> Old`, clears current, then calls vtable+`0x3c` (`DoMappings`) |
| 0x0042db40 | CController__DoMappings | Main mapping engine (push_type switch) that drives `CController__SendButtonAction` |
| 0x004027c0 | VFuncSlot_00_004026e0__Unk_004027c0 | Event-branch helper reached from `VFuncSlot_00_004026e0` on event `0x7d1`; uses `CMapWho__GetFirstEntryWithinRadius` / owner scans. |
| 0x004028e0 | VFuncSlot_00_004026e0__Unk_004028e0 | Event-branch helper reached from `VFuncSlot_00_004026e0` on event `2000`; terrain/height-related branch (`CHeightField__Unk_0047ea20`). |
| 0x00403650 | Transform__Unk_00403650 | High-fanout 0x10-byte row copy helper used in monitor/unit/mesh-renderer paths; preserves sentinel behavior at `+0xAC`. |
| 0x005147b0 | CPCController__GetJoyButtonOnce | Joystick button “pressed once” (edge detect `0 -> 1`) using per-pad state tables (`old @ 0x00888fa4`, `current @ 0x00888f94`, byte @ `+0x30+button`) |
| 0x005147f0 | CPCController__GetJoyButtonOn | Joystick button “held” (current state) using per-pad state table (`current @ 0x00888f94`, byte @ `+0x30+button`) |
| 0x00514810 | CPCController__GetJoyButtonRelease | Joystick button “released” (edge detect `1 -> 0`) using per-pad state tables (`old @ 0x00888fa4`, `current @ 0x00888f94`, byte @ `+0x30+button`) |
| 0x00514850 | CPCController__GetKeyOnce | Key “once” (read+clear) from `0x00888d94[key]` |
| 0x00514890 | CPCController__GetKeyOn | Key “on” (held) from `0x00888c94[key]` |
| 0x00514870 | CPCController__GetKeyState3 | Third key table read from `0x00888e94[key]` (semantics TBD) |
| 0x00514640 | CPCController__GetJoyAnalogueLeftX | Joystick state `+0x00` scaled by `0.001` |
| 0x00514670 | CPCController__GetJoyAnalogueLeftY | Joystick state `+0x04` scaled by `0.001` |
| 0x005146a0 | CPCController__GetJoyAnalogueRightX | Joystick state `+0x08` scaled by `0.001` |
| 0x005146d0 | CPCController__GetJoyAnalogueRightY | `(state+0x14 - 32768)/32768` (guarded) |
| 0x005148b0 | CPCController__GetJoyPovX | `sin(POV * 0.00017453294)` (POV=-1 => 0) |
| 0x00514900 | CPCController__GetJoyPovY | `-cos(POV * 0.00017453294)` (POV=-1 => 0) |
| 0x00514720 | CPCController__RecordControllerState | Writes `mButtons1/2/3` (`this+0x14/+0x18/+0x1c`) into controller `DXMemBuffer` |
| 0x00514760 | CPCController__ReadControllerState | Reads `mButtons1/2/3`; on EOF closes buffer and clears playback flag (`this+0x161=0`) |
| 0x0046f2c0 | CGame__GetCamera | Returns `mCurrentCamera[number]` |
| 0x0046f2d0 | CGame__SetCamera | Thin wrapper around `CGame__SetCurrentCamera(number, cam, false)` |
| 0x0046f2f0 | CGame__DeclareLevelWon | Level-won transition: sets state/timer, stops vibration, pauses |
| 0x0046f360 | CGame__MPDeclarePlayerWon | Multiplayer winner declaration for player 1/2 |
| 0x0046f3e0 | CGame__MPDeclareGameDrawn | Multiplayer draw declaration path |
| 0x0046f430 | CGame__DeclareLevelLost | Level-lost transition with message + death/non-death pause path |
| 0x0046f550 | CGame__DeclarePlayerDead | Player death handler (camera swap + respawn/loss routing) |
| 0x0046f7e0 | CGame__ReceiveButtonAction | Debug button dispatcher (0..14), including Aurore-gated free-camera toggle path |
| 0x0046fae0 | CGame__UnPause | Clears pause flag and deactivates pause-menu path when free-cam is off |
| 0x0046fb00 | CGame__Pause | Pause entrypoint (vibration-off + optional pause-menu control handoff) |
| 0x0046fb80 | CGame__ToggleDebugUnitForward | Debug unit selection forward within current debug squad |
| 0x0046fc40 | CGame__ToggleDebugUnitBackward | Debug unit selection backward within current debug squad |
| 0x0046fd40 | CGame__ToggleDebugSquadBackward | Debug squad selection backward (with wrap) |
| 0x0046fe20 | CGame__ToggleDebugSquadForward | Debug squad selection forward |
| 0x0046fec0 | CGame__StartPlayingState | Sets game state to playing and posts `\"game playing\"` script event |
| 0x0046ff10 | CGame__HandleEvent | Core game-event dispatcher (`0x7d1..0x7d6`, respawn, pause/fade transitions) |
| 0x00470120 | CGame__RespawnPlayer | Respawn flow (life checks, spawn/start selection, retry scheduling) |
| 0x00470430 | CGame__ToggleFreeCameraOn | Free-camera-on path for a player slot |
| 0x004705d0 | CGame__GetController | Returns `mController[number]` accessor used by pause/free-cam control handoff paths |
| 0x004705e0 | CGame__SetCurrentCamera | Camera assignment helper (`current` vs `old` by free-cam state) |
| 0x00515880 | PLATFORM__Process | Source-aligned platform event pump / quit-code polling wrapper (`CPCPlatform::Process`) |
| 0x005158c0 | PLATFORM__BeginScene | Source-aligned scene-begin wrapper (`CPCPlatform::BeginScene`), used by game/frontend render loops |
| 0x005158e0 | PLATFORM__EndScene | Source-aligned scene-end wrapper (`CPCPlatform::EndScene`), used by game/frontend render loops |
| 0x00515910 | PLATFORM__ClearScreen | Source-aligned clear-screen wrapper (`CPCPlatform::ClearScreen(DWORD col)`) |
| 0x005159e0 | PLATFORM__GetSysTimeFloat | Source-aligned high-resolution timer helper in seconds (`CPCPlatform::GetSysTimeFloat`) |
| 0x00518bf0 | CCredits__BuildDefaultEntries | Builds hard-coded credits-entry table in global memory (`DAT_00896ca8..DAT_0089754c`) before credits rendering |
| 0x00519ff0 | CCredits__WriteEntry_TextId | Credits-entry helper for text-id rows (`{section,text_id,0,style}`) with destination row pointer in `this` (`ECX`) |
| 0x0051a030 | CCredits__RenderCredits | Shared credits renderer used by `CGame__RollCredits` and FE credits-page render path; returns continue/done state |
| 0x0051a7f0 | CFEPCredits__ButtonPressed | FE credits-page back/exit button hook (`button==0x2e`): plays FE sound, sets page `0x11` (`0x1e` transition), resumes FE music |
| 0x0051a820 | CFEPCredits__Process | FE credits-page process hook: watches completion flag (`this+0x08`) and triggers page/music return + draws prompt code `0x2e` |
| 0x0051a880 | CFEPCredits__RenderPreCommon | FE credits-page pre-common render hook; at `transition==1.0` issues `FUN_004679e0(1.0, 0x3fffffff, dest)` |
| 0x0051a8b0 | CFEPCredits__Render | FE credits-page render hook: fade-alpha ramp from `transition`, calls `CCredits__RenderCredits`, sets completion flag when credits stream ends |
| 0x0051a970 | CFEPCredits__TransitionNotification | FE credits-page transition hook: seeds timer (`now+2.0`), starts credits music, clears local page flag |
| 0x0051ae70 | CFEPDirectory__RenderSaveFileList | Shared frontend save-list renderer/poller used by both `CFEPDirectory__Render` and `CFEPVirtualKeyboard__Render` |
| 0x0051f470 | CFEPOptions__GetKillCounterTopBytes_23F4_23F8 | Reads CCareer kill-counter top-byte metadata pair (`0x23F4`/`0x23F8`) into caller buffer (`int * out_pair`) |
| 0x0051f490 | CFEPOptions__SetKillCounterTopBytes_23F4_23F8 | Writes CCareer kill-counter top-byte metadata pair (`0x23F4`/`0x23F8`) from caller buffer (`int * in_pair`) |
| 0x0051f8e0 | CFEPOptions__Cleanup | Options-page cleanup helper; releases owned resources and clears options globals/state |
| 0x0051fff0 | CFEPOptions__EnumerateSaveFiles | Enumerates save files for frontend options/load flow (method on options context/page object) |
| 0x00521650 | CFEPWingmen__GetWingmenCount | Returns available wingmen count for current level context (`char`) |
| 0x00521a60 | CFEPWingmen__Destroy | Wingmen-page cleanup/destructor helper (`void CFEPWingmen__Destroy(void * this)`) |
| 0x00521ae0 | CFEPWingmen__Load | Wingmen-page load/deserialize helper (`void CFEPWingmen__Load(void * this, void * stream)`) |
| 0x00521c80 | CFEPWingmen__Update | Wingmen-page per-frame update helper (`void CFEPWingmen__Update(void * this, int state)`) |
| 0x0044fda0 | CFEPBEConfig__Cleanup | BE-config page cleanup helper (`void CFEPBEConfig__Cleanup(void * this)`) |
| 0x0044fdf0 | CFEPBEConfig__CleanupSquads | BE-config squad cleanup helper (`void CFEPBEConfig__CleanupSquads(void * this)`) |
| 0x004011b0 | vector_constructor_iterator_nothrow | Non-EH vector-constructor iterator helper (`base`, `elem_size`, `count`, `ctor_fn`) used in object-init paths |
| 0x00403f40 | CResourceDescriptor__ctor | Resource-descriptor element ctor: clears 4x 256-byte name blocks and runtime pointer/count fields (`+0x400..+0x418`) |
| 0x00403f80 | CResourceDescriptor__dtor | Resource-descriptor element dtor: frees descriptor-owned object array (`+0x414`, count `+0x418`) and nulls pointers |
| 0x00401ec0 | Vec3__SetXYZ | 3-float vector setter (`out = {x,y,z}`) |
| 0x00401ee0 | Vec3__Add | Vector add helper (`out = a + b`) |
| 0x00401f10 | Mat34__SetRows | Matrix/row block copy helper (copies 3 row vectors into destination) |
| 0x00411a60 | Vec3__Cross | 3D cross-product helper (`out = a x b`) |
| 0x00401fa0 | HeightDelta__Below025_D0 | Threshold helper: returns true when `(height_ref - field_d0) < 0.25` |
| 0x00401fd0 | HeightDelta__Below015_D4 | Threshold helper: returns true when `(height_ref - field_d4) < 0.15` |
| 0x00409760 | LinkedPtrCursor__MoveFirstAndGet | Linked-pointer cursor helper: move to first node and return payload pointer/value |
| 0x00409780 | LinkedPtrCursor__MoveNextAndGet | Linked-pointer cursor helper: move to next node and return payload pointer/value |
| 0x00412900 | CMonitor__CanUseTrackingUpdate | Monitor-side state gate helper deciding if tracking-update path should run. |
| 0x004129a0 | LinkedObjectList__CountFlag9C | Counts list elements where object field `+0x9c` is non-zero |
| 0x00413a70 | CMonitor__ShouldUseSurfaceAlignmentPath | Monitor-side terrain/height gate helper for surface-alignment branch. |
| 0x004136e0 | CMonitor__ApplyYawInputByWeaponClass | Applies yaw input delta scaled by weapon/class-dependent multiplier and monitor sensitivity factor. |
| 0x00413760 | CMonitor__ProcessTrackingAndSurfaceAlignment | Main monitor tracking/surface-alignment process routine. |
| 0x00414b70 | LinkedObjectList__CountFlag9C_IncludingExtra | `CountFlag9C` variant that also includes optional extra object at context `+0x18` |
| 0x00411630 | CMonitor__IntegrateMovementAgainstTerrain | Monitor-side movement/terrain integration helper (caller: `OID_Unk_005078f0__Wrapper_00410c50`). |
| 0x00411aa0 | CMonitor__ComputeTerrainVelocityScalar | Monitor-side scalar helper using terrain-height and velocity gates (caller: `OID_Unk_005078f0__Wrapper_00410c50`). |
| 0x00412000 | CMonitor__ClearTrackedEntryFlag60ByIndex | Walks to indexed tracked-entry node and clears field `+0x60`. |
| 0x00414010 | CMonitor__ClearCurrentTrackedEntryFlag60 | Clears field `+0x60` on current tracked-entry node from shared selection context. |
| 0x004a1270 | CMonitor__SelectNearestHostileTargetReader | Selects nearest hostile/eligible target in radius and sets active target reader. |
| 0x004127a0 | CGeneralVolume__EnableLinkedEntriesByName | Enables linked-list entry flags (`+0x9c`) for nodes whose payload name matches the provided key string. |
| 0x00412d80 | CGeneralVolume__HandleDashForwardInput | Forward dash input handler (`do_dash_Forward`) that applies movement impulse and lockout side effects. |
| 0x00412f70 | CGeneralVolume__HandleDashBackwardInput | Backward dash input handler (`do_dash_Backward`) that applies movement impulse and lockout side effects. |
| 0x00413160 | CGeneralVolume__HandleDashLeftInput | Left dash/strafe input handler (`do_dash_LEFT`) with impulse push and lockout state updates. |
| 0x00413360 | CGeneralVolume__HandleDashRightInput | Right dash/strafe input handler (`do_dash_RIGHT`) with impulse push and lockout state updates. |
| 0x004135d0 | CGeneralVolume__IsDashLockoutActive | Returns whether dash lockout counter (`this+0x44`) is currently active (`> 0`). |
| 0x004135e0 | CGeneralVolume__ApplyScaledVelocityAndSetMovementLatch | Reads current motion vector, applies scaling/damping, writes impulse back, and sets movement latch (`actor+0x638`). |
| 0x00413eb0 | CGeneralVolume__SelectNextEnabledEntry | Cycles to the next enabled entry and normalizes selection/latch state when current entry becomes invalid. |
| 0x00414030 | CGeneralVolume__ResolveCurrentOrFallbackEntry | Resolves selected entry by index with fallback to explicit linked/primary entries. |
| 0x004145d0 | CGeneralVolume__GetCurrentEntryPayload | Returns payload pointer from `ResolveCurrentOrFallbackEntry` (`entry->a4->0`). |
| 0x00414970 | CGeneralVolume__EnableEntriesByName | Enables entries by payload name across linked nodes plus primary entry (`+0x18`). |
| 0x00414a40 | CGeneralVolume__DisableEntriesByNameAndReselect | Disables entries by payload name and triggers reselection when active selection is cleared. |
| 0x005078f0 | CMonitor__UpdateTrackedRenderPair | Core tracked render-pair update helper (transform refresh + optional projected-volume update path). |
| 0x0053f830 | PCPlatform__LoadFonts_InitFontSlot | `PCPlatform__LoadFonts` helper: copies font name into slot buffer (`this+0x5c`), stores pointer at `+0x54`, resets load-state flag |
| 0x00523db0 | CProfiler__ResetAll | Source-aligned profiler accumulator reset helper used at `CGame__MainLoop` entry |
| 0x00515940 | PLATFORM__GetWindowWidth | Returns cached active window/render width used by render/UI layout paths |
| 0x00515b00 | PLATFORM__GetWindowHeight | Returns cached active window/render height used by render/UI layout paths |
| 0x00528b50 | CEngine__SetNumViewpoints | Source-aligned `CEngine::SetNumViewpoints(int)` (`mViewpoints = n`) |
| 0x0053e220 | CDXEngine__PreRender | Engine pre-render stage called from `CGame__Render` before per-view rendering |
| 0x0053e2e0 | CDXEngine__Render | Engine per-view render stage (`viewpoint`) called 1..4 times per frame |
| 0x0053ecc0 | CDXEngine__PostRender | Engine post-render HUD/UI/overlay pass called from `CGame__Render` |
| 0x00523120 | lookup_FMV | FMV lookup-table helper: returns intro/outro FMV id by level and index (0/1/2), `-1` when absent |

### Camera Runtime Helpers

| Address | Function | Description |
|---------|----------|-------------|
| 0x0041a210 | CMovieCamera__ctor | Source-aligned `CMovieCamera(CThing*)` constructor (ActiveReader init + cached camera-state/time fields) |
| 0x0041a390 | CMovieCamera__dtor | CMovieCamera destructor body (unregisters ActiveReader from monitor deletion list) |
| 0x0041a370 | CMovieCamera__scalar_deleting_dtor | MSVC scalar deleting dtor wrapper for `CMovieCamera` |
| 0x0041a200 | CMovieCamera__GetShowHUD | Source-aligned `CMovieCamera::GetShowHUD()` (always returns false) |
| 0x0041ad30 | CInterpolatedCamera__ctor | Source-aligned `CInterpolatedCamera(CCamera*)` interpolation constructor used by engine viewpoint setup |
| 0x0041a3f0 | CMovieCamera__GetPos | Recovered manually (CodeBrowser `F`) on 2026-02-12, then renamed/signed via MCP |
| 0x0041a530 | CMovieCamera__GetOrientation | Recovered manually on 2026-02-12, then renamed/signed via MCP |
| 0x0041a710 | CMovieCamera__GetOldPos | Recovered manually on 2026-02-12, then renamed/signed via MCP |
| 0x0041a6f0 | CMovieCamera__GetOldOrientation | Recovered manually on 2026-02-12, then renamed/signed via MCP |
| 0x0041a630 | CMovieCamera__GetZoom | Recovered manually on 2026-02-12, then renamed/signed via MCP |
| 0x0041a6e0 | CMovieCamera__GetOldZoom | Recovered manually on 2026-02-12, then renamed/signed via MCP |
| 0x0041b070 | CCamera__GetAspectRatio | Recovered manually on 2026-02-12, then renamed/signed via MCP |
| 0x00466140 | CGenericCamera__GetPos | Struct-return style generic-camera position accessor (copies 16 bytes from `this+0x34` into output buffer); RTTI/COL near vtable points to `.?AVCGenericCamera@@` |
| 0x00466170 | CGenericCamera__scalar_deleting_dtor | MSVC scalar deleting dtor wrapper for `CGenericCamera` (`dtor` + conditional free by flag bit) |
| 0x004661b0 | CGenericCamera__dtor | Generic-camera destructor body (resets vtable to `0x005d9260`, returns) |

### ActiveReader / Monitor (Runtime Safety)

| Address | Function | Description |
|---------|----------|-------------|
| 0x00401000 | CGenericActiveReader__SetReader | Core ActiveReader helper (remove from old deletion list, assign, register with new monitor) |
| 0x00401040 | CMonitor__AddDeletionEvent | Lazily allocates/uses `monitor+0x04` deletion list (`CSPtrSet`) and registers a reader cell |
| 0x0042d9b0 | CMonitor__DeleteDeletionEvent | Unregister helper: removes a reader cell from `monitor+0x04` (`CSPtrSet__Remove`) when list exists |
| 0x00419a20 | CMonitor__scalar_deleting_dtor | Scalar deleting dtor wrapper (`Shutdown` + conditional `OID__FreeObject`) |
| 0x0044b1d0 | CGenericActiveReader__dtor | Unregister helper used before freeing/destroying an ActiveReader (removes from `mToRead+0x04`) |
| 0x00466120 | CMonitor__ctor | Monitor base constructor (`this+0x04 = NULL`, vtable set) |
| 0x0046dbc0 | CMonitor__Shutdown_Thunk | Compiler thunk forwarding directly to `0x004bac40` |
| 0x004bac40 | CMonitor__Shutdown | Monitor shutdown/destructor: iterate `monitor+0x04` and null each reader cell (`*cell = NULL`), then clear+free the `CSPtrSet` |
| 0x004bacb0 | CMonitor__Shutdown_Core | Shared monitor cleanup implementation (same null+clear+free behavior, no vtable write) |
| 0x00505d00 | CSPtrSet__ctor | Thin ctor wrapper used in monitor allocation paths: calls `CSPtrSet__Init(this)` and returns `this` |

### Rendering State Helpers

| Address | Function | Description |
|---------|----------|-------------|
| 0x00513bc0 | RenderState_Set | Cached render-state setter; dispatches to device SetRenderState-like vtable call and swaps cull mode (2/3) when winding-flip flag is enabled |

### Mesh Optimization Helpers (Recent Mapping Corrections)

| Address | Function | Description |
|---------|----------|-------------|
| 0x004ab360 | CMesh__OptimizeParts | Core mesh-part optimization pass (`CMesh__Load` caller) that merges/removes parts under structural/skinning/name constraints. |
| 0x004bb040 | CMeshPart__CanMergeInOptimizePass | Part-level merge gate used by `CMesh__OptimizeParts` before candidate merge operations. |
| 0x004bae70 | CMeshPart__CanOptimizePart_Strict | Stricter part-level optimize gate used by `CMesh__OptimizeParts` for merge/remove eligibility checks. |
| 0x004bb210 | CMesh__HasSpecialOptimizationConstraints | Mesh-level topology guard queried by `CMesh__OptimizeParts` to keep root parts on special skeleton/topology families. |
| 0x004ba9d0 | VTable_005e1c4c__Slot00_TryInvokeVFunc1D4 | Table-slot helper: runs readiness gate (`CUnitAI__Unk_0047ce80`) then dispatches virtual method at `this+0x1d4`; owner table semantics are still unresolved. |
| 0x004bac10 | VTable_005e3cc0__Slot00_Dispatch68_AndPostHook | Table-slot helper: dispatches through `this+0x30` target vfunc `+0x68`, then executes shared post-hook `VFuncSlot_06_00452da0`; owner table semantics still unresolved. |

### CExplosion Owner Corrections (Headless 2026-02-25)

| Address | Function | Description |
|---------|----------|-------------|
| 0x00447d50 | CUnitAI__Helper_00447d50 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CUnitAI`. |
| 0x0044a6e0 | CResourceAccumulator__Helper_0044a6e0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CResourceAccumulator`. |
| 0x0044d560 | CFrontEnd__Helper_0044d560 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CFrontEnd`. |
| 0x00477ba0 | CUnitAI__Helper_00477ba0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CUnitAI`. |
| 0x00479770 | CMeshCollisionVolume__Helper_00479770 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CMeshCollisionVolume`. |
| 0x00480ed0 | CUnitAI__Helper_00480ed0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CUnitAI`. |
| 0x00482210 | CUnitAI__Helper_00482210 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CUnitAI`. |
| 0x00487bc0 | CDXEngine__Helper_00487bc0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CDXEngine`. |
| 0x00487d10 | CDXEngine__Helper_00487d10 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CDXEngine`. |
| 0x00488ea0 | CCollisionSeekingInfantryBloke__Helper_00488ea0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CCollisionSeekingInfantryBloke`. |
| 0x0048ddd0 | CParticleSet__Helper_0048ddd0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CParticleSet`. |
| 0x004968f0 | CMeshPart__Helper_004968f0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CMeshPart`. |
| 0x0049c250 | CMeshPart__Helper_0049c250 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CMeshPart`. |
| 0x004adf90 | CMesh__Helper_004adf90 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CMesh`. |
| 0x004b6260 | CSphere__Helper_004b6260 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CSphere`. |
| 0x004b82a0 | CMessageLog__Helper_004b82a0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CMessageLog`. |
| 0x004bcbf0 | CWorld__Helper_004bcbf0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CWorld`. |
| 0x004bd5c0 | CEngine__Helper_004bd5c0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CEngine`. |
| 0x004bdff0 | CWorld__Helper_004bdff0 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CWorld`. |
| 0x004bff40 | CSphereTrigger__Helper_004bff40 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CSphereTrigger`. |
| 0x004c7950 | CEngine__Helper_004c7950 | Former `CExplosionInitThing__Unk_*`; exclusive caller ownership resolved to `CEngine`. |

### CUnitAI Owner Corrections (Headless 2026-02-25 to 2026-02-26)

Nine owner-correction waves promoted 162 unambiguous non-`CUnitAI` targets from `CUnitAI__Unk_*` to owner-scoped helper names (2026-02-25: wave1=40, wave2=40, wave3=32, wave4=21, wave5=2, wave6=2; 2026-02-26 follow-up: wave1=24, wave2=1, wave3=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave1/rename_map_cunitai_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave1/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave2/rename_map_cunitai_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave2/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave3/rename_map_cunitai_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave3/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave4/rename_map_cunitai_owner_wave4.txt`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave4/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave5/rename_map_cunitai_owner_wave5.txt`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave5/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave6/rename_map_cunitai_owner_wave6.txt`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-25/wave6/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-26/wave1/rename_map_cunitai_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-26/wave2/rename_map_cunitai_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-26/wave2/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-26/wave3/rename_map_cunitai_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cunitai_owner_correction_2026-02-26/wave3/verify_after_apply/verify_index.tsv`

Representative mappings:

| Address | Function | Description |
|---------|----------|-------------|
| 0x00416280 | CBomberGuide__Helper_00416280 | Former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CBomberGuide`. |
| 0x00423650 | PCPlatform__Helper_00423650 | Former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `PCPlatform`. |
| 0x00423870 | CResourceAccumulator__Helper_00423870 | Former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CResourceAccumulator`. |
| 0x004247a0 | CGeneralVolume__Helper_004247a0 | Former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CGeneralVolume`. |
| 0x004309e0 | CExplosionStatement__Helper_004309e0 | Former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CExplosionStatement`. |
| 0x00440ad0 | CWaterRenderSystem__Helper_00440ad0 | Former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CWaterRenderSystem`. |
| 0x00441e40 | CGame__Helper_00441e40 | Former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CGame`. |
| 0x0044c210 | CMesh__Helper_0044c210 | Former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CMesh`. |
| 0x0040d5b0 | CExplosionInitThing__Helper_0040d5b0 | Wave4 residual: former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x00442380 | CSoundManager__Helper_00442380 | Wave4 residual: former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CSoundManager`. |
| 0x0044dd60 | CFrontEnd__Helper_0044dd60 | Wave4 residual: former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CFrontEnd`. |
| 0x004daff0 | CFearGrid__Helper_004daff0 | Wave4 residual: former `CUnitAI__Unk_*`; exclusive caller ownership resolved to `CFearGrid`. |
| 0x0044c720 | CSquadNormal__Helper_0044c720 | Wave5 residual: former `CUnitAI__Unk_*`; strict caller ownership resolved to `CSquadNormal`. |
| 0x0047ce80 | CCannon__Helper_0047ce80 | Wave5 residual: former `CUnitAI__Unk_*`; strict caller ownership resolved to `CCannon`. |
| 0x00480e10 | CCollisionSeekingRound__Helper_00480e10 | Wave6 residual: former `CUnitAI__Unk_*`; strict caller ownership resolved to `CCollisionSeekingRound`. |
| 0x0049bd50 | CMCMech__Helper_0049bd50 | Wave6 residual: former `CUnitAI__Unk_*`; strict caller ownership resolved to `CMCMech`. |
| 0x00426fd0 | CFastVB__Helper_00426fd0 | 2026-02-26 wave1 residual: former `CUnitAI__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x0044d390 | CFEPSaveGame__Helper_0044d390 | 2026-02-26 wave1 residual: former `CUnitAI__Unk_*`; strict caller ownership resolved to `CFEPSaveGame`. |
| 0x00490a40 | CStaticShadows__Helper_00490a40 | 2026-02-26 wave1 residual: former `CUnitAI__Unk_*`; strict caller ownership resolved to `CStaticShadows`. |
| 0x0046b1e0 | CFEPSaveGame__Helper_0046b1e0 | 2026-02-26 wave2 residual: former `CUnitAI__Unk_*`; strict caller ownership resolved to `CFEPSaveGame`. |


### CDXTexture Owner Corrections (Headless 2026-02-25 to 2026-02-26)

Evidence-gated xref/decompile passes promoted 289 unambiguous non-`CDXTexture` targets from `CDXTexture__Unk_*` to owner-scoped helper names (2026-02-25: wave1=163, wave2=51, wave3=10, wave4=12, wave5=4, wave6=13, wave7=1; 2026-02-26 follow-up: wave1=32, wave2=3, wave3=0, wave4=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave1/rename_map_cdxtexture_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave1/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave2/rename_map_cdxtexture_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave2/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave3/rename_map_cdxtexture_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave3/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave4/rename_map_cdxtexture_owner_wave4.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave4/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave5/rename_map_cdxtexture_owner_wave5.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave5/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave6/rename_map_cdxtexture_owner_wave6.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave6/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave7/rename_map_cdxtexture_owner_wave7.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-25/wave7/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-26/wave1/rename_map_cdxtexture_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-26/wave2/rename_map_cdxtexture_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-26/wave2/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-26/wave3/rename_map_cdxtexture_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-26/wave3/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-26/wave4/rename_map_cdxtexture_owner_wave4.txt`
- `reverse-engineering/binary-analysis/scratch/cdxtexture_owner_correction_2026-02-26/wave4/verify_after_apply/verify_index.tsv`

Representative mappings:

| Address | Function | Description |
|---------|----------|-------------|
| 0x0055e598 | ControlsUI__Helper_0055e598 | Former `CDXTexture__Unk_*`; exclusive caller ownership resolved to `ControlsUI`. |
| 0x0055e6e2 | CFastVB__Helper_0055e6e2 | Former `CDXTexture__Unk_*`; exclusive caller ownership resolved to `CFastVB`. |
| 0x0055ecb1 | CTexture__Helper_0055ecb1 | Former `CDXTexture__Unk_*`; exclusive caller ownership resolved to `CTexture`. |
| 0x0055f2a7 | CDropship__Helper_0055f2a7 | Former `CDXTexture__Unk_*`; exclusive caller ownership resolved to `CDropship`. |
| 0x0055f380 | CStaticShadows__Helper_0055f380 | Former `CDXTexture__Unk_*`; exclusive caller ownership resolved to `CStaticShadows`. |
| 0x0055f44b | CTokenArchive__Helper_0055f44b | Former `CDXTexture__Unk_*`; exclusive caller ownership resolved to `CTokenArchive`. |
| 0x0055feca | CDXEngine__Helper_0055feca | Former `CDXTexture__Unk_*`; exclusive caller ownership resolved to `CDXEngine`. |
| 0x0057a934 | CMeshCollisionVolume__Helper_0057a934 | Former `CDXTexture__Unk_*`; exclusive caller ownership resolved to `CMeshCollisionVolume`. |
| 0x0055f39d | CStaticShadows__Helper_0055f39d | Wave2 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CStaticShadows`. |
| 0x00565083 | ControlsUI__Helper_00565083 | Wave2 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `ControlsUI`. |
| 0x0057511b | Platform__Helper_0057511b | Wave2 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `Platform`. |
| 0x00574da5 | CFastVB__Helper_00574da5 | Wave2 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x005b4ae0 | CTexture__Helper_005b4ae0 | Wave2 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x0056374b | CFastVB__Helper_0056374b | Wave3 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x005657f0 | ControlsUI__Helper_005657f0 | Wave3 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `ControlsUI`. |
| 0x005ac930 | CTexture__Helper_005ac930 | Wave3 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x0055dda8 | CFastVB__Helper_0055dda8 | Wave4 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x00581a4f | CFastVB__Helper_00581a4f | Wave4 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x005ac180 | CTexture__Helper_005ac180 | Wave4 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x0055ddca | CFastVB__Helper_0055ddca | Wave5 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x0058a578 | CTexture__Helper_0058a578 | Wave5 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x0056f280 | CFastVB__Helper_0056f280 | Wave6 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x00599c49 | CFastVB__Helper_00599c49 | Wave6 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x0059877e | CTexture__Helper_0059877e | Wave6 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x00562013 | ControlsUI__Helper_00562013 | Wave7 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `ControlsUI`. |
| 0x0055dcb0 | OID__Helper_0055dcb0 | 2026-02-26 wave1 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `OID`. |
| 0x0055e624 | ControlsUI__Helper_0055e624 | 2026-02-26 wave1 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `ControlsUI`. |
| 0x005611da | CTexture__Helper_005611da | 2026-02-26 wave1 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x0055e950 | CDXEngine__Helper_0055e950 | 2026-02-26 wave2 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CDXEngine`. |
| 0x00560b93 | CTexture__Helper_00560b93 | 2026-02-26 wave2 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x0056961e | CMCBuggy__Helper_0056961e | 2026-02-26 wave2 residual: former `CDXTexture__Unk_*`; strict caller ownership resolved to `CMCBuggy`. |


### CTexture Owner Corrections (Headless 2026-02-25 to 2026-02-26)

Evidence-gated xref/decompile passes promoted 240 unambiguous non-`CTexture` targets from `CTexture__Unk_*` to owner-scoped helper names (2026-02-25: wave1=128, wave2=50, wave3=17, wave4=6, wave5=17, wave6=1; 2026-02-26 follow-up: wave1=20, wave2=1, wave3=0, wave4=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave1/rename_map_ctexture_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave1/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave2/rename_map_ctexture_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave2/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave3/rename_map_ctexture_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave3/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave4/rename_map_ctexture_owner_wave4.txt`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave4/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave5/rename_map_ctexture_owner_wave5.txt`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave5/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave6/rename_map_ctexture_owner_wave6.txt`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-25/wave6/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-26/wave1/rename_map_ctexture_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-26/wave2/rename_map_ctexture_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-26/wave2/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-26/wave3/rename_map_ctexture_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-26/wave3/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-26/wave4/rename_map_ctexture_owner_wave4.txt`
- `reverse-engineering/binary-analysis/scratch/ctexture_owner_correction_2026-02-26/wave4/verify_after_apply/verify_index.tsv`

Representative mappings:

| Address | Function | Description |
|---------|----------|-------------|
| 0x0055d7e0 | CDXTexture__Helper_0055d7e0 | Former `CTexture__Unk_*`; exclusive caller ownership resolved to `CDXTexture`. |
| 0x00560740 | CDXTexture__Helper_00560740 | Former `CTexture__Unk_*`; exclusive caller ownership resolved to `CDXTexture`. |
| 0x0056112b | CFastVB__Helper_0056112b | Former `CTexture__Unk_*`; exclusive caller ownership resolved to `CFastVB`. |
| 0x00562020 | CFastVB__Helper_00562020 | Former `CTexture__Unk_*`; exclusive caller ownership resolved to `CFastVB`. |
| 0x0057c28b | CMeshCollisionVolume__Helper_0057c28b | Former `CTexture__Unk_*`; exclusive caller ownership resolved to `CMeshCollisionVolume`. |
| 0x00586b63 | CFastVB__Helper_00586b63 | Former `CTexture__Unk_*`; exclusive caller ownership resolved to `CFastVB`. |
| 0x00592d9e | CMeshCollisionVolume__Helper_00592d9e | Former `CTexture__Unk_*`; exclusive caller ownership resolved to `CMeshCollisionVolume`. |
| 0x0059519a | CDXTexture__Helper_0059519a | Former `CTexture__Unk_*`; exclusive caller ownership resolved to `CDXTexture`. |
| 0x0055dc8a | CFastVB__Helper_0055dc8a | Wave2 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x0055f19d | CFastVB__Helper_0055f19d | Wave2 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x0056e62d | CDXTexture__Helper_0056e62d | Wave2 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x005748ad | Platform__Helper_005748ad | Wave2 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `Platform`. |
| 0x00560a49 | CDXTexture__Helper_00560a49 | Wave3 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x0056fe70 | CFastVB__Helper_0056fe70 | Wave3 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x0059c8c1 | CDXTexture__Helper_0059c8c1 | Wave3 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x0055d6d4 | CDXTexture__Helper_0055d6d4 | Wave4 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x00572fa0 | CFastVB__Helper_00572fa0 | Wave4 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x005d0a2a | CFEPSaveGame__Helper_005d0a2a | Wave4 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CFEPSaveGame`. |
| 0x0056f580 | CFastVB__Helper_0056f580 | Wave5 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x005736d0 | CFastVB__Helper_005736d0 | Wave5 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x0059c670 | CDXTexture__Helper_0059c670 | Wave5 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x00574230 | CFastVB__Helper_00574230 | Wave6 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x0055def0 | CDXTexture__Helper_0055def0 | 2026-02-26 wave1 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x0055dfe7 | CDXEngine__Helper_0055dfe7 | 2026-02-26 wave1 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CDXEngine`. |
| 0x0055e64e | CUnitAI__Helper_0055e64e | 2026-02-26 wave1 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CUnitAI`. |
| 0x00561179 | CDXTexture__Helper_00561179 | 2026-02-26 wave1 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x0055ed50 | CDXTexture__Helper_0055ed50 | 2026-02-26 wave2 residual: former `CTexture__Unk_*`; strict caller ownership resolved to `CDXTexture`. |


### CFastVB Owner Corrections (Headless 2026-02-25 to 2026-02-26)

Evidence-gated xref/decompile passes promoted 221 unambiguous non-`CFastVB` targets from `CFastVB__Unk_*` to owner-scoped helper names (2026-02-25: wave1=130, wave2=37, wave3=11, wave4=2, wave5=6, wave6=3; 2026-02-26 follow-up: wave1=28, wave2=4, wave3=0, wave4=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave1/rename_map_cfastvb_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave1/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave2/rename_map_cfastvb_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave2/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave3/rename_map_cfastvb_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave3/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave4/rename_map_cfastvb_owner_wave4.txt`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave4/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave5/rename_map_cfastvb_owner_wave5.txt`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave5/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave6/rename_map_cfastvb_owner_wave6.txt`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-25/wave6/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-26/wave1/rename_map_cfastvb_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-26/wave2/rename_map_cfastvb_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-26/wave2/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-26/wave3/rename_map_cfastvb_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-26/wave3/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-26/wave4/rename_map_cfastvb_owner_wave4.txt`
- `reverse-engineering/binary-analysis/scratch/cfastvb_owner_correction_2026-02-26/wave4/verify_after_apply/verify_index.tsv`

Representative mappings:

| Address | Function | Description |
|---------|----------|-------------|
| 0x0055de6f | CDXTexture__Helper_0055de6f | Former `CFastVB__Unk_*`; exclusive caller ownership resolved to `CDXTexture`. |
| 0x00562ab1 | CTexture__Helper_00562ab1 | Former `CFastVB__Unk_*`; exclusive caller ownership resolved to `CTexture`. |
| 0x0057430b | CMeshCollisionVolume__Helper_0057430b | Former `CFastVB__Unk_*`; exclusive caller ownership resolved to `CMeshCollisionVolume`. |
| 0x005766a5 | CVertexShader__Helper_005766a5 | Former `CFastVB__Unk_*`; exclusive caller ownership resolved to `CVertexShader`. |
| 0x00594c48 | CMeshCollisionVolume__Helper_00594c48 | Former `CFastVB__Unk_*`; exclusive caller ownership resolved to `CMeshCollisionVolume`. |
| 0x0059f050 | CDXTexture__Helper_0059f050 | Former `CFastVB__Unk_*`; exclusive caller ownership resolved to `CDXTexture`. |
| 0x005b85c0 | CMeshCollisionVolume__Helper_005b85c0 | Former `CFastVB__Unk_*`; exclusive caller ownership resolved to `CMeshCollisionVolume`. |
| 0x005d0eb8 | CTexture__Helper_005d0eb8 | Former `CFastVB__Unk_*`; exclusive caller ownership resolved to `CTexture`. |
| 0x0055d90b | CDXTexture__Helper_0055d90b | Wave2 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x00562b15 | CTexture__Helper_00562b15 | Wave2 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x00599161 | CTexture__Helper_00599161 | Wave2 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x00594945 | CMeshCollisionVolume__Helper_00594945 | Wave2 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CMeshCollisionVolume`. |
| 0x00566104 | CDXTexture__Helper_00566104 | Wave3 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x0056a05b | CTexture__Helper_0056a05b | Wave3 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x0059c630 | CTexture__Helper_0059c630 | Wave3 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x00574476 | CDXTexture__Helper_00574476 | Wave4 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x0059c650 | CTexture__Helper_0059c650 | Wave4 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x00561834 | CDXTexture__Helper_00561834 | Wave5 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x00573ff0 | CTexture__Helper_00573ff0 | Wave5 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x005987f4 | CTexture__Helper_005987f4 | Wave5 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CTexture`. |
| 0x00561f75 | CDXTexture__Helper_00561f75 | Wave6 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x00561faa | CDXTexture__Helper_00561faa | Wave6 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x00561fdb | CDXTexture__Helper_00561fdb | Wave6 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x0055db0a | CDXLandscape__Helper_0055db0a | 2026-02-26 wave1 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CDXLandscape`. |
| 0x0057600b | CVBufTexture__Helper_0057600b | 2026-02-26 wave1 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CVBufTexture`. |
| 0x005960c1 | CDXTexture__Helper_005960c1 | 2026-02-26 wave2 residual: former `CFastVB__Unk_*`; strict caller ownership resolved to `CDXTexture`. |

### CVBufTexture Owner Corrections (Headless 2026-02-26)

Evidence-gated xref/decompile passes promoted 14 unambiguous non-`CVBufTexture` targets from `CVBufTexture__Unk_*` to owner-scoped helper names (wave1=14, wave2=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cvbuftexture_owner_correction_2026-02-26/wave1/rename_map_cvbuftexture_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cvbuftexture_owner_correction_2026-02-26/wave1/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cvbuftexture_owner_correction_2026-02-26/wave2/rename_map_cvbuftexture_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cvbuftexture_owner_correction_2026-02-26/wave2/verify_after_apply/verify_index.tsv`

Representative mappings:

| Address | Function | Description |
|---------|----------|-------------|
| 0x0050a0e0 | OID__Helper_0050a0e0 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `OID`. |
| 0x0050a290 | CUnit__Helper_0050a290 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CUnit`. |
| 0x00511db0 | CWorldPhysicsManager__Helper_00511db0 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CWorldPhysicsManager`. |
| 0x00512cc0 | CDXLandscape__Helper_00512cc0 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CDXLandscape`. |
| 0x005234d0 | PlatformInput__Helper_005234d0 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `PlatformInput`. |
| 0x00523a70 | CDXEngine__Helper_00523a70 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CDXEngine`. |
| 0x00523b50 | CDXEngine__Helper_00523b50 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CDXEngine`. |
| 0x00527960 | CFEPMultiplayerStart__Helper_00527960 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CFEPMultiplayerStart`. |
| 0x00527990 | CGame__Helper_00527990 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CGame`. |
| 0x00527c50 | CFrontEnd__Helper_00527c50 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CFrontEnd`. |
| 0x00527cc0 | CWaterRenderSystem__Helper_00527cc0 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CWaterRenderSystem`. |
| 0x00527d20 | CDXLandscape__Helper_00527d20 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CDXLandscape`. |
| 0x00527dd0 | CDXEngine__Helper_00527dd0 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CDXEngine`. |
| 0x0052cd20 | CD3DApplication__Helper_0052cd20 | Wave1 residual: former `CVBufTexture__Unk_*`; strict caller ownership resolved to `CD3DApplication`. |

### CDXEngine Owner Corrections (Headless 2026-02-26)

Evidence-gated xref/decompile passes promoted 6 unambiguous non-`CDXEngine` targets from `CDXEngine__Unk_*` to owner-scoped helper names (wave1=5, wave2=1, wave3=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cdxengine_owner_correction_2026-02-26/wave1/rename_map_cdxengine_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cdxengine_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxengine_owner_correction_2026-02-26/wave2/rename_map_cdxengine_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cdxengine_owner_correction_2026-02-26/wave2/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cdxengine_owner_correction_2026-02-26/wave3/rename_map_cdxengine_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cdxengine_owner_correction_2026-02-26/wave3/verify_after_apply/verify_index.tsv`

Representative mappings:

| Address | Function | Description |
|---------|----------|-------------|
| 0x0053d760 | CThing__Helper_0053d760 | Wave1 residual: former `CDXEngine__Unk_*`; strict caller ownership resolved to `CThing`. |
| 0x00540840 | PCPlatform__Helper_00540840 | Wave1 residual: former `CDXEngine__Unk_*`; strict caller ownership resolved to `PCPlatform`. |
| 0x00544770 | CDXLandscape__Helper_00544770 | Wave1 residual: former `CDXEngine__Unk_*`; strict caller ownership resolved to `CDXLandscape`. |
| 0x005492d0 | CLTShell__Helper_005492d0 | Wave1 residual: former `CDXEngine__Unk_*`; strict caller ownership resolved to `CLTShell`. |
| 0x00549310 | CLTShell__Helper_00549310 | Wave1 residual: former `CDXEngine__Unk_*`; strict caller ownership resolved to `CLTShell`. |
| 0x005447d0 | CDXLandscape__Helper_005447d0 | Wave2 residual: former `CDXEngine__Unk_*`; strict caller ownership resolved to `CDXLandscape`. |

### CWorldPhysicsManager Owner Corrections (Headless 2026-02-26)

Evidence-gated xref/decompile passes promoted 3 unambiguous non-`CWorldPhysicsManager` targets from `CWorldPhysicsManager__Unk_*` to owner-scoped helper names (wave1=3, wave2=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cworldphysicsmanager_owner_correction_2026-02-26/wave1/rename_map_cworldphysicsmanager_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cworldphysicsmanager_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cworldphysicsmanager_owner_correction_2026-02-26/wave2/rename_map_cworldphysicsmanager_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cworldphysicsmanager_owner_correction_2026-02-26/wave2/verify_after_apply/verify_index.tsv`

Representative mappings:

| Address | Function | Description |
|---------|----------|-------------|
| 0x0050f680 | CSpawnerThng__Helper_0050f680 | Wave1 residual: former `CWorldPhysicsManager__Unk_*`; strict caller ownership resolved to `CSpawnerThng`. |
| 0x005113f0 | CWeaponRound__Helper_005113f0 | Wave1 residual: former `CWorldPhysicsManager__Unk_*`; strict caller ownership resolved to `CWeaponRound`. |
| 0x00511510 | CUnit__Helper_00511510 | Wave1 residual: former `CWorldPhysicsManager__Unk_*`; strict caller ownership resolved to `CUnit`. |


### CEngine Owner Corrections (Headless 2026-02-25 to 2026-02-26)

Evidence-gated xref/decompile passes promoted 70 unambiguous non-`CEngine` targets from `CEngine__Unk_*` to owner-scoped helper names (wave1=48, wave2=9, wave3=12, wave4=1).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cengine_owner_correction_2026-02-25/wave1/rename_map_cengine_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cengine_owner_correction_2026-02-25/wave1/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cengine_owner_correction_2026-02-25/wave2/rename_map_cengine_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cengine_owner_correction_2026-02-25/wave2/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cengine_owner_correction_2026-02-26/wave3/rename_map_cengine_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cengine_owner_correction_2026-02-26/wave3/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cengine_owner_correction_2026-02-26/wave4/rename_map_cengine_owner_wave4.txt`
- `reverse-engineering/binary-analysis/scratch/cengine_owner_correction_2026-02-26/wave4/verify_after_apply/verify_index.tsv`

Representative mappings:

| Address | Function | Description |
|---------|----------|-------------|
| 0x00449dc0 | CWorld__Helper_00449dc0 | Former `CEngine__Unk_*`; exclusive caller ownership resolved to `CWorld`. |
| 0x0044a110 | CCutscene__Helper_0044a110 | Former `CEngine__Unk_*`; exclusive caller ownership resolved to `CCutscene`. |
| 0x0044a130 | CGame__Helper_0044a130 | Former `CEngine__Unk_*`; exclusive caller ownership resolved to `CGame`. |
| 0x004bc6d0 | CExplosionInitThing__Helper_004bc6d0 | Former `CEngine__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x004cdba0 | CParticleManager__Helper_004cdba0 | Former `CEngine__Unk_*`; exclusive caller ownership resolved to `CParticleManager`. |
| 0x004fe540 | CUnitAI__Helper_004fe540 | Former `CEngine__Unk_*`; exclusive caller ownership resolved to `CUnitAI`. |
| 0x005061f0 | CBattleEngine__Helper_005061f0 | Former `CEngine__Unk_*`; exclusive caller ownership resolved to `CBattleEngine`. |
| 0x00527de0 | CWaterRenderSystem__Helper_00527de0 | Former `CEngine__Unk_*`; exclusive caller ownership resolved to `CWaterRenderSystem`. |
| 0x005286e0 | CD3DApplication__Helper_005286e0 | Former `CEngine__Unk_*`; exclusive caller ownership resolved to `CD3DApplication`. |
| 0x004bea10 | CExplosionInitThing__Helper_004bea10 | Wave2 residual: former `CEngine__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x00509e40 | CBattleEngine__Helper_00509e40 | Wave2 residual: former `CEngine__Unk_*`; exclusive caller ownership resolved to `CBattleEngine`. |
| 0x0053f040 | CVBufTexture__Helper_0053f040 | Former `CEngine__Unk_*`; exclusive caller ownership resolved to `CVBufTexture`. |
| 0x00449ef0 | CFrontEnd__Helper_00449ef0 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CFrontEnd`. |
| 0x0044a0c0 | CDXMeshVB__Helper_0044a0c0 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CDXMeshVB`. |
| 0x004bd440 | CWorld__Helper_004bd440 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CWorld`. |
| 0x004bdf70 | CWorld__Helper_004bdf70 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CWorld`. |
| 0x004ffdd0 | CSquadNormal__Helper_004ffdd0 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CSquadNormal`. |
| 0x00501310 | CDXEngine__Helper_00501310 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CDXEngine`. |
| 0x00506010 | CGeneralVolume__Helper_00506010 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CGeneralVolume`. |
| 0x005096a0 | CUnit__Helper_005096a0 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CUnit`. |
| 0x005099a0 | CUnit__Helper_005099a0 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CUnit`. |
| 0x00509f70 | CUnit__Helper_00509f70 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CUnit`. |
| 0x00528af0 | CDXTexture__Helper_00528af0 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x0053f010 | CCutscene__Helper_0053f010 | Wave3 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CCutscene`. |
| 0x0050a0b0 | CSquadNormal__Helper_0050a0b0 | Wave4 residual: former `CEngine__Unk_*`; strict caller ownership resolved to `CSquadNormal`. |


### CUnit Owner Corrections (Headless 2026-02-25 to 2026-02-26)

Evidence-gated xref/decompile passes promoted 67 unambiguous non-`CUnit` targets from `CUnit__Unk_*` to owner-scoped helper names (2026-02-25: wave1=47, wave2=4, wave3=1; 2026-02-26 follow-up: wave4=15, wave5=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cunit_owner_correction_2026-02-25/wave1/rename_map_cunit_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cunit_owner_correction_2026-02-25/wave1/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunit_owner_correction_2026-02-25/wave2/rename_map_cunit_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cunit_owner_correction_2026-02-25/wave2/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunit_owner_correction_2026-02-25/wave3/rename_map_cunit_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cunit_owner_correction_2026-02-25/wave3/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunit_owner_correction_2026-02-25/wave4/rename_map_cunit_owner_wave4.txt`
- `reverse-engineering/binary-analysis/scratch/cunit_owner_correction_2026-02-25/wave4/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cunit_owner_correction_2026-02-25/wave5/rename_map_cunit_owner_wave5.txt`
- `reverse-engineering/binary-analysis/scratch/cunit_owner_correction_2026-02-25/wave5/verify_after_apply/verify_index.tsv`

Representative mappings:

| Address | Function | Description |
|---------|----------|-------------|
| 0x00402020 | CGeneralVolume__Helper_00402020 | Former `CUnit__Unk_*`; exclusive caller ownership resolved to `CGeneralVolume`. |
| 0x00403730 | CExplosionInitThing__Helper_00403730 | Owner correction follow-up: helper was previously attributed to `CFEPMultiplayerStart`, then revalidated by vtable-span + behavior evidence and moved to `CExplosionInitThing` (wave19). |
| 0x004d20a0 | CExplosionInitThing__Helper_004d20a0 | Deferred weak symbol closeout: former `CFEPMultiplayerStart__Unk_*`, promoted after vtable-span data xrefs and decompile behavior matched explosion-init pickup/notify flow (wave19). |
| 0x004d8a70 | CCollisionSeekingRound__Helper_004d8a70 | Former `CUnit__Unk_*`; exclusive caller ownership resolved to `CCollisionSeekingRound`. |
| 0x004e2a90 | CSoundManager__Helper_004e2a90 | Former `CUnit__Unk_*`; exclusive caller ownership resolved to `CSoundManager`. |
| 0x004e47e0 | CGame__Helper_004e47e0 | Former `CUnit__Unk_*`; exclusive caller ownership resolved to `CGame`. |
| 0x004f4530 | CGillMHead__Helper_004f4530 | Former `CUnit__Unk_*`; exclusive caller ownership resolved to `CGillMHead`. |
| 0x004fc3a0 | CSpawnerThng__Helper_004fc3a0 | Former `CUnit__Unk_*`; exclusive caller ownership resolved to `CSpawnerThng`. |
| 0x004fcc30 | CThing__Helper_004fcc30 | Former `CUnit__Unk_*`; exclusive caller ownership resolved to `CThing`. |
| 0x004fd4d0 | CCannon__Helper_004fd4d0 | Former `CUnit__Unk_*`; exclusive caller ownership resolved to `CCannon`. |
| 0x004fd8d0 | CDestructableSegmentsController__Helper_004fd8d0 | Former `CUnit__Unk_*`; exclusive caller ownership resolved to `CDestructableSegmentsController`. |
| 0x004e6640 | CThing__Helper_004e6640 | Wave2 residual: former `CUnit__Unk_*`; exclusive caller ownership resolved to `CThing`. |
| 0x004f0200 | CLTShell__Helper_004f0200 | Wave2 residual: former `CUnit__Unk_*`; exclusive caller ownership resolved to `CLTShell`. |
| 0x004f2a30 | CLTShell__Helper_004f2a30 | Wave2 residual: former `CUnit__Unk_*`; exclusive caller ownership resolved to `CLTShell`. |
| 0x004f74b0 | CDXBattleLine__Helper_004f74b0 | Wave2 residual: former `CUnit__Unk_*`; exclusive caller ownership resolved to `CDXBattleLine`. |
| 0x004f7660 | CDXBattleLine__Helper_004f7660 | Wave3 residual: former `CUnit__Unk_*`; strict caller ownership resolved to `CDXBattleLine`. |
| 0x00402000 | CUnitAI__Helper_00402000 | 2026-02-26 wave4 residual: former `CUnit__Unk_*`; strict caller ownership resolved to `CUnitAI`. |
| 0x004f27e0 | CHud__Helper_004f27e0 | 2026-02-26 wave4 residual: former `CUnit__Unk_*`; strict caller ownership resolved to `CHud`. |
| 0x004f7c70 | CD3DApplication__Helper_004f7c70 | 2026-02-26 wave4 residual: former `CUnit__Unk_*`; strict caller ownership resolved to `CD3DApplication`. |
| 0x004fd3d0 | CBattleEngine__Helper_004fd3d0 | 2026-02-26 wave4 residual: former `CUnit__Unk_*`; strict caller ownership resolved to `CBattleEngine`. |

### Semantic Wave20 Promotions (Headless 2026-02-26)

Evidence-gated headless semantic pass (dry/apply/verify) promoted 6 residual weak symbols in the BattleEngine weapon-cycle and influence-map/air-unit adjacency cluster.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave20/rename_map_wave20.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave20/verify_decomp/index.tsv`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave20/xrefs/xrefs_probe.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x00411e70 | CCockpit__CycleToNextUsableWeapon | Weapon-cycle helper invoked from `CBattleEngine__ChangeWeapon`; iterates selection list and advances to a valid next weapon candidate while resetting prior selection state. |
| 0x004124d0 | CGeneralVolume__GetSelectedWeaponDef | Returns selected weapon-definition pointer from indexed node in the active weapon set (used by `CBattleEngine__ChangeWeapon`). |
| 0x004145f0 | CGeneralVolume__GetSelectedWeaponDef_CachedPath | Alternate selected-weapon definition accessor via cached-path helper (`CGeneralVolume__Unk_00414030`) used by ChangeWeapon mode branches. |
| 0x00412cf0 | CCockpit__DestroyWeaponSetAndOwnedNodes | Destruction/clear helper for weapon-set container: removes SPtrSet nodes, destroys owned entries, then clears set state. |
| 0x004ad7f0 | CInfluenceMap__SetTrackedThingAndClearCachedObject | Setter used by battle-engine mode swap path; frees cached object pointer at `+0x24` and updates tracked-thing pointer at `+0x14`. |
| 0x0050f440 | CAirUnit__Helper_0050f440 | Owner-correction from `CWorldPhysicsManager__Unk_*` based on `CAirUnit__VFunc_01_0050f420` caller + destructor-like clear path (`SPtrSet` clear, particle detach, base unit dtor). |

### Semantic Wave21 Promotions (Headless 2026-02-26)

Evidence-gated headless semantic pass (dry/apply/verify) promoted 8 residual weak symbols across battle-engine weapon selection, damage-cell maintenance, explosion overlay, memory manager unlink/release, message-log render, and DX engine generic sort utility paths.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave21/rename_map_wave21.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave21/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave21/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave21/verify_decomp_postcompact/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x0040f2f0 | CBattleEngine__GetWeaponProfileByIndex | Returns selected weapon profile for the currently targeted slot/index in the battle-engine weapon-cycle path. |
| 0x00414cb0 | CExplosionInitThing__PopulateBattleLinePoints | Populates/refreshes battle-line points for the explosion-init tracked target/path data. |
| 0x00440eb0 | CDamage__InsertCellEntry | Inserts a damage-grid cell entry into the per-cell bookkeeping structure. |
| 0x00440f80 | CDamage__RemoveCellEntryByCoords | Removes/clears a damage-grid cell entry by coordinates from the same bookkeeping structure. |
| 0x004879e0 | CExplosionInitThing__AccumulateOverlayMarkerFromViewpoint | Accumulates overlay marker state from viewpoint/target inputs for explosion-init overlay rendering. |
| 0x004a17b0 | CMemoryManager__UnlinkAndReleaseMutex | Unlinks a node/object from memory-manager list links and releases associated mutex/lock state. |
| 0x004b93f0 | CMessageLog__Render | Message-log render pass helper for drawing queued log entries. |
| 0x0055e902 | CDXEngine__InsertionSortGeneric | Generic insertion sort utility used by DX engine helper paths (owner-corrected from prior `CDXTexture__Unk_*`). |

### Semantic Wave22 Promotions (Headless 2026-02-26)

Evidence-gated headless semantic pass (dry/apply/verify) promoted 11 residual weak symbols in the message-log and pause-menu clusters.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave22/rename_map_wave22.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave22/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave22/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave22/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x004b8e70 | CMessageLog__LoadTextures | Loads/refreshes message-log texture resources used by panel/card render paths. |
| 0x004b8ef0 | CMessageLog__EnqueueMessageNode | Enqueues a message entry/node into the message-log queue/list. |
| 0x004b9010 | CMessageLog__RenderPanelFrame | Renders the outer panel/frame layer for the message-log UI block. |
| 0x004b9a80 | CMessageLog__RenderMessageCard | Renders one message-card entry from queued/active message data. |
| 0x004b9ea0 | CMessageLog__ResetRenderState | Resets message-log render/transient state before/after panel draw passes. |
| 0x004d04d0 | CPauseMenu__ReloadSharedBlankTexture | Refreshes/reloads shared blank texture resource used by pause-menu surfaces. |
| 0x004d0510 | CPauseMenu__LoadPauseTextures | Loads pause-menu texture assets used by the pause UI render path. |
| 0x004d06e0 | CPauseMenu__ResumeGameAndPersistOptions | Resume/exit helper that also persists options/defaultoptions state during pause-menu flow. |
| 0x004d0810 | CPauseMenu__ButtonPressed | Pause-menu button-dispatch handler for navigation/selection actions. |
| 0x004d0de0 | CPauseMenu__GetBindingCapacityError | Returns/produces binding-capacity error message/state for control-binding paths. |
| 0x004d0ff0 | CPauseMenu__InitPauseSession | Initializes pause-session state/resources before interactive pause-menu loop. |

### Semantic Wave23 Promotions (Headless 2026-02-26)

Evidence-gated headless semantic pass (dry/apply/verify) promoted 5 residual weak symbols in the virtual-keyboard, pause-menu prompt-binding, and frontend-page movement-check helpers.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave23/rename_map_wave23.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave23/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave23/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave23/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x00520530 | CFEPVirtualKeyboard__InitKeyboardLayout | Initializes virtual-keyboard key layout tables (rows, key tokens, widths, and mode defaults). |
| 0x00520cc0 | CFEPVirtualKeyboard__HandleKeyToken | Applies selected key/control token to the edit buffer (cursor move, insert/delete, mode toggles, confirm). |
| 0x00520f70 | CFEPVirtualKeyboard__MoveSelectionToRow | Moves keyboard selection to a target row while preserving weighted column choice and skipping empty cells. |
| 0x004d0db0 | CPauseMenu__InitBindingPromptAction | Initializes pause-menu binding-prompt action node with target menu item pointer and dispatch id. |
| 0x00403a50 | CFrontEndPage__HasPendingPositionLerp | Returns true when page target/current position lerp endpoints differ and lerp-disable flag is clear. |

### Semantic Wave24 Promotions (Headless 2026-02-26)

Evidence-gated headless semantic correction pass (dry/apply/verify) repaired `CPlayer` camera-view drift and promoted adjacent residual helpers.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave24/rename_map_wave24.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave24/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave24/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave24/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x004d28c0 | CPlayer__GotoFPView | Switches player camera state to first-person mode and updates view/orientation buffers for the new mode. |
| 0x004d29c0 | CPlayer__Goto3rdPersonView | Switches player camera state to third-person mode and restores distance/orientation settings for chase view. |
| 0x004d28a0 | CPlayer__Init | Initializes `CPlayer` camera/view state fields and default mode flags before gameplay control begins. |
| 0x004d2a50 | CPlayer__GotoControlView | Selects control-view mode (player-driven active view) and updates current/old view snapshots. |
| 0x004d2a70 | CPlayer__GetCurrentViewPoint | Returns pointer/output to current active view-position vector used by render/camera consumers. |
| 0x004d2ae0 | CPlayer__GetCurrentViewOrientation | Returns pointer/output to current active view-orientation matrix/angles for render/camera consumers. |
| 0x004d2b40 | CPlayer__GetOldCurrentViewPoint | Returns pointer/output to previous-frame view-position snapshot for interpolation/blend transitions. |
| 0x004d2bb0 | CPlayer__GetOldCurrentViewOrientation | Returns pointer/output to previous-frame view-orientation snapshot for interpolation/blend transitions. |

### Semantic Wave25 Promotions (Headless 2026-02-26)

Evidence-gated headless cleanup pass (dry/apply/verify) promoted 8 residual weak symbols in tightly coupled `CGeneralVolume`, `CMonitor`, and `CCockpit` helper paths.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave25/rename_map_wave25.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave25/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave25/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave25/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x0040b660 | CGeneralVolume__GetWrappedDeltaSigned | Returns signed wrapped angular delta between two float inputs. |
| 0x0040c720 | CGeneralVolume__ResetAndSetActiveReader | Clears mode state, binds a new active reader via `CGenericActiveReader__SetReader`, then runs post-bind setup helper. |
| 0x0040e840 | CMonitor__ToggleAttachedObjectFlag300 | Toggles integer flag at offset `+0x12c` on attached object pointer stored at `this+0x528`. |
| 0x00409880 | CMonitor__GetLastValidRangeStep100 | Scans five fixed slots and returns the last active bucket index in 100-step units. |
| 0x0040dcb0 | CCockpit__SetFlag58C_Enabled | Sets cockpit flag field at offset `+0x58c` to enabled (`1`). |
| 0x00409e80 | CGeneralVolume__SetParam2CC_ToOne | Writes float `1.0` to `CGeneralVolume` field `+0x2cc`. |
| 0x00409e90 | CGeneralVolume__SetParam2CC_ToOne_IfCurrentState1 | Conditionally writes float `1.0` to field `+0x2cc` when current related state equals `1`. |
| 0x00409ec0 | CGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1 | Conditionally writes float `0.4` to field `+0x2cc` when current related state equals `1`. |

### Semantic Wave26 Promotions (Headless 2026-02-26)

Evidence-gated headless cleanup pass (dry/apply/verify) promoted 6 additional residual `CGeneralVolume` dispatch/jitter helpers.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave26/rename_map_wave26.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave26/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave26/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave26/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x00409ef0 | CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0 | Dispatches to mode-2 or mode-3 reset helper path based on `this+0x260`. |
| 0x00409f20 | CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90 | Clears field `+0x588`, seeds `+0x2b4`, then dispatches mode-specific helper path. |
| 0x0040c570 | CGeneralVolume__DispatchModeSpecific_145D0_or_12480 | Routes to one of two mode-specific helper paths (`004145d0` or `00412480`). |
| 0x0040d4d0 | CGeneralVolume__Update4ACLatchFromHeightAndA0 | Updates latch field `+0x4ac` and cached scalar `+0x5dc` from active object height/bounds checks. |
| 0x0040e860 | CGeneralVolume__OffsetPointByForwardScaled | Offsets an input point by forward vector scaled with global factor; optionally runs attached-object transform callback. |
| 0x00407940 | CGeneralVolume__RandomizeOffsets4B8_4C0 | Randomizes local offsets `+0x4b8/+0x4bc/+0x4c0` within bounded range and triggers downstream update callbacks. |

### Semantic Wave27 Promotions (Headless 2026-02-26)

Evidence-gated headless cleanup pass (dry/apply/verify) promoted 6 additional residual `CMonitor` helpers rooted in process/input/target-state and tracked-list maintenance paths.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave27/rename_map_wave27.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave27/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave27/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave27/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x004081c0 | CMonitor__Process | Primary monitor process/update routine coordinating per-frame monitor state transitions. |
| 0x00407a50 | CMonitor__UpdateCameraVectorsAndInput | Updates camera-direction vectors and input-derived monitor orientation state. |
| 0x0040de40 | CMonitor__HandleTargetStateChangeAndHudPrompt | Handles target-state transitions and triggers related HUD prompt/message path updates. |
| 0x0040e940 | CMonitor__UpdateTrackedList_59C | Maintains tracked-entry list anchored at monitor offset `+0x59c`. |
| 0x0040eb50 | CMonitor__FlushTrackedList_1D4 | Flushes/clears tracked-entry list chain anchored at monitor offset `+0x1d4`. |
| 0x0040ebf0 | CMonitor__UpdateTrackedList_620 | Maintains secondary tracked-entry list anchored at monitor offset `+0x620`. |

### Semantic Wave28 Promotions (Headless 2026-02-26)

Evidence-gated headless cleanup pass (dry/apply/verify) promoted 8 additional residual `CMonitor` helpers centered on tracked-entry management, target-reader selection, and surface-alignment process flow.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave28/rename_map_wave28.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave28/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave28/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave28/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x00412000 | CMonitor__ClearTrackedEntryFlag60ByIndex | Clears field `+0x60` on tracked-entry node selected by monitor list index. |
| 0x00414010 | CMonitor__ClearCurrentTrackedEntryFlag60 | Clears field `+0x60` on current tracked-entry node resolved from monitor state. |
| 0x004a1270 | CMonitor__SelectNearestHostileTargetReader | Selects nearest hostile/eligible target within fixed radius and sets active target reader. |
| 0x005078f0 | CMonitor__UpdateTrackedRenderPair | Updates/propagates transform data for monitor tracked render-pair entries. |
| 0x004136e0 | CMonitor__ApplyYawInputByWeaponClass | Applies yaw-input delta scaled by weapon/class multiplier and monitor sensitivity factor. |
| 0x00413760 | CMonitor__ProcessTrackingAndSurfaceAlignment | Main monitor tracking/surface-alignment process routine. |
| 0x00413a70 | CMonitor__ShouldUseSurfaceAlignmentPath | Gate check used by monitor process to decide whether surface-alignment path should run. |
| 0x00412900 | CMonitor__CanUseTrackingUpdate | Checks movement/height/state gates to allow or block tracking-update path. |

### Semantic Wave29 Promotions (Headless 2026-02-26)

Follow-up evidence-gated headless pass (dry/apply/verify) promoted 2 remaining terrain-motion monitor helpers from the same tracked-render flow.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave29/rename_map_wave29.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave29/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave29/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave29/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x00411630 | CMonitor__IntegrateMovementAgainstTerrain | Integrates monitor movement/orientation state against terrain/static-shadow constraints in tracked-render update flow. |
| 0x00411aa0 | CMonitor__ComputeTerrainVelocityScalar | Computes terrain/velocity-based scalar used by monitor movement-adjustment logic. |

### Semantic Wave30 Promotions (Headless 2026-02-26)

Evidence-gated headless pass (dry/apply/verify) promoted 12 `CGeneralVolume` residual helpers centered on dash-direction handlers, entry-resolution flow, and name-keyed enable/disable operations.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave30/rename_map_wave30.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave30/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave30/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave30/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x004127a0 | CGeneralVolume__EnableLinkedEntriesByName | Enables linked-entry flags for nodes whose payload name matches input key. |
| 0x00412d80 | CGeneralVolume__HandleDashForwardInput | Forward dash input path with impulse push and dash-lockout side effects. |
| 0x00412f70 | CGeneralVolume__HandleDashBackwardInput | Backward dash input path with impulse push and dash-lockout side effects. |
| 0x00413160 | CGeneralVolume__HandleDashLeftInput | Left dash/strafe input path with impulse push and lockout state update. |
| 0x00413360 | CGeneralVolume__HandleDashRightInput | Right dash/strafe input path with impulse push and lockout state update. |
| 0x004135d0 | CGeneralVolume__IsDashLockoutActive | Returns whether dash lockout counter (`this+0x44`) is active. |
| 0x004135e0 | CGeneralVolume__ApplyScaledVelocityAndSetMovementLatch | Applies scaled/damped movement vector and sets movement latch (`actor+0x638`). |
| 0x00413eb0 | CGeneralVolume__SelectNextEnabledEntry | Selects next enabled entry and repairs selection/latch state when current entry is invalidated. |
| 0x00414030 | CGeneralVolume__ResolveCurrentOrFallbackEntry | Resolves selected entry by index with fallback to explicit linked/primary entries. |
| 0x004145d0 | CGeneralVolume__GetCurrentEntryPayload | Returns payload pointer from resolved current/fallback entry. |
| 0x00414970 | CGeneralVolume__EnableEntriesByName | Enables entries by payload-name key across linked list and primary entry. |
| 0x00414a40 | CGeneralVolume__DisableEntriesByNameAndReselect | Disables entries by payload-name key and reseats selection when active entry is cleared. |

### Semantic Wave31 Promotions (Headless 2026-02-26)

Evidence-gated headless pass (dry/apply/verify) promoted 13 additional `CGeneralVolume` residual helpers focused on iterator/current-entry accessors and state-refresh update paths.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave31/rename_map_wave31.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave31/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave31/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave31/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x00411b70 | CGeneralVolume__IsStateMachineActive | Returns non-zero when local state machine is active (`+0x2c` or `+0x48` non-zero). |
| 0x004121b0 | CGeneralVolume__EntryIterator_GetSlotFillRatio | Iterator accessor: normalized slot fill ratio from `+0x52c[idx] / cfg[0x88+idx]` (clamped). |
| 0x004122b0 | CGeneralVolume__EntryIterator_GetSlotFlag_55C | Iterator accessor: returns per-slot flag/value at `+0x55c[idx]`. |
| 0x00412310 | CGeneralVolume__EntryIterator_GetSlotFlag_544 | Iterator accessor: returns per-slot flag/value at `+0x544[idx]`. |
| 0x00412370 | CGeneralVolume__EntryIterator_GetDistanceProgressRatio | Iterator accessor: computes distance/progress ratio from entry threshold buckets and `entry+0x60`. |
| 0x00412480 | CGeneralVolume__EntryIterator_GetModeId | Iterator accessor: returns selected entry mode id (`entry->a4[0]`). |
| 0x00413cc0 | CGeneralVolume__ResetState588AndRefreshCurrentEntry | Clears state `+0x588`, resolves current entry, and refreshes entry callback when enabled. |
| 0x00413cf0 | CGeneralVolume__UpdateCurrentEntryProgressAndRefresh | Updates current-entry progress/flags (`+0x52c/+0x544/+0x55c/+0x588`) and refreshes current-entry callback. |
| 0x00414410 | CGeneralVolume__GetCurrentEntrySlotFillRatio | Current-entry accessor: normalized slot fill ratio for resolved entry. |
| 0x00414470 | CGeneralVolume__GetCurrentEntryRoundedSlotValue | Current-entry accessor: rounded current slot value when slot gate `+0x55c[idx]` is clear. |
| 0x004144c0 | CGeneralVolume__GetCurrentEntrySlotFlag_55C | Current-entry accessor: returns slot flag/value at `+0x55c[idx]`. |
| 0x00414520 | CGeneralVolume__GetCurrentEntryDistanceProgressRatio | Current-entry accessor: computes distance/progress ratio from resolved entry thresholds. |
| 0x004145a0 | CGeneralVolume__GetCurrentEntryDisplayString | Current-entry accessor: resolves localized display string via `CText__GetStringById`. |

### Semantic Wave32 Promotions (Headless 2026-02-26)

Evidence-gated headless pass (dry/apply/verify) promoted the final 7 residual `CGeneralVolume` weak helpers from this cluster.

Artifacts:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave32/rename_map_wave32.txt`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave32/rename_dry.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave32/rename_apply.log`
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave32/verify_decomp/index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x0040ac50 | CGeneralVolume__IntegrateSlotAccumulators | Integrates per-slot accumulators (`+0x52c`) using configured per-mode rates and clamps. |
| 0x0040dfb0 | CGeneralVolume__SpawnPickupAndDispatch | Spawns/dispatches pickup object from name-keyed payload and initializes launch/state fields. |
| 0x00410310 | CGeneralVolume__HandleBoostWindowInput | Processes boost-window gate using timing fields (`+0x24/+0x44`) and actor velocity checks. |
| 0x00410490 | CGeneralVolume__ApplyInputDampingToVelocity | Applies input-derived damping/impulse adjustments to actor velocity components. |
| 0x00410740 | CGeneralVolume__HandleAxisPositiveThresholdCross | Handles positive-axis threshold crossing path and updates directional impulse/lockout state. |
| 0x004109d0 | CGeneralVolume__HandleAxisNegativeThresholdCross | Handles negative-axis threshold crossing path and updates directional impulse/lockout state. |
| 0x004114d0 | CGeneralVolume__GetFlagFCScalar | Returns scalar derived from actor flag at `unit+0xfc` for downstream movement gating. |

### CMesh Owner Corrections (Headless 2026-02-26)

Evidence-gated xref/decompile pass promoted 8 unambiguous non-`CMesh` targets from `CMesh__Unk_*` to owner-scoped helper names (wave1=8).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cmesh_owner_correction_2026-02-26/wave1/rename_map_cmesh_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cmesh_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x004a52d0 | CLTShell__Helper_004a52d0 | Wave1 residual: former `CMesh__Unk_*`; strict caller ownership resolved to `CLTShell`. |
| 0x004aa3f0 | CMeshPart__Helper_004aa3f0 | Wave1 residual: former `CMesh__Unk_*`; strict caller ownership resolved to `CMeshPart`. |
| 0x004aa4e0 | CRTMesh__Helper_004aa4e0 | Wave1 residual: former `CMesh__Unk_*`; strict caller ownership resolved to `CRTMesh`. |
| 0x004aa500 | CRTMesh__Helper_004aa500 | Wave1 residual: former `CMesh__Unk_*`; strict caller ownership resolved to `CRTMesh`. |
| 0x004aa680 | CMCMech__Helper_004aa680 | Wave1 residual: former `CMesh__Unk_*`; strict caller ownership resolved to `CMCMech`. |
| 0x004aa6b0 | CDestructableSegmentsController__Helper_004aa6b0 | Wave1 residual: former `CMesh__Unk_*`; strict caller ownership resolved to `CDestructableSegmentsController`. |
| 0x004aa820 | CMCMech__Helper_004aa820 | Wave1 residual: former `CMesh__Unk_*`; strict caller ownership resolved to `CMCMech`. |
| 0x004aa8a0 | CDestroyableSegment__Helper_004aa8a0 | Wave1 residual: former `CMesh__Unk_*`; strict caller ownership resolved to `CDestroyableSegment`. |

### CBattleEngine Owner Corrections (Headless 2026-02-26)

Evidence-gated xref/decompile pass promoted 2 unambiguous non-`CBattleEngine` targets from `CBattleEngine__Unk_*` to owner-scoped helper names (wave1=2).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cbattleengine_owner_correction_2026-02-26/wave1/rename_map_cbattleengine_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cbattleengine_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x00406040 | CDXCompass__Helper_00406040 | Wave1 residual: former `CBattleEngine__Unk_*`; strict caller ownership resolved to `CDXCompass`. |
| 0x004062d0 | CSquadNormal__Helper_004062d0 | Wave1 residual: former `CBattleEngine__Unk_*`; strict caller ownership resolved to `CSquadNormal`. |

### CThing Owner Corrections (Headless 2026-02-26)

Evidence-gated xref/decompile pass promoted 4 unambiguous non-`CThing` targets from `CThing__Unk_*` to owner-scoped helper names (wave1=4).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cthing_owner_correction_2026-02-26/wave1/rename_map_cthing_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cthing_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x004f39b0 | CUnit__Helper_004f39b0 | Wave1 residual: former `CThing__Unk_*`; strict caller ownership resolved to `CUnit`. |
| 0x004f3ac0 | CUnitAI__Helper_004f3ac0 | Wave1 residual: former `CThing__Unk_*`; strict caller ownership resolved to `CUnitAI`. |
| 0x004f3c80 | CAtmospheric__Helper_004f3c80 | Wave1 residual: former `CThing__Unk_*`; strict caller ownership resolved to `CAtmospheric`. |
| 0x004f3d10 | CCollisionSeekingRound__Helper_004f3d10 | Wave1 residual: former `CThing__Unk_*`; strict caller ownership resolved to `CCollisionSeekingRound`. |

### CMonitor Owner Corrections (Headless 2026-02-25 to 2026-02-26)

Evidence-gated xref/decompile passes promoted 14 unambiguous non-`CMonitor` targets from `CMonitor__Unk_*` to owner-scoped helper names (wave1=12, wave2=2, wave3=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cmonitor_owner_correction_2026-02-25/wave1/rename_map_cmonitor_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cmonitor_owner_correction_2026-02-25/wave1/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cmonitor_owner_correction_2026-02-26/wave2/rename_map_cmonitor_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cmonitor_owner_correction_2026-02-26/wave2/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cmonitor_owner_correction_2026-02-26/wave3/rename_map_cmonitor_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cmonitor_owner_correction_2026-02-26/wave3/verify_after_apply/verify_index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x00407060 | CEngine__Helper_00407060 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CEngine`. |
| 0x0040dc90 | CExplosionInitThing__Helper_0040dc90 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x00410210 | CBattleEngine__Helper_00410210 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CBattleEngine`. |
| 0x00412050 | CEngine__Helper_00412050 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CEngine`. |
| 0x00412520 | CExplosionInitThing__Helper_00412520 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x00412bc0 | CBattleEngine__Helper_00412bc0 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CBattleEngine`. |
| 0x004140d0 | CEngine__Helper_004140d0 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CEngine`. |
| 0x00414610 | CExplosionInitThing__Helper_00414610 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x00452db0 | CFEPGoodies__Helper_00452db0 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CFEPGoodies`. |
| 0x00472e50 | CVBufTexture__Helper_00472e50 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CVBufTexture`. |
| 0x00490220 | CEngine__Helper_00490220 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CEngine`. |
| 0x00490780 | CDXEngine__Helper_00490780 | Former `CMonitor__Unk_*`; exclusive caller ownership resolved to `CDXEngine`. |
| 0x004097a0 | CUnit__Helper_004097a0 | Wave2 residual: former `CMonitor__Unk_*`; strict caller ownership resolved to `CUnit`. |
| 0x0040f110 | CEngine__Helper_0040f110 | Wave2 residual: former `CMonitor__Unk_*`; strict caller ownership resolved to `CEngine`. |

### CGeneralVolume Owner Corrections (Headless 2026-02-25 to 2026-02-26)

Evidence-gated xref/decompile passes promoted 28 unambiguous non-`CGeneralVolume` targets from `CGeneralVolume__Unk_*` to owner-scoped helper names (wave1=20, wave2=8, wave3=0, wave4=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cgeneralvolume_owner_correction_2026-02-25/wave1/rename_map_cgeneralvolume_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cgeneralvolume_owner_correction_2026-02-25/wave1/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cgeneralvolume_owner_correction_2026-02-26/wave2/rename_map_cgeneralvolume_owner_wave2.txt`
- `reverse-engineering/binary-analysis/scratch/cgeneralvolume_owner_correction_2026-02-26/wave2/verify_after_apply/index.tsv`
- `reverse-engineering/binary-analysis/scratch/cgeneralvolume_owner_correction_2026-02-26/wave3/rename_map_cgeneralvolume_owner_wave3.txt`
- `reverse-engineering/binary-analysis/scratch/cgeneralvolume_owner_correction_2026-02-26/wave3/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/cgeneralvolume_owner_correction_2026-02-26/wave4/rename_map_cgeneralvolume_owner_wave4.txt`
- `reverse-engineering/binary-analysis/scratch/cgeneralvolume_owner_correction_2026-02-26/wave4/verify_after_apply/verify_index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x00409950 | CMonitor__Helper_00409950 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CMonitor`. |
| 0x0040a580 | CMonitor__Helper_0040a580 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CMonitor`. |
| 0x0040acc0 | CBattleEngine__Helper_0040acc0 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CBattleEngine`. |
| 0x0040b120 | CMonitor__Helper_0040b120 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CMonitor`. |
| 0x0040b6d0 | CBattleEngine__Helper_0040b6d0 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CBattleEngine`. |
| 0x0040c2e0 | CEngine__Helper_0040c2e0 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CEngine`. |
| 0x0040c340 | CEngine__Helper_0040c340 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CEngine`. |
| 0x0040c3a0 | CExplosionInitThing__Helper_0040c3a0 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x0040c3c0 | CExplosionInitThing__Helper_0040c3c0 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x0040c460 | CExplosionInitThing__Helper_0040c460 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x0040c480 | CExplosionInitThing__Helper_0040c480 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x0040c4a0 | CExplosionInitThing__Helper_0040c4a0 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x0040c550 | CExplosionInitThing__Helper_0040c550 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x0040c590 | CExplosionInitThing__Helper_0040c590 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CExplosionInitThing`. |
| 0x0040c5b0 | CRepairPadAI__Helper_0040c5b0 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CRepairPadAI`. |
| 0x0040c5e0 | CRepairPadAI__Helper_0040c5e0 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CRepairPadAI`. |
| 0x0040c650 | CBattleEngine__Helper_0040c650 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CBattleEngine`. |
| 0x0040d0f0 | CEngine__Helper_0040d0f0 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CEngine`. |
| 0x0040d1a0 | CMonitor__Helper_0040d1a0 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CMonitor`. |
| 0x0040c630 | CDXCompass__Helper_0040c630 | Wave2 residual: former `CGeneralVolume__Unk_*`; strict caller ownership resolved to `CDXCompass`. |
| 0x0040d120 | CMeshCollisionVolume__Helper_0040d120 | Wave2 residual: former `CGeneralVolume__Unk_*`; strict caller ownership resolved to `CMeshCollisionVolume`. |
| 0x0040d150 | CExplosionInitThing__Helper_0040d150 | Wave2 residual: former `CGeneralVolume__Unk_*`; strict caller ownership resolved to `CExplosionInitThing`. |
| 0x0040d180 | CMeshCollisionVolume__Helper_0040d180 | Wave2 residual: former `CGeneralVolume__Unk_*`; strict caller ownership resolved to `CMeshCollisionVolume`. |
| 0x0040d1f0 | OID__Helper_0040d1f0 | Wave2 residual: former `CGeneralVolume__Unk_*`; strict caller ownership resolved to `OID`. |
| 0x0040d2c0 | CSquadNormal__Helper_0040d2c0 | Wave2 residual: former `CGeneralVolume__Unk_*`; strict caller ownership resolved to `CSquadNormal`. |
| 0x0040d320 | CMCBuggy__Helper_0040d320 | Wave2 residual: former `CGeneralVolume__Unk_*`; strict caller ownership resolved to `CMCBuggy`. |
| 0x0040d660 | CExplosionInitThing__Helper_0040d660 | Wave2 residual: former `CGeneralVolume__Unk_*`; strict caller ownership resolved to `CExplosionInitThing`. |
| 0x0040ef20 | CMonitor__Helper_0040ef20 | Former `CGeneralVolume__Unk_*`; exclusive caller ownership resolved to `CMonitor`. |

### CMeshCollisionVolume Owner Corrections (Headless 2026-02-26)

Evidence-gated xref/decompile pass promoted 10 unambiguous non-`CMeshCollisionVolume` targets from `CMeshCollisionVolume__Unk_*` to owner-scoped helper names (wave1=10).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/cmeshcollisionvolume_owner_correction_2026-02-26/wave1/rename_map_cmeshcollisionvolume_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/cmeshcollisionvolume_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`

| Address | Function | Description |
|---------|----------|-------------|
| 0x00465f00 | CVBufTexture__Helper_00465f00 | Wave1 residual: former `CMeshCollisionVolume__Unk_*`; strict caller ownership resolved to `CVBufTexture`. |
| 0x00569814 | CDXTexture__Helper_00569814 | Wave1 residual: former `CMeshCollisionVolume__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x0056982f | CDXTexture__Helper_0056982f | Wave1 residual: former `CMeshCollisionVolume__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x00575d51 | CFastVB__Helper_00575d51 | Wave1 residual: former `CMeshCollisionVolume__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x00575d75 | CFastVB__Helper_00575d75 | Wave1 residual: former `CMeshCollisionVolume__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x00599ffd | CFastVB__Helper_00599ffd | Wave1 residual: former `CMeshCollisionVolume__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x0059d47a | CDXTexture__Helper_0059d47a | Wave1 residual: former `CMeshCollisionVolume__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x0059d614 | CDXTexture__Helper_0059d614 | Wave1 residual: former `CMeshCollisionVolume__Unk_*`; strict caller ownership resolved to `CDXTexture`. |
| 0x005a4d98 | CFastVB__Helper_005a4d98 | Wave1 residual: former `CMeshCollisionVolume__Unk_*`; strict caller ownership resolved to `CFastVB`. |
| 0x005b3ec0 | CDXTexture__Helper_005b3ec0 | Wave1 residual: former `CMeshCollisionVolume__Unk_*`; strict caller ownership resolved to `CDXTexture`. |

### CSoundManager Owner Corrections (Headless 2026-02-26)

Evidence-gated xref/decompile passes promoted 7 unambiguous non-`CSoundManager` targets from `CSoundManager__Unk_*` to owner-scoped helper names (wave1=7, wave2=0).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/csoundmanager_owner_correction_2026-02-26/wave1/rename_map_csoundmanager_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/csoundmanager_owner_correction_2026-02-26/wave1/verify_after_apply/verify_index.tsv`
- `reverse-engineering/binary-analysis/scratch/csoundmanager_owner_correction_2026-02-26/wave2/rename_map_csoundmanager_owner_wave2.txt`

| Address | Function | Description |
|---------|----------|-------------|
| 0x004e1200 | CMessageBox__Helper_004e1200 | Wave1 residual: former `CSoundManager__Unk_*`; strict caller ownership resolved to `CMessageBox`. |
| 0x004e1260 | CMonitor__Helper_004e1260 | Wave1 residual: former `CSoundManager__Unk_*`; strict caller ownership resolved to `CMonitor`. |
| 0x004e1800 | CMonitor__Helper_004e1800 | Wave1 residual: former `CSoundManager__Unk_*`; strict caller ownership resolved to `CMonitor`. |
| 0x004e1880 | CMonitor__Helper_004e1880 | Wave1 residual: former `CSoundManager__Unk_*`; strict caller ownership resolved to `CMonitor`. |
| 0x004e1910 | CBattleEngine__Helper_004e1910 | Wave1 residual: former `CSoundManager__Unk_*`; strict caller ownership resolved to `CBattleEngine`. |
| 0x004e1940 | CMonitor__Helper_004e1940 | Wave1 residual: former `CSoundManager__Unk_*`; strict caller ownership resolved to `CMonitor`. |
| 0x004e1ab0 | CMonitor__Helper_004e1ab0 | Wave1 residual: former `CSoundManager__Unk_*`; strict caller ownership resolved to `CMonitor`. |

### IScript Owner Corrections (Headless 2026-02-26)

Evidence-gated xref/decompile pass on `IScript__Unk_*` produced a strict 0-map no-op (wave1=0): no unique non-self owners met the promotion gate (`top_owner_count>=2` + unique winner).

Artifacts:
- `reverse-engineering/binary-analysis/scratch/iscript_owner_correction_2026-02-26/wave1/rename_map_iscript_owner_wave1.txt`
- `reverse-engineering/binary-analysis/scratch/iscript_owner_correction_2026-02-26/wave1/chosen_unambiguous_targets.tsv`

### MSVC Runtime Helpers (Common in Decompilation)

| Address | Function | Description |
|---------|----------|-------------|
| 0x0055dc20 | eh_vector_constructor_iterator | MSVC helper that constructs array elements and unwinds partial construction on exceptions |
| 0x0055db8a | eh_vector_destructor_iterator | MSVC helper that destroys array elements (reverse iteration semantics) |

### Camera (Recent Mapping Corrections)

| Address | Function | Description |
|---------|----------|-------------|
| 0x00418ef0 | CThing3rdPersonCamera__ctor | 3rd-person camera ctor (was previously mislabeled `CCamera__ctor`) |
| 0x00419140 | CThing3rdPersonCamera__dtor | 3rd-person camera dtor (was previously mislabeled `CCamera__dtor`) |
| 0x00419120 | CThing3rdPersonCamera__scalar_deleting_dtor | MSVC scalar deleting dtor wrapper |
| 0x004198d0 | CPanCamera__ctor | Pan camera ctor with `(for_thing, curve, length)` |
| 0x00419a60 | CPanCamera__dtor | Pan camera dtor |
| 0x00419a40 | CPanCamera__scalar_deleting_dtor | MSVC scalar deleting dtor wrapper |
| 0x00419b00 | CPanCamera__Update | Pan-camera update path (schedules UPDATE_CAMERA / 2000) |
| 0x00419d40 | CPanCamera__GetPos | Recovered manually (CodeBrowser `F`) on 2026-02-12, then renamed/signed via MCP |
| 0x00419d70 | CPanCamera__GetOrientation | Recovered manually on 2026-02-12, then renamed/signed via MCP |
| 0x00419d90 | CPanCamera__GetOldPos | Recovered manually on 2026-02-12, then renamed/signed via MCP |
| 0x00419dc0 | CPanCamera__GetOldOrientation | Recovered manually on 2026-02-12, then renamed/signed via MCP |
| 0x00419de0 | CPanCamera__HandleEvent | Recovered manually on 2026-02-12, then renamed/signed via MCP |

### HUD Component (Recent Mapping Corrections)

| Address | Function | Description |
|---------|----------|-------------|
| 0x004de3a0 | CHudComponent__ctor | Constructor for 0x68-byte HUD component object created by `CHud__SetHudComponent`; loads/caches Effect mesh/resource handles |
| 0x004de730 | CHudComponent__scalar_deleting_dtor | Scalar deleting dtor wrapper for HUD component |
| 0x004de760 | CHudComponent__dtor | HUD component destructor body (owned object release + monitor shutdown path) |
| 0x004de850 | CHudComponent__RequestDestroy | Deferred-destroy marker (sets flags at `+0x64/+0x65`) consumed by HUD render path |
| 0x004de860 | CHudComponent__RenderPass | Per-component render/update helper (iterates sub-item table and dispatches through `CHudComponent__RenderPassEntry`) |

### Utility Helpers (Recent Mapping Corrections)

| Address | Function | Description |
|---------|----------|-------------|
| 0x004de080 | CRTTree__scalar_deleting_dtor | Scalar deleting dtor wrapper (`CRTTree__Destructor` + optional `OID__FreeObject`) |
| 0x004de8c0 | RandomSeedPair__Set | Initializes a 2-dword seed pair to the same value (current/base seed) |
| 0x004de8d0 | Random__NextLCGAbs | LCG step helper (Schrage-style constants) that updates `*seed` and returns absolute value |
| 0x00549270 | MEM_MANAGER__Cleanup | Global memory-cleanup wrapper used by load/restart paths (`MEM_MANAGER.Cleanup()`, double coalesce pass) |

### StaticShadows (Recent Mapping Corrections)

| Address | Function | Description |
|---------|----------|-------------|
| 0x004ebc00 | CStaticShadows__Reattach | Rebinds static-shadow entries to live things by stored IDs, logs unattached cases, then refreshes visibility |

### EventManager (Recent Mapping Corrections)

| Address | Function | Description |
|---------|----------|-------------|
| 0x0044afa0 | CEventManager__ctor | Initializes 600 ring-bucket `CSPtrSet` containers and sets vtable/state |
| 0x0044afe0 | CEventManager__scalar_deleting_dtor | MSVC scalar deleting dtor wrapper (`dtor` + optional free) |
| 0x0044b000 | CEventManager__dtor | Destructor body; calls `CEventManager__Shutdown` |
| 0x0044b060 | CEventManager__Init | Initializes counters and allocates overflow container + 20,000 event pool |
| 0x0044b1f0 | CEventManager__Shutdown | Clears ring buffers/overflow and frees event pool |
| 0x0044b2a0 | CEventManager__GetNextFreeEvent | Pops free-list head; logs fatal when exhausted |
| 0x0044b2d0 | CEventManager__AddEvent_TimeFromNow | Relative-time AddEvent overload |
| 0x0044b310 | CEventManager__AddEvent_ScheduledEvent | Scheduled-event overload; returns temp event to free-list path |
| 0x0044b370 | CEventManager__AddEvent_AtTime | Main scheduling path (near-frame ring buffer + overflow insertion) |
| 0x0044b5c0 | CEventManager__Update | Calls `AdvanceTime` then `Flush` |
| 0x0044b600 | CEventManager__AdvanceTime | Retail variant returns wrap flag while advancing time/buffer index |
| 0x0044b640 | CEventManager__Flush | Executes due events and performs cleanup/sanity checks |

### ScheduledEvent (Recent Mapping Corrections)

| Address | Function | Description |
|---------|----------|-------------|
| 0x004de1f0 | CScheduledEvent__Set | Initialize scheduled event fields (`event_num`, `time`, `to_call`, `data`) via ActiveReader tracking |
| 0x004de230 | CScheduledEvent__dtor | Scheduled event destructor: decrements live counter and unregisters ActiveReader cells (`mToCall`, `mData`) |

### Options Tail Layout (0x56 Bytes)

Written by `OptionsTail_Write` (`0x00420b10`) and read by `OptionsTail_Read` (`0x00420d70`). Offsets are relative to the start of the 0x56-byte tail block appended at the end of the save buffer.

| Offset | Size | Global | Notes |
|--------|------|--------|-------|
| 0x00 | 4 | `g_Options_UnknownFloat0` (`0x006254f0`) | Options tail float (default ~0.7) |
| 0x04 | 4 | `g_MouseSensitivity` (`0x006254f4`) | Mouse sensitivity scalar |
| 0x08 | 2 | `g_ControlSchemeIndex` (`0x00677d70`, low-16) | Control preset index |
| 0x0A | 2 | `g_LanguageIndex` (`0x0083d97c`, low-16) | Language index |
| 0x0C | 4 | `g_MeshQualityDistance` (`0x006321a0`) | Mesh quality distance scalar |
| 0x10 | 4 | `g_MeshLodBias` (`0x00631e88`) | `cg_meshlodbias` console variable |
| 0x14 | 4 | `g_MeshQualityScaleFactor` (`0x00630e0c`) | Mesh quality scale factor |
| 0x18 | 4 | `g_MeshQualityLodTable` (`0x009c7558`) | Mesh LOD table pointer/float data |
| 0x1C | 4 | `g_LandscapeLowresGeom` (`0x008aa99c`) | CVar value: `LANDSCAPE_LOWRES_GEOM` |
| 0x20 | 4 | `g_ScreenShape` (`0x0082b484`) | 0=4:3, 1=16:9, 2=1:1 |
| 0x24 | 4 | `g_DisallowMipMapping` (`0x0082b474`) | CVar: `RENDERSTATE_DISALLOW_MIPMAPPING` |
| 0x28 | 4 | `g_D3DDeviceIndex` (`0x0066061c`) | Selected adapter/device index |
| 0x2C | 4 | `g_TryLockableBackbuffer` (`0x0066306c`) | D3D init flag |
| 0x30 | 4 | `g_LandscapeMaxLevelsUser` (`0x008aa95c`) | CVar value: `LANDSCAPE_MAXLEVELS_USER` |
| 0x34 | 4 | `g_UserTextureResLossShift` (`0x009cc104`) | CVar value: `USER_TEXTURE_RES_LOSS_SHIFT` |
| 0x38 | 4 | `g_UserTextureAllow32Bit` (`0x009cc0e4`) | CVar value: `USER_TEXTURE_ALLOW_32_BIT` |
| 0x3C | 4 | `g_ProfileMultisampleType` | Profile-selected multisample type (looked up from profile tables) |
| 0x40 | 4 | `g_InvertXAxisFlag` (`0x00663070`) | Negates X in input/camera update |
| 0x44 | 4 | `g_SoundEnabledFlag` (`0x00663074`) | Master sound enable flag |
| 0x48 | 4 | `g_SoundSampleRateIndex` (`0x00663080`) | Sample rate/bit depth index |
| 0x4C | 4 | `g_SoundDeviceIndex` (`0x00663078`) | DirectSound device index |
| 0x50 | 4 | `g_Sound3DMethod` (`0x00663084`) | 3D sound method selection |
| 0x54 | 1 | `g_LandscapeDetailLevel2` (`0x009c7c54`) | Landscape detail enum part |
| 0x55 | 1 | `g_LandscapeDetailLevel1` (`0x009c7c56`) | Landscape detail enum part |

### Career System (CCareer)

| Address | Function | Description |
|---------|----------|-------------|
| 0x0041b740 | CCareerNode__Blank | Reset one node to default “blank” state |
| 0x0041b770 | CCareerNode__SetBaseThingExistTo | Set/clear one of the 288 `mBaseThingsExists` persistence bits |
| 0x0041b7b0 | CCareer__GetLevelStructure | Return pointer to static `level_structure` world/link table (`&DAT_00623e28`); source-parity `CCareer::GetLevelStructure()` helper |
| 0x0041b7c0 | CCareer__Blank | Reset career state and rebuild the mission graph (`level_structure`) |
| 0x0041b8f0 | CCareer__GetNodeFromWorld | Get node from world number |
| 0x0041b940 | CCareerNode__GetChildLinks | Return this node’s two outgoing links (lower/higher) |
| 0x0041b9f0 | CCareerNode__GetParentLinks | Scan all nodes and return links whose `mToNode` resolves to `this` node |
| 0x0041bb20 | CCareer__DoesBaseThingExist | Query “base thing exists” persistence bit by world + offset |
| 0x0041bbb0 | CCareer__IsWorldLater | World-number reachability test (uses `Later`) |
| 0x0041bc60 | CCareer__Later | Depth-first reachability helper |
| 0x0041bd00 | CCareer__Update | Apply `END_LEVEL_DATA` after a win (slots/kills/ranking/complete), then `ReCalcLinks` + `UpdateGoodieStates` |
| 0x0041bdf0 | CCareer__ReCalcLinks | Recalculate link completion / broken state |
| 0x0041c180 | CCareer__UpdateThingsKilled | Accumulate per-level kill deltas into career totals |
| 0x0041c240 | TOTAL_S_GRADES | Source helper: count S-ranked completed nodes and compare against `goodies[goodie_num].GetNumber()` |
| 0x0041c330 | CCareer__GetGradeForWorld | Source-equivalent `GRADE(world_num)` helper: resolves node ranking for a world, converts to grade letter, writes one-byte grade to `out_grade` |
| 0x0041c450 | CCareer__CountGoodies | Count goodies with state `> GS_INSTRUCTIONS` (source parity with `CCareer::CountGoodies()`) |
| 0x0041c470 | CCareer__UpdateGoodieStates | Update goodie states |
| 0x00420ab0 | CGrade__ctor_char | Inline `CGrade(char)` helper used by goodie-grade comparisons |
| 0x00420ac0 | CGrade__operator_gte | Inline `CGrade::operator>=` (`S` special-case, else lexical compare) |
| 0x00420af0 | CCareer__GetNode | Inline `CCareer::GetNode(int)` accessor (`index<0 -> NULL`) |
| 0x00421350 | CCareer__Save | Save career data |
| 0x00421470 | CCareer__GetGradeFromRanking | Convert ranking float to grade letter (`int CCareer__GetGradeFromRanking(float ranking)`; source semantic type is `WCHAR`) |
| 0x004214e0 | CCareer__SetSlot | Set tech slot bit |
| 0x00421550 | CCareer__GetAndResetGoodieNewCount | Debriefing helper: returns+clears `new_goodie_count` |
| 0x00421560 | CCareer__GetAndResetFirstGoodie | Debriefing helper: returns+clears `first_goodie` flag |
| 0x00421570 | CCareer__IsEpisodeAvailable | Check episode availability |
| 0x00421970 | CCareer__NodeArrayAt | Internal node-array index helper (`node_base + index*0x40`) used by `CCareer__UpdateGoodieStates` |
| 0x00461a50 | Career_IsWorldUnlocked | Career map gate: unlocked if any parent link has `mLinkType==CN_COMPLETE`; world 100 always unlocked; TURKEY cheat bypass |

### MissionScript Slot Bits (CGame)

`mSlots` persistence is script-driven: mission scripts call `GetSlot` / `SetSlot` / `SetSlotSave`, which map to the runtime slot-bitset (`CGame::mSlots` at `this+0x308`) plus `CCareer__SetSlot` (for immediate persistence).

| Address | Function | Description |
|---------|----------|-------------|
| 0x0046d410 | CGame__GetSlot | Read the runtime slot bit (`CGame::mSlots` at `this+0x308`, slot range `0..255`) |
| 0x0046d3a0 | CGame__SetSlot | Set/clear a runtime slot bit (`CGame::mSlots` at `this+0x308`, slot range `0..255`) |
| 0x005338d0 | IScript__SetSlot | `SetSlot(slot, val)` script handler: calls `CGame__SetSlot` (persists into CCareer on LevelWon via END_LEVEL_DATA copy) |
| 0x00533900 | IScript__SetSlotSave | `SetSlotSave(slot, val)` script handler: calls `CGame__SetSlot` and persists immediately to `CCareer__SetSlot(&CAREER, slot, val)` |
| 0x005339a0 | IScript__GetSlotBitValue | `GetSlot` script handler: returns a bool parameter containing `CGame__GetSlot(slot)` |

### MissionScript Player Lives

| Address | Function | Description |
|---------|----------|-------------|
| 0x00472620 | CGame__SetPlayerLives | Helper for `SetPlayerLives(player_index, lives)`: writes `this+0x290/+0x294` for player 1/2 |
| 0x005338a0 | IScript__SetPlayerLives | `SetPlayerLives(player_index, lives)` script handler: calls `CGame__SetPlayerLives(&DAT_008a9a98, ...)` |

### MissionScript Goodies

| Address | Function | Description |
|---------|----------|-------------|
| 0x00533a70 | IScript__SetGoodieState | `SetGoodieState(index, state)` script handler: sets `g_Career_mGoodies[index-1] = state` (scripts use 1-based indices) |
| 0x00533aa0 | IScript__GetGoodieState | `GetGoodieState(index)` script handler: returns `g_Career_mGoodies[index-1]` as a scalar result |

### MissionScript Level Outcome

| Address | Function | Description |
|---------|----------|-------------|
| 0x005381a0 | IScript__LevelLost | `LevelLost()` script handler: calls `CGame__DeclareLevelLost(&DAT_008a9a98, 0, 0)` (loss with no message) |
| 0x005381c0 | IScript__LevelLostString | `LevelLostString(message_id)` script handler: calls `CGame__DeclareLevelLost(&DAT_008a9a98, message_id, 0)` |
| 0x005381e0 | IScript__LevelWon | `LevelWon()` script handler: calls `CGame__DeclareLevelWon(&DAT_008a9a98)` |

### Cheat System

| Address | Function | Description |
|---------|----------|-------------|
| 0x00465490 | IsCheatActive | XOR decrypt + strstr() check |

### CLI Parsing

| Address | Function | Description |
|---------|----------|-------------|
| 0x00423bc0 | CLIParams__ParseCommandLine | Command-line parsing |
| 0x00424150 | (inline) | Guard flag check for -forcewindowed |
| 0x00424168 | (inline) | Set mForceWindowed = 1 |

### Display/D3D

| Address | Function | Description |
|---------|----------|-------------|
| 0x00528f80 | CD3DApplication__Init | Init defaults (640x480) |
| 0x005290a0 | CD3DApplication__Create | Creates D3D device |
| 0x00529350 | CD3DApplication__BuildDeviceList | Enumerate display modes |
| 0x0052af00 | CD3DApplication__Initialize3DEnvironment | Create device, fullscreen/windowed |
| 0x0052b760 | CD3DApplication__Resize3DEnvironment | Resets D3D device + restores vidmem resources after mode/size changes |
| 0x0052b840 | CD3DApplication__ToggleFullscreen | Toggles fullscreen/windowed and reapplies present parameters |
| 0x0052ba50 | CD3DApplication__ForceWindowed | Selects fallback windowable device/mode when fullscreen path fails |
| 0x0052bc80 | CD3DApplication__SelectDeviceProc | Device-selection dialog callback (adapter/device/mode/MSAA UI) |
| 0x0052c4f0 | CD3DApplication__DisplayErrorMsg | Retail error/fatal dispatch for D3D init/reset failures |
| 0x0052c8d0 | CD3DApplication__SetDeviceCursorFromIcon | Uploads Win32 icon mask/color into D3D cursor surface |
| 0x0052c730 | CD3DApplication__SetResolution | Set width/height |

### Localization

| Address | Function | Description |
|---------|----------|-------------|
| 0x00524830 | Localization__GetStringById | Returns `wchar_t*` UI string by id (uses `g_LanguageIndex`) |
| 0x004a4220 | Localization__GetYesNoString | Returns `Localization__GetStringById(5/6)` based on `value==0` |

### Frontend (FEP)

| Address | Function | Description |
|---------|----------|-------------|
| 0x004662a0 | CFrontEnd__Init | 24 FEP pages, player alloc |
| 0x00466980 | CFrontEnd__GetPlayer0ControllerPort | Returns player-0 controller port; normalizes unset sentinel (`-1`) to `0`. |
| 0x00466990 | CFrontEnd__NumControllersPresent | Retail build currently resolves as constant controller-count return path (`2`). |
| 0x00466ab0 | CFrontEnd__SetLanguage | Frontend text/language resource switch helper (`TEXT_DB.Copy(mTextSets[l])` parity). |
| 0x00466ba0 | CFrontEnd__Process | Per-frame frontend processing (EVENT_MANAGER update, pages, controllers, message box) |
| 0x00466ae0 | CFrontEnd__SetPage | Source-parity `CFrontEnd::SetPage(page,time)` page transition helper (calls DeActive/Transition/Active notifications) |
| 0x00466de0 | CFrontEnd__DrawLine | Frontend line draw helper (midpoint + atan2 + scaled link sprite). |
| 0x00466e70 | CFrontEnd__DrawBox | Draws four-sided box via repeated `CFrontEnd__DrawLine` edge draws. |
| 0x00467010 | CFrontEnd__DrawPanel | Clamped blank-panel rectangle draw helper (`FET2_BLANK` style path). |
| 0x004670b0 | CFrontEnd__DrawBarGraph | Panel-backed proportional fill-bar helper (`num/max` foreground draw). |
| 0x00467200 | CFrontEnd__DrawSlidingTextBordersAndMask | High-fanout transition bracket/mask renderer for frontend page transitions. |
| 0x004679a0 | CFrontEnd__HasStandardSlidingTextBordersAndMask | Static page-style predicate used by border/mask transition renderer. |
| 0x00467ae0 | CFrontEnd__DrawBar | Segmented bar helper (left/center/right texture strips). |
| 0x00467bd0 | CFrontEnd__DrawTitleBar | Animated title-bar draw path (shadow offsets + transition alpha/scale shaping). |
| 0x004681c0 | CFrontEnd__EnableAdditiveAlpha | Sets additive blend mode (`ONE/ONE`). |
| 0x004681e0 | CFrontEnd__EnableModulateAlpha | Sets alpha-modulate blend mode (`SRCALPHA/INVSRCALPHA`). |
| 0x00468200 | CFrontEnd__Render | Frontend render pass used by `CFrontEnd__Run` while-wait loop |
| 0x004684d0 | CFrontEnd__Run | Main loop, state machine |
| 0x00468730 | CFrontEnd__GetShadowOffsetX | Returns animated X shadow offset (`sin(counter/period) * radius_x`). |
| 0x00468750 | CFrontEnd__GetShadowOffsetY | Returns animated Y shadow offset (`cos(counter/period) * radius_y`). |
| 0x00468770 | CFrontEnd__PlaySound | Source-parity UI sound helper (`Front End Move/Select/Back`) by enum/id |
| 0x00466190 | CFEPMultiplayerStart__scalar_deleting_dtor | FEP MultiplayerStart scalar deleting dtor wrapper (`dtor` + optional free) |
| 0x00466200 | CFEPMultiplayerStart__dtor | FEP MultiplayerStart destructor body (cleanup + monitor shutdown path) |
| 0x00459920 | CFEPMultiplayerStart__SubObj8848__ctor | Embedded helper ctor called from `CFEPMultiplayerStart__ctor` (ECX=`this+0x8848`); sets vtable `0x005db4fc`, zeros selection tables, seeds defaults. |
| 0x004599a0 | CFEPMultiplayerStart__SubObj8848__Init | Embedded subobject vtable slot 0; recovered headlessly and signature-normalized (`int ... (void * this)`). |
| 0x00459a60 | CFEPMultiplayerStart__SubObj8848__ActiveNotification | Embedded subobject active-notification hook (`from_page`), recovered headlessly from prior create-function backlog. |
| 0x00459aa0 | CFEPMultiplayerStart__SubObj8848__TransitionNotification | Embedded subobject transition-notification path; timestamp reset + 300-entry grid clear + mode-dependent highlight for pages 5/6. |
| 0x00459b00 | CFEPMultiplayerStart__SubObj8848__Process | Embedded subobject process hook (`menu_state`), recovered headlessly from prior create-function backlog. |
| 0x00459c10 | CFEPMultiplayerStart__SubObj8848__ButtonPressed | Embedded subobject button handler recovered headlessly from prior create-function backlog. |
| 0x00459e50 | CFEPMultiplayerStart__SubObj8848__RenderPreCommon | Embedded subobject pre-render hook (`transition`), recovered headlessly from prior create-function backlog. |
| 0x00459ee0 | CFEPMultiplayerStart__SubObj8848__Render | Embedded subobject render hook (`transition`, `dest`), recovered headlessly from prior create-function backlog. |
| 0x00459810 | CFEPMultiplayerStart__SubObj39B8__QueuePageId | Embedded helper called from `CFrontEnd__Init` with ECX=`this+0x39b8`; stores queued startup page id from `DAT_0066304c`. |
| 0x0051b600 | CFEPMultiplayerStart__SubObj4034__ctor | Embedded helper ctor called from `CFEPMultiplayerStart__ctor` (ECX=`this+0x4034`); installs vtable `0x005e49b4` and sets base runtime defaults. |
| 0x0051b610 | CFEPMultiplayerStart__SubObj4034__ResetFlags | Embedded helper resetting runtime flags (`+0x0c/+0x10`) and global gate `DAT_00677614` under `DAT_0083d448` guard. |
| 0x0051be70 | CFEPMultiplayerStart__SubObj4034__InitRuntimeState | Embedded helper setting runtime timestamp (`PLATFORM__GetSysTimeFloat`), clearing transition globals, and resetting subobject state. |
| 0x00513af0 | D3DStateCache__SetSlotMode4or5 | High-fanout D3D render-state cache helper: writes per-slot cache `DAT_008557f4` and issues device vfunc `+0x10c` when transitioning cached state to mode 4/5. |
| 0x00513820 | D3DStateCache__SetStateCached | Cached D3D state setter for per-slot state array `DAT_008557f0` with device vfunc `+0x10c` emission on value change. |
| 0x00513870 | D3DStateCache__SetStateRaw | Unconditional D3D state setter for per-slot state array `DAT_008557f0` with immediate device vfunc `+0x10c` call. |
| 0x005138b0 | D3DStateCache__SetState114Cached | Cached policy-gated setter using device vfunc `+0x114` (special handling for state ids 6/8/10 and caps flags). |
| 0x00513930 | D3DStateCache__SetState114Raw | Raw policy-gated setter using device vfunc `+0x114` (same state-id filters as cached variant, no cache write). |
| 0x00513a50 | CEngine__SetRenderStateCached | Engine-local cached render-state wrapper (`this+0x32ea0` device object, vfunc `+0x104`) with global cache array `DAT_008554d0`. |
| 0x00513b60 | D3DStateCache__ForceSlotMode4or5 | Unconditional per-slot mode setter (state id 1 -> value 4/5) with immediate device vfunc `+0x10c` call. |
| 0x00513a80 | PlatformInput__GetKeyState3Core | Low-level key-state byte fetch used by `CPCController__GetKeyState3` (reads `this + 0x332e4 + key`). |
| 0x00513a90 | PlatformInput__GetKeyOnceCore | Low-level edge-trigger key poll used by `CPCController__GetKeyOnce`; reads+clears latch byte at `this + 0x331e4 + key` and maintains pending queue (`DAT_00855424..`). |
| 0x00513800 | IUnknown__ReleaseIfNonNull_ReturnZero | Null-safe COM-release helper (`if (obj) obj->Release(); return 0`), used by VBuffer release paths. |
| 0x00513600 | D3DStateCache__ResetSentinelTable | Initializes `DAT_00855540` sentinel table with `0xFEDCBA98` across 0xAC dwords. |
| 0x00513650 | CEngine__PrintGraphicsCardInfo | Console diagnostics helper printing graphics card/device capability strings. |
| 0x005139a0 | CEngine__CreateTextureOrFatal | Engine texture-create wrapper using device vfunc `+0x5c`; logs D3D error string and raises fatal on failure. |
| 0x00513a10 | CEngine__CreateTextureUnchecked | Unchecked variant of device vfunc `+0x5c` texture-create wrapper (no fatal/error reporting). |
| 0x00513770 | CEngine__DeviceCall68_CheckError | Engine device-call wrapper (`+0x68`) with debug-trace D3D error reporting on failed HRESULT. |
| 0x005137d0 | CEngine__DeviceCall6C | Engine wrapper over device vfunc `+0x6c` call path (unchecked). |
| 0x005159c0 | PLATFORM__SetKeySink | Public key-sink registration wrapper used by console/remap/UI flows; forwards to `PlatformInput__SetKeySinkCore`. |
| 0x005135f0 | PlatformInput__SetKeySinkCore | Core key-sink setter used by virtual keyboard process/shutdown and `PLATFORM__SetKeySink` wrapper (`this + 0x33458 = key_sink`). |
| 0x005134a0 | CEngine__GrabScreenshot | Screenshot capture helper (`grabs_scr_%4d.tga`) called by frontend cheat-check/update path. |
| 0x00513370 | PlatformInput__PollPadState | Per-pad DirectInput poll/update helper (supports optional button rotation path, reacquire on input-loss). |
| 0x00513120 | PlatformInput__InitDirectInput | DirectInput startup/enumeration path (joypad detection, device setup, callback registration, per-pad capability initialization). |
| 0x0051bfa0 | CFEPLanguageTest__Init | Dev/debug FEP page init ("LANGUAGE TEST"); previously misattributed as MultiplayerStart due to vtable mix-up (corrected 2026-02-13) |
| 0x0051ff90 | CFEPVirtualKeyboard__Init | Virtual-keyboard page init (vtable `0x005db830`, RTTI `.?AVCFEPVirtualKeyboard@@`) |
| 0x0051ffd0 | CFEPVirtualKeyboard__Shutdown | Virtual-keyboard page shutdown helper |
| 0x005202d0 | CFEPVirtualKeyboard__Process | Virtual-keyboard process loop; state-driven directory refresh/context setup |
| 0x00520370 | CFEPVirtualKeyboard__ButtonPressed | Virtual-keyboard input handler (nav/select/back/char cycle) |
| 0x00521100 | CFEPVirtualKeyboard__Render | Virtual-keyboard page render path (transition alpha/draw flow) |
| 0x00520130 | CFEPVirtualKeyboard__TransitionNotification | Virtual-keyboard transition hook; save-name reseed/reset on selected page transitions |
| 0x0051f9f0 | CFEPScreenPos__Init | Screen-position page init (vtable `0x005db858`) |
| 0x0051fa00 | CFEPScreenPos__ButtonPressed | Screen-position calibration input handler (range adjust + page flow) |
| 0x0051fb60 | CFEPScreenPos__RenderPreCommon | Screen-position pre-common transition draw helper |
| 0x0051fb90 | CFEPScreenPos__Render | Screen-position render path ("Adjust Screen Position" overlays) |
| 0x0051fd50 | CFEPScreenPos__TransitionNotification | Screen-position page transition hook (vtable `0x005db858`, RTTI `.?AVCFEPScreenPos@@`) |

### God Mode Toggle

| Address | Function | Description |
|---------|----------|-------------|
| 0x004ce328 | (PauseMenu__Init) | God-mode menu toggle label check: reads `g_bGodModeEnabled` (`0x00662ab4` = `CAREER+0x2494`) |

### Memory Management

| Address | Function | Description |
|---------|----------|-------------|
| 0x00549270 | MEM_MANAGER__Cleanup | Source-level cleanup wrapper (`MEM_MANAGER.Cleanup()`) used in restart/load cleanup paths |
| 0x0041xxxx | CMemoryManager__Init | Initialize heap |
| 0x0041xxxx | CMemoryManager__Alloc | Allocate memory |
| 0x0041xxxx | CMemoryManager__Free | Free memory |

### Console System

| Address | Function | Description |
|---------|----------|-------------|
| 0x00429bc0 | CConsole__Init | Initialize console |
| 0x00429ef0 | CConsole__RegisterBuiltinCommands | Register commands |
| 0x0042a410 | CConsole__ResetLayoutForWindowHeight | Recomputes console layout metrics (`+0x2384/+0x2388/+0xb3cc`) from current window height |
| 0x0042a4f0 | CConsole__ExecuteBufferedCommandSlot | Executes selected buffered line (`this+0x23BC`) through `CConsole__ExecuteCommandLine` when non-empty |
| 0x0042a460 | CConsole__ListBinds | Lists current key bindings by iterating key->bind tables and printing formatted lines |
| 0x0042a540 | CConsoleVar__GetTypeName | Maps cvar type enum (`+0xa0`) to printable type label (`DWORD/string/float/fvector/fmatrix/...`) |
| 0x0042a5f0 | CConsoleVar__FormatValueToString | Formats cvar value text by type using value pointer at `+0xa4` |
| 0x0042a770 | CConsole__FindCommandByName | Linked-list lookup of command entry by name (`this+0x2394`, `stricmp`) |
| 0x0042a7b0 | CConsole__SetVariableByName | Resolves console variable by name and applies typed value parsing/writes with read-only checks |
| 0x0042ad30 | CConsole__ExecScript | `Exec` script handler: reads script file and dispatches each line as a console command |
| 0x0042ae70 | CConsole__ShutdownAndFreeAllLists | Full console teardown helper (frees command/var lists plus owned aux pointers) |
| 0x0042af20 | CConsole__ClearCommandAndVariableLists | Clears/frees command and variable lists only |
| 0x0042af80 | CConsole__RegisterCommand | Register single command |
| 0x0042b040 | CConsole__RegisterVariable | Register cvar |
| 0x0042b120 | CConsole__HandleBind | Console input/bind handler (toggle/history/navigation/tab-complete/dispatch paths) |
| 0x0042ba90 | CConsole__MenuUp | Console menu cursor up (decrement/clamp selection index) |
| 0x0042bac0 | CConsole__MenuDown | Console menu cursor down (increment/clamp selection index) |
| 0x0042bb30 | CConsole__MenuSelect | Console menu select/activate current entry |
| 0x0042b500 | CConsole__Status | Start nested status section (`...` suffix) and increment depth |
| 0x0042b650 | CConsole__StatusUpdateLine | Internal status line rewrite helper used by status/progress completion paths |
| 0x0042b800 | CConsole__StatusDone | Complete status section (success/fail) and decrement depth |
| 0x0042b840 | CConsole__AddString | Core variadic console text sink (formats and appends/splits rolling lines) |
| 0x0042b9c0 | CConsole__ExecuteCommandLine | Tokenizes input line and dispatches matching command callback (`Unknown command` fallback) |
| 0x0042bbc0 | CConsole__SetLoading | Loading-screen mode toggle (enable/disable, texture lifecycle, loading-timer logging) |
| 0x0042bcf0 | CConsole__InitKeyNameTable | Initializes console key-name table strings (Backspace/Return/Shift/arrows/num keys) |
| 0x0042c810 | CConsole__RenderLoadingScreen | Loading-screen render/update helper (progress bar + localized loading text path) |
| 0x0042cf40 | CConsole__SetLoadingRange | Loading progress range setter (`min/max` + UI refresh) |
| 0x0042cf70 | CConsole__SetLoadingFraction | Loading progress interpolation setter (`t` within active range + UI refresh) |
| 0x0042c750 | FatalError__ExitWithLocalizedPrefix_A | Fatal wrapper: prepends localized prefix (`Localization id 0xCC`) and exits process |
| 0x0042d0b0 | FatalError__ExitWithLocalizedPrefix_B | Fatal wrapper variant used in mesh/resource deserialize failure paths |
| 0x0042d260 | OptionsEntries__InitSingleBindingEntry | Initializes one persisted options-entry binding slot (`active`, `entry_id`, slot-0 device/scan/vk fields) |
| 0x0042d2b0 | OptionsEntries__InitDualBindingEntry | Initializes dual-binding options entries (slot-0 + slot-1 metadata) during static control-binding table setup |
| 0x0042d300 | OptionsEntries__InitSentinelEntry | Sentinel/reset helper paired with the options-entry initialization sequence |
| 0x00453460 | OptionsEntries__InitDefaultDualBindingsTable | Builds default dual-binding table at `DAT_00677af0` via repeated `OptionsEntries__InitDualBindingEntry` calls plus sentinel rows |
| 0x00514210 | OptionsEntries__InitDefaultSingleBindingsTable | Builds default single-binding table at `DAT_008892d8` via repeated `OptionsEntries__InitSingleBindingEntry` calls plus sentinel row |
| 0x00453970 | CControllerDefinition__InitDefaults | Initializes `CControllerDefinition` defaults and vtable before controls remap/preset paths |
| 0x004539b0 | CControllerDefinition__scalar_deleting_dtor | Scalar deleting dtor wrapper (`dtor` + optional `OID__FreeObject` by flag) |
| 0x004539d0 | CControllerDefinition__dtor | `CControllerDefinition` destructor body (key-sink gate reset + owned pointer release) |
| 0x0042d310 | PlatformInput__InitMouse | Creates/acquires DirectInput mouse device; resets mouse globals/profiler and center coordinates |
| 0x0042d3b0 | PlatformInput__ShutdownMouse | Unacquires/releases DirectInput mouse device; refreshes stored cursor position |
| 0x0042d420 | PlatformInput__PollMouseMotion | Polls mouse deltas and updates cursor/wheel globals; reacquires on transient input loss |
| 0x0042d4d0 | PlatformInput__PollMouseState | Polls motion + button transitions (left/right/middle) and updates edge/held globals |

### Physics Script Statement Helpers

| Address | Function | Description |
|---------|----------|-------------|
| 0x0042f5f0 | CWeaponStatement__Create | Allocates/initializes weapon-statement node and appends to statement set (`DAT_008553e8`) |
| 0x0042f750 | CWeaponStatement__GetSerializedSize | Recursive byte-size accumulator for weapon-statement tree |
| 0x0042fa80 | CWeaponModeStatement__Create | Allocates/initializes weapon-mode statement node and appends to statement set (`DAT_008553ec`) |
| 0x0042fc70 | CWeaponModeStatement__GetSerializedSize | Recursive byte-size accumulator for weapon-mode statement tree |
| 0x0042ffa0 | CRoundStatement__Create | Allocates/initializes round-statement node and appends to statement set (`DAT_008553f0`) |
| 0x004301e0 | CRoundStatement__GetSerializedSize | Recursive byte-size accumulator for round-statement tree |
| 0x00433390 | CComponentBasedOn__CopyFrom | Deep-copy helper used by component-based statement path (`CComponentBasedOn__VFunc_01_0043db90`) |

### Unit System

| Address | Function | Description |
|---------|----------|-------------|
| 0x004f39c0 | CThing__AddCollision | Collision at this+0x38 |
| 0x004f4120 | CThing__SetName | Name at this+0x78 |
| 0x004f4230 | CThing__SetSound | Sound at this+0x74 |
| 0x004f44a0 | CThing__AddTrail | Trail at this+0x6c |

---

## String Addresses

### CLI Parameter Strings

| Address | String |
|---------|--------|
| 0x006244a0 | "-forcewindowed" |

### File Mode Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x00629038 | "rb" | Binary read (load) |
| 0x0063316c | "wb" | Binary write (save) |
| 0x0063df7c | "savegames\\*.bes" | Save file pattern |
| 0x0063df94 | "savegames\\" | Save directory |

### Config Strings

| Address | String | Purpose |
|---------|--------|---------|
| 0x0064be10 | "ALLOW_WIDESCREEN_MODES" | Config file key |

### Error/Warning Strings

| Address | String |
|---------|--------|
| 0x006241b4 | "WARNING: Could not find career node from world number %d" |
| 0x006241f0 | "FATAL ERROR: Can't update career because can't find node for world %d" |
| 0x00624238 | "Updating career (world %d completed)" |
| 0x00624288 | "%-15s killed this level %d, Total %d" |
| 0x006242ec | "Error: no career node for world %d" |
| 0x00624318 | "Error: Outside slot range (%d) in call to GetSlot" |
| 0x0062434c | "Error: Outside slot range (%d) in call to SetSlot" |
| 0x0062c368 | "WARNING : THING HEAP NEARLY FULL!" |
| 0x0062f938 | "Mesh '%s' leaked : refcount=%d\n" |
| 0x0062f7b8 | "Writing memory dump '%s'\n" |

---

## Debug Path Strings (166 total)

Format: `C:\dev\ONSLAUGHT2\[filename]`

### High-Priority Source Files

| Address | Source File | Priority |
|---------|-------------|----------|
| 0x00631690 | Player.cpp | HIGH |
| 0x006230bc | BattleEngine.cpp | HIGH |
| 0x006243bc | Carrier.cpp | HIGH |
| 0x00633b6c | Unit.cpp | HIGH |
| 0x0062e0e0 | Mech.cpp | HIGH |
| 0x0062d4a8 | Infantry.cpp | MEDIUM |
| 0x00623a78 | Bomber.cpp | MEDIUM |
| 0x00628b40 | engine.cpp | MEDIUM |
| 0x0062f590 | MemoryManager.cpp | MEDIUM |
| 0x00632428 | SoundManager.cpp | MEDIUM |

### Complete Debug Path Index (Alphabetical)

| Address | Source File |
|---------|-------------|
| 0x00622cf4 | AirUnit.cpp |
| 0x00622ec4 | Atmospherics.cpp |
| 0x006230bc | BattleEngine.cpp |
| 0x006235a8 | BattleEngineConfigurations.cpp |
| 0x00623674 | BattleEngineDataManager.cpp |
| 0x00623990 | Boat.cpp |
| 0x00623a78 | Bomber.cpp |
| 0x00623ab8 | BSpline.cpp |
| 0x00623af4 | Building.cpp |
| 0x00623c18 | bytesprite.cpp |
| 0x00623c90 | Camera.cpp |
| 0x00623dd4 | Cannon.cpp |
| 0x006243bc | Carrier.cpp |
| 0x00624400 | Carver.cpp |
| 0x00624464 | chunker.cpp |
| 0x00624630 | CollisionSeekingRound.cpp |
| 0x006246d8 | collisionseekingthing.cpp |
| 0x006247f8 | Component.cpp |
| 0x00624d0c | console.cpp |
| 0x00625538 | Controller.cpp |
| 0x0062568c | CPhysicsScript.cpp |
| 0x00625818 | CPhysicsScriptStatements.cpp |
| 0x0062811c | Cutscene.cpp |
| 0x006282dc | damage.cpp |
| 0x006287b4 | DestructableSegmentsController.cpp |
| 0x006289c0 | DiveBomber.cpp |
| 0x00628a54 | Dropship.cpp |
| 0x00628b40 | engine.cpp |
| 0x00628d3c | eventmanager.cpp |
| 0x00628fac | FEPBEConfig.cpp |
| 0x0062913c | FEPDebriefing.cpp |
| 0x0062921c | FEPDevelopment.cpp |
| 0x00629318 | FEPGoodies.cpp |
| 0x006293c0 | FEPLoadGame.cpp |
| 0x00629414 | FEPMain.cpp |
| 0x00629a78 | FEPSaveGame.cpp |
| 0x00629a9c | flexarray.cpp |
| 0x00629df0 | FrontEnd.cpp |
| 0x0062bba4 | game.cpp |
| 0x0062c968 | gcgamut.cpp |
| 0x0062c9e8 | GillM.cpp |
| 0x0062ca6c | GillMHead.cpp |
| 0x0062cadc | GroundAttackAircraft.cpp |
| 0x0062cb0c | GroundUnit.cpp |
| 0x0062cb30 | GroundVehicle.cpp |
| 0x0062cbd0 | HeightField.cpp |
| 0x0062cc98 | HiveBoss.cpp |
| 0x0062ce76 | Hud.cpp |
| 0x0062d390 | ibuffer.cpp |
| 0x0062d3cc | imageloader.cpp |
| 0x0062d3f0 | imposter.cpp |
| 0x0062d4a8 | Infantry.cpp |
| 0x0062d61c | InfluenceMap.cpp |
| 0x0062d7b0 | InitThing.cpp |
| 0x0062d824 | landscapeib.cpp |
| 0x0062d8e0 | LandscapeTexture.cpp |
| 0x0062db04 | maptex.cpp |
| 0x0062db88 | mapwho.cpp |
| 0x0062dc80 | MCBuggy.cpp |
| 0x0062df60 | MCMech.cpp |
| 0x0062e06c | MCTentacle.cpp |
| 0x0062e0e0 | Mech.cpp |
| 0x0062f590 | MemoryManager.cpp |
| 0x0062f7d8 | MenuItem.cpp |
| 0x0062f8e8 | mesh.cpp |
| 0x0062fe40 | MeshCollisionVolume.cpp |
| 0x0062fe70 | MeshPart.cpp |
| 0x00630178 | MeshRenderer.cpp |
| 0x006309a4 | Mine.cpp |
| 0x006309c0 | Missile.cpp |
| 0x00630a4c | Music.cpp |
| 0x00630c20 | oids.cpp |
| 0x00630cd8 | ParticleDescriptor.cpp |
| 0x00630e60 | ParticleManager.cpp |
| 0x00630fb0 | ParticleSet.cpp |
| 0x006314dc | PauseMenu.cpp |
| 0x00631630 | Plane.cpp |
| 0x00631654 | Platform.cpp |
| 0x00631690 | Player.cpp |
| 0x006316bb | PolyBucket.cpp |
| 0x00631784 | RadarWarningReceiver.cpp |
| 0x00631b7c | ResourceAccumulator.cpp |
| 0x00631d38 | Round.cpp |
| 0x00631e2c | RTCutscene.cpp |
| 0x00631f28 | rtmesh.cpp |
| 0x0063221c | Sentinel.cpp |
| 0x00632428 | SoundManager.cpp |
| 0x00632650 | SpawnerThng.cpp |
| 0x0063270c | SphereTrigger.cpp |
| 0x00632730 | SPtrSet.cpp |
| 0x0063283c | SquadNormal.cpp |
| 0x00632918 | SquadRelaxed.cpp |
| 0x006329f8 | StaticShadows.cpp |
| 0x00632abc | Submarine.cpp |
| 0x00632ccc | Tentacle.cpp |
| 0x00632dd8 | text.cpp |
| 0x00632ef0 | texture.cpp |
| 0x0063314c | tgaloader.cpp |
| 0x006331c0 | thing.cpp |
| 0x00633240 | ThunderHead.cpp |
| 0x00633a00 | TokenArchive.cpp |
| 0x00633a84 | tree.cpp |
| 0x00633ab8 | triangulate.cpp |
| 0x00633b6c | Unit.cpp |
| 0x00633d08 | vbuffer.cpp |
| 0x00633d5c | vbuftexture.cpp |
| 0x0063cf78 | VertexShader.cpp |
| 0x0063d12c | Warspite.cpp |
| 0x0063d170 | WarspiteDome.cpp |
| 0x0063d1b0 | wavread.cpp |
| 0x0063d1f8 | WaypointManager.cpp |
| 0x0063d2ac | world.cpp |
| 0x0063d488 | WorldMeshList.cpp |
| 0x0063d798 | WorldPhysicsManager.cpp |
| 0x0063dd8c | ltshell.cpp |
| 0x0063e03c | PCPlatform.cpp |
| 0x0063e284 | PCRTID.cpp |
| 0x0063e46c | pcsoundmanager.cpp |
| 0x0063fb24 | FastVB.cpp |
| 0x0063fb4c | FEPDirectory.cpp |
| 0x0063fc24 | FEPMultiplayerStart.cpp |
| 0x0063fc88 | FEPOptions.cpp |
| 0x0063fd4c | FEPWingmen.cpp |
| 0x00640030 | mixermap.cpp |

### MissionScript Subfolder

| Address | Source File |
|---------|-------------|
| 0x0064c5c4 | MissionScript/AsmInstruction.cpp |
| 0x0064cc80 | MissionScript/DataType.cpp |
| 0x0064cce0 | MissionScript/EventFunction.cpp |
| 0x0064fa40 | MissionScript/IScript.cpp |
| 0x0064fe98 | MissionScript/ScriptEventNB.cpp |
| 0x00650040 | MissionScript/ScriptObjectCode.cpp |
| 0x00650134 | MissionScript/Symtab.cpp |

### DirectX Files

| Address | Source File |
|---------|-------------|
| 0x00650324 | DXBattleLine.cpp |
| 0x006503d4 | DXClouds.cpp |
| 0x00650454 | DXCompass.cpp |
| 0x00650644 | DXFMV.CPP |
| 0x00650670 | DXFont.cpp |
| 0x00650744 | DXFrontEndVideo.cpp |
| 0x006508cc | DXImposter.cpp |
| 0x00650a88 | DXKempyCube.cpp |
| 0x00650bdc | DXLandscape.cpp |
| 0x00650fd0 | DXMemBuffer.cpp |
| 0x00651244 | DXMeshVB.cpp |
| 0x00651d60 | DXPalletizer.cpp |
| 0x00651dcc | DXParticleTexture.cpp |
| 0x0065211c | DXPatchManager.cpp |
| 0x00652410 | DXShadows.cpp |
| 0x00652534 | DXSnow.cpp |
| 0x006525a0 | DXSurf.cpp |
| 0x0065269c | DXTexture.cpp |
| 0x006529b0 | DXTrees.cpp |

---

## Known Binary Patches

### Widescreen Patch (Community)

| Region | File Offset | VA | Original | Patched | Purpose |
|--------|-------------|-----|----------|---------|---------|
| 1 | 0x0001B087 | 0x0041B087 | `C4 8B 5D` | `F0 4F 9D` | Data reference update |
| 2 | 0x000506CE | 0x004506CE | `68 00 00 40 3F` | `E9 5F 78 18 00` | Hook: JMP to code cave |
| 3 | 0x00129696 | 0x00529696 | `CC` | `00` | NOP padding |
| 4 | 0x0012B156 | 0x0052B156 | `D9 05 F0 4A 5E 00` | `E9 07 CD 0A 00 90` | Hook aspect ratio |
| 5 | 0x0012B200 | 0x0052B200 | `E8 3B 65 F1 FF` | `E9 98 CD 0A 00` | Another aspect hook |

**Code Cave:** 0x005D7DB5 - 0x005D7FFD (~600 bytes of new code)

### Windowed Mode Enable Patch

| File Offset | Original | Patched | Purpose |
|-------------|----------|---------|---------|
| 0x262F3E | 0x00 | 0x01 | Enable -forcewindowed guard flag |

### Extra Graphics Gate Default Patch

| File Offset | VA | Original | Patched | Purpose |
|-------------|----|----------|---------|---------|
| 0x0CDD40 | 0x004CDD40 | `6A 00` | `6A 01` | Change `GEFORCE_FX_POWER` tweak registration default from disabled to enabled (retail cardid default gate unlock). |

### Ignore cardid Override Load Patch

| File Offset | VA | Original | Patched | Purpose |
|-------------|----|----------|---------|---------|
| 0x12AF3F | 0x0052AF3F | `E8 9C D7 FF FF` | `90 90 90 90 90` | Bypass startup call into `CD3DApplication__LoadCardIdAndApplyVendorTweaks` so executable defaults are used directly. |

### Dev-Mode Goodies Fix (Disable `lat\xEAte` Flag in Gallery)

**Note:** MALLOY works without this patch via save-name checks. This patch is only useful if you enable `g_bAllCheatsEnabled` (dev mode), which makes `IsCheatActive()` return TRUE for all indices including the goodies-only `lat\xEAte` cheat (index 5). In the goodies UI, that can interfere with “unlock everything” testing.

| Address | Original | Patched | Purpose |
|---------|----------|---------|---------|
| 0x0045D819 | `F7 D8` (NEG EAX) | `33 C0` (XOR EAX,EAX) | Force `g_Cheat_LATETE = 0` in `CFEPGoodies::Process` |

### Force Cheats (Archived / Experimental)

| Address | Original | Patched | Purpose |
|---------|----------|---------|---------|
| 0x00465490 | prologue | `MOV EAX,1; RET 4` | Force `IsCheatActive()` TRUE (breaks goodies unless `lat\xEAte` is also mitigated) |
| 0x004654a0 | 75 (JNZ) | EB (JMP) | Legacy: bypass final return-path branch in `IsCheatActive()` (does not force TRUE for all cases) |

---

## Console Variables (CVars)

| Address | Name | Type | Default | Notes |
|---------|------|------|---------|-------|
| 0x0067a070 | cg_gamutlocked | bool | 0 | Freezes gamut calculation |
| 0x0067a071 | cg_showgamut | bool | 0 | Displays gamut visualization |
| 0x0062c8c4 | cg_renderimposters | bool | ? | Controls imposter rendering |

---

## RTTI Class Names

| Address | Class Name |
|---------|------------|
| 0x0062bc28 | CGame |
| 0x00631680 | CPlayer |
| 0x00623248 | CBattleEngine |
| 0x00633ae0 | CUnit |
| 0x00631cf8 | CRound |
| 0x0063d260 | CWeapon |
| 0x006327f0 | CSquad |
| 0x00629c18 | CFEPGoodies |
| 0x00629cf8 | CFEPSaveGame |
| 0x00629d60 | CFEPLoadGame |
| 0x00629d40 | CFEPDebriefing |
| 0x00629cb8 | CFEPOptions |
| 0x00629d80 | CFEPMain |
| 0x00629d18 | CFEPVirtualKeyboard |
| 0x00629db8 | CFEPScreenPos |

## Recent Headless Recoveries (2026-02-25)

Recovered in headless mode with `CreateFunctionsFromAddressList.java` + `GhidraBatchRename.java` + `ApplyMenuItemRecoveredSignatures.java` (all with read-back verification).

| Address | Symbol | Signature |
|---------|--------|-----------|
| 0x00405930 | CControllerDefinition__VFunc_03_00405930 | `int __thiscall CControllerDefinition__VFunc_03_00405930(void * this)` |
| 0x00453a50 | CMenuItem__ButtonPressed_NoOp | `void __thiscall CMenuItem__ButtonPressed_NoOp(void * this, int from_controller, int button)` |
| 0x00453a60 | CMenuItem__IsEnabled | `int __thiscall CMenuItem__IsEnabled(void * this)` |
| 0x00453a70 | CMenuItem__GetRowHeight | `int __thiscall CMenuItem__GetRowHeight(void * this)` |
| 0x00453a80 | CMenuItem__DefaultFalseFlag | `byte __thiscall CMenuItem__DefaultFalseFlag(void * this)` |
| 0x00453a90 | CMenuItem__scalar_deleting_dtor | `void * __thiscall CMenuItem__scalar_deleting_dtor(void * this, byte flags)` |
| 0x004a3140 | CMenuItem__Clone | `void * __thiscall CMenuItem__Clone(void * this)` |
| 0x004a3190 | CMenuItem__GetText | `short * __thiscall CMenuItem__GetText(void * this)` |
| 0x004a3420 | CMenuItem__GetTextWidth | `int __thiscall CMenuItem__GetTextWidth(void * this)` |

Wave 2 (MenuItem dropdown/slider slot recovery):

| Address | Symbol | Signature |
|---------|--------|-----------|
| 0x004a37c0 | CMenuItem__RenderValueBar | `void __thiscall CMenuItem__RenderValueBar(void * this, float x, float y, int interactive)` |
| 0x004a3be0 | CMenuItemDropdown__RenderOrQueueDeferred | `void __thiscall CMenuItemDropdown__RenderOrQueueDeferred(void * this, float x, float y, int interactive)` |
| 0x004a40e0 | CMenuItemDropdown__IsExpanded | `byte __thiscall CMenuItemDropdown__IsExpanded(void * this)` |
| 0x004a4110 | CMenuItemDropdown__ButtonPressed | `void __thiscall CMenuItemDropdown__ButtonPressed(void * this, int from_controller, int button)` |
| 0x004a4290 | CMenuItemSlider__ButtonPressed | `void __thiscall CMenuItemSlider__ButtonPressed(void * this, int from_controller, int button)` |
| 0x004a42f0 | CMenuItemDropdown__HasPendingSelectionChange | `bool __thiscall CMenuItemDropdown__HasPendingSelectionChange(void * this)` |
| 0x004a4310 | CMenuItemSlider__Render | `void __thiscall CMenuItemSlider__Render(void * this, float x, float y, int alpha)` |
| 0x004a43a0 | CMenuItem__ButtonPressed | `void __thiscall CMenuItem__ButtonPressed(void * this, int from_controller, int button)` |
| 0x004a4450 | CMenuItem__GetWidth | `int __thiscall CMenuItem__GetWidth(void * this)` |

---

## Structure Offsets

### CLIParams (base: 0x0089c0a0)

| Offset | Type | Field |
|--------|------|-------|
| 0x38 | bool | m_bForceWindowed |
| 0x164 | int | m_nResWidth |
| 0x168 | int | m_nResHeight |

### CD3DApplication

| Offset | Type | Field |
|--------|------|-------|
| 0x32e64 | bool | m_bWindowed |
| 0x330bc | DWORD | m_dwCreationWidth |
| 0x330c0 | DWORD | m_dwCreationHeight |

---

## Naming Conventions

### Function Names

Pattern: `ClassName__FunctionName`

Examples:
- `CCareer__Blank`
- `CCareerNode__SetBaseThingExistTo`
- `CLIParams__ParseCommandLine`
- `CFrontEnd__Run`

### Global Variables

Pattern: `g_` prefix for globals

Examples:
- `g_bDevModeEnabled`
- `g_bAllCheatsEnabled`
- `g_pPhysicsScript`

### Data Labels

Pattern: `DAT_` prefix for Ghidra-generated data labels

Example: `DAT_00662f3e` (guard flag)

---

## Function Discovery Method

1. **Debug Path Xrefs**: Find xrefs to debug path strings (e.g., `0x00631690` for Player.cpp)
2. **Error String Xrefs**: Find xrefs to error/warning strings
3. **RTTI Analysis**: Use RTTI class names to identify class methods
4. **Vtable Analysis**: Follow vtable pointers to virtual functions
5. **Call Graph**: Trace function calls from known entry points

---

## Statistics

| Metric | Count |
|--------|-------|
| Total Functions in Binary | 5,861 |
| Named Functions | 5,861 (100.00%) |
| Source-file entries tracked (`Functions` numeric rows) | 158 |
| Source-file corpus represented (`Functions` numeric sum) | 1,059 |
| Debug Path Strings (current canonical tracking) | 169 |
| Error Strings Found | 50+ |
| RTTI Classes Found | 30+ |
| Markdown docs under `functions/` | 358 |

---

## Quick Reference

### Find Function from Debug Path

1. Go to debug path address (e.g., `0x00631690` for Player.cpp)
2. List xrefs (References > Show References to Address)
3. Each xref is likely a function from that source file
4. Decompile to confirm

### Check Guard Flag State

```
Goto 0x00662f3e
Read byte value:
  0x00 = DISABLED (feature blocked)
  0x01 = ENABLED (feature active)
```

### XOR Decrypt Cheat Code

```
Key: "HELP ME!!" (9 bytes, at 0x00629a64)
Data: 256 bytes starting at 0x00629464 + (index * 256)
Algorithm: XOR each byte with key[i % 9]
```

---

*Generated from binary analysis documentation - December 2025*
*Tools: Ghidra 12.x + GhydraMCP (ports 8192+)*

### Semantic Wave33 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0052b760 | CD3DApplication__Resize3DEnvironment | Source-parity with `CD3DApplication::Resize3DEnvironment` reset/restore flow. |
| 0x0052b840 | CD3DApplication__ToggleFullscreen | Source-parity fullscreen toggle path with fallback routing. |
| 0x0052ba50 | CD3DApplication__ForceWindowed | Source-parity fallback path to windowable adapter/device mode. |
| 0x0052bc80 | CD3DApplication__SelectDeviceProc | Source-parity `SelectDeviceProc` dialog callback behavior. |
| 0x0052c4f0 | CD3DApplication__DisplayErrorMsg | Retail fatal/error dispatch mapped from HRESULT-style codes. |
| 0x0052c8d0 | CD3DApplication__SetDeviceCursorFromIcon | Device cursor upload helper inferred from icon-mask/color conversion and caller parity. |

### Semantic Wave34 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x004e0b30 | CSoundManager__PlaySample | Source-parity wrapper from `PlayNamedSample`; performs once-only duplicate suppression then routes into core playback path. |
| 0x004e0f70 | CSoundManager__StopSoundEvent | Event stop/cleanup helper: owner-complete callback, channel release, clear playing/reader state. |
| 0x004e1040 | CSoundManager__SortEventList | Source-parity priority-sort + channel rebalance (`3/4` channel budget path) for active events. |
| 0x004e1130 | CSoundManager__KillSamplesForThing | Iterates active events and stops currently-playing entries owned by the target thing. |
| 0x004e1190 | CSoundManager__KillSample | Iterates active events and stops entries matching owner + sample pair. |
| 0x004e12b0 | CSoundManager__KillAllSamples | Stops all active events and clears playing/reader state. |
| 0x004e1300 | CSoundManager__PauseAllSamples | Marks events paused and stops currently-assigned channels. |
| 0x004e1330 | CSoundManager__UnPauseAllSamples | Clears paused flag and reapplies per-event channel looping state. |
| 0x004e1360 | CSoundManager__UpdateSoundPosition | Source-parity event positional/pan update using camera transforms and track mode handling. |
| 0x004e18d0 | CSoundManager__SetPitch | Source-parity desired-pitch + fade-time setter on sound events. |
| 0x004e2360 | CSoundManager__GetDebugMenuText | Builds debug HUD text for nth active sound event (sample/channel/volume/tracking mode). |

### Semantic Wave35 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0050abb0 | CWorld__ShutdownAndClear_Thunk | Thin wrapper/thunk into the core shutdown-clear routine at `0x0050ada0`. |
| 0x0050ada0 | CWorld__ShutdownAndClear | Core world teardown/clear routine: releases LOD lists, clears sets, frees world globals, resets world-text/state slots. |
| 0x0050af70 | CWorld__FindThingByName | Iterates world object set and returns first entry matching requested name string. |
| 0x0050b010 | CWorld__DispatchHelper_004bc480 | Direct dispatch wrapper into `CWorld__Helper_004bc480`; kept helper-style naming pending stronger semantic contract evidence. |
| 0x0050b020 | CWorld__DispatchHelper_004bc3e0 | Direct dispatch wrapper into `CWorld__Helper_004bc3e0`; kept helper-style naming pending stronger semantic contract evidence. |
| 0x0050d680 | CWorld__ReleaseSubObject_AndMaybeFree | Calls cleanup helper then conditionally frees object when flag bit0 is set. |
| 0x0050d6a0 | CWorld__PushWorldTextSlot | Resolves text-id string and pushes entry into first free slot of 4-slot world-text arrays. |
| 0x0050d720 | CWorld__UpdateWorldTextSlotTiming | Updates timing/aux state for matching world-text slot entry. |
| 0x0050d7a0 | CWorld__ClearWorldTextSlot | Clears/deactivates a matching world-text slot entry by text id. |
| 0x0050d7d0 | CWorld__IsMultiplayerMode | Returns true when world mode/state field `+0x27c` is `1` or `2`. |
| 0x0050d7f0 | CWorld__ClearLinkedObjectPairSet | Releases object-pair nodes and clears linked pair-set container. |

### Semantic Wave36 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x004f35d0 | CThing__InitRenderThing | Source parity with `CThing::InitRenderThing`: obtains class-id render descriptor and instantiates render-thing chain into `this+0x30`. |
| 0x004f36d0 | CThing__Render | Source parity with `CThing::Render(DWORD flags)`: invisibility/objective-flag gating, render dispatch, optional debug cuboid path. |
| 0x004f3710 | CThing__RenderImposter | Source parity with `CThing::RenderImposter()`: imposter render dispatch when render thing exists and `TF_DONT_RENDER` is clear. |
| 0x004f37c0 | CThing__DrawDebugCuboid | Source parity with `CThing::DrawDebugCuboid()`: debug matrix setup and outline cuboid/sphere helper draws. |
| 0x004f3970 | CThing__SetObjective | Source parity with `CThing::SetObjective(BOOL)`: objective noticeboard add/remove + `TF_MARKED_OBJECTIVE` bit toggle. |
| 0x004f3de0 | CThing__IsOverWater | Source parity with `CThing::IsOverWater()`: compares water level and ground collision height at current position. |
| 0x004f4430 | CComplexThing__StartDieProcess | Source parity with `CComplexThing::StartDieProcess()`: base start-die path plus mission-script `StartedDying()` callback. |
| 0x004f4480 | CComplexThing__Hit | Source parity with `CComplexThing::Hit(CThing*, CCollisionReport*)`: mission-script `Hit()` callback when other thing is a complex thing type. |

### Semantic Wave37 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00403ba0 | CThing__Hit_TriggerDieOnDamageMaskA | Collision-hit path: if not already dying and death gate is enabled, triggers die/start path when incoming damage mask contains `0x10` or `0x2100000`, then forwards to shared hit helper. |
| 0x00403bf0 | CThing__Hit_TriggerDieOnDamageMaskB | Collision-hit sibling path: same die-gate logic but keyed to incoming damage mask bit `0x100000`, then forwards to shared hit helper. |
| 0x00417540 | CThing__RenderAndUpdateStaticShadow | Render-stage wrapper: runs `CThing__Render`, updates static-shadow visibility, and executes the additional frame-gated render callback while the countdown is active. |
| 0x004176c0 | CThing__InitRenderThingFromInitMeshName | Render-thing init path driven by init data: builds `%s.msh` name strings, creates the render object, and binds it into `this+0x30`. |

### Semantic Wave38 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x004f3a50 | CCSPersistentThing__scalar_deleting_dtor | Strong scalar-deleting-dtor pattern: calls dtor body (`0x004f3a70`), conditionally frees on `(flags & 1)`, then returns `this`. |
| 0x004f3a70 | CCSPersistentThing__dtor | Dtor body paired with `0x004f3a50`: performs `CMonitor__Shutdown(this+0x24)` and invokes `CCollisionSeekingRound__Destructor()`. |

### Semantic Wave39 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0044e2c0 | CMonitor__CheckSVFAnimationAndAdvanceState | SVF animation gate helper: resolves animation index for `PTR_DAT_00628e9c` (string target `SVF`) and triggers state-advance vfunc when current animation index matches. |
| 0x0047d3b0 | CMonitor__TryQueuePrefireAnimation | Prefire queue helper: validates `prefire` animation availability and queues it through animation-dispatch vfunc `+0xf0` under runtime state gating. |
| 0x0047d420 | CUnitAI__QueueFiringOrPostfireAnimation | Firing-phase queue helper: selects `firing` versus `postfire` token from runtime flag and queues the matching animation through animation-dispatch vfunc `+0xf0`. |
| 0x004ef120 | CMonitor__SpawnParticleEffectFromIndexedListInHeightBand | Indexed effect emitter: walks global list `DAT_008553f8`, samples candidate position, and spawns particle effect when Z is within configured height band. |

### Semantic Wave40 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00510a90 | CWorldPhysicsManager__ClearAndFreeAllDefinitionLists | Global WorldPhysicsManager teardown: drains all nine definition lists, frees each node through type-specific helpers/vfunc destruction, clears set heads, then frees list containers and nulls globals. |
| 0x00510eb0 | CWorldPhysicsManager__FreeRoundStatement | Round-statement entry free helper used while draining `DAT_008553f0` (`CRoundStatement__Create` list). |
| 0x00510f10 | CWorldPhysicsManager__FreeWeaponModeStatement | Weapon-mode statement free helper used while draining `DAT_008553ec` (`CWeaponModeStatement__Create` list). |
| 0x00511040 | CWorldPhysicsManager__FreeWeaponStatement | Weapon-statement entry free helper used while draining `DAT_008553e8` (`CWeaponStatement` list). |
| 0x005110f0 | CWorldPhysicsManager__FreeThingOrComponentDefinitionEntry | Shared free helper for Thing/Component definition entries (used by `DAT_008553fc` and `DAT_00855400` teardown paths). |
| 0x005115b0 | CWorldPhysicsManager__MapGunOrSpawnerTagToIndex | String-to-index mapper: `GunA..GunI` -> `1..9`, `SpawnerA..SpawnerE` -> `10..14` (validated from binary string table at `0x00633b24..0x00633c64`). |

### Semantic Wave41 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00511070 | CWorldPhysicsManager__FreeTagDefinitionEntry | Per-entry cleanup helper for DAT_008553f8 tag-definition nodes; frees owned pointers (`+0x18..+0x30`) and zeroes fields. |
| 0x005113a0 | CWorldPhysicsManager__ClearEntryWorkSets_40_50 | Clears two embedded working sets at offsets `+0x40` and `+0x50` for WorldPhysicsManager definition nodes. |
| 0x00511720 | CWorldPhysicsManager__ResolveTagListNameToIndex_E8 | Searches DAT_008553f8 by entry name (`entry+0x30`) and caches resolved index into `this+0xE8` (`-1` on miss). |
| 0x005117c0 | CWorldPhysicsManager__ResolveTagListNameToIndex_EC | Searches DAT_008553f8 by entry name (`entry+0x30`) and caches resolved index into `this+0xEC` (`-1` on miss). |
| 0x00511860 | CWorldPhysicsManager__ResolveTagListNameToIndex_F0 | Searches DAT_008553f8 by entry name (`entry+0x30`) and caches resolved index into `this+0xF0` (`-1` on miss). |

### Semantic Wave42 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0050ef30 | CCarrier__Destructor | Slot-1 destructor body for `CCarrier` (xref owner `CCarrier__VFunc_01_0050ee50`); clears owned sets and dispatches into base `CUnit` dtor path. |
| 0x0050f030 | CBigAirUnit__Destructor | Slot-1 destructor body for `CBigAirUnit` (xref owner `CBigAirUnit__VFunc_01_0050f010`); same cleanup skeleton as carrier branch with base-unit teardown. |
| 0x0050f630 | CRelaxedSquad__Destructor | Slot-1 destructor body for `CRelaxedSquad` (xref owner `CRelaxedSquad__VFunc_01_0050f610`); clears set at `+0xA4` then executes base-complex teardown. |
| 0x0050f8d0 | CMissile__Destructor | Slot-1 destructor body for `CMissile` (xref owner `CMissile__VFunc_01_0050f8b0`); removes two tracked set links (`+0xE8/+0xEC`), drops particle list membership, then runs base actor teardown. |
| 0x0050fd90 | CComponent__Destructor | Slot-1 destructor body for `CComponent` (xref owner `CComponent__VFunc_01_0050fd70`); removes set link at `+0x26C`, unregisters particle-list membership, then runs unit teardown. |
| 0x0050fe10 | CGillMHead__Destructor_VFunc01 | Slot-1 destructor body for Gill head branch (xref owner `CGillMHead__VFunc_01_0050fd30`); same set/particle/unit-teardown skeleton as component/tentacle siblings. |
| 0x0050fe90 | CTentacle__Destructor | Slot-1 destructor body for `CTentacle` (xref owner `CTentacle__VFunc_01_0050fd50`); same set/particle/unit-teardown skeleton as nearby sibling destructors. |
| 0x0050fff0 | CExplosion__Destructor | Slot-1 destructor body for `CExplosion` (xref owner `CExplosion__VFunc_01_0050ffd0`); removes nested set link at `+0x90` then dispatches base complex-thing teardown. |
| 0x00510250 | CHazard__Destructor | Slot-1 destructor body for `CHazard` (xref owner `CHazard__VFunc_01_00510230`); drops particle-list membership then dispatches base complex-thing teardown. |
| 0x00510520 | CWorldPhysicsManager__ResolveLoadedDefinitionReferences | Post-load reference fixup pass called from `CGame__LoadResources`: iterates definition lists and resolves loaded names/ids into runtime pointers/indices. |
| 0x00510740 | CWorldPhysicsManager__FreeNestedThingSets_6C | Shutdown helper called from `CGame__ShutdownRestartLoop`; drains nested set at `entry+0x6C` on thing/component definition lists and frees each child object. |
| 0x00510800 | CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData | Full reload path: clear/init lists, load `data/default_physics.dat`, then rebuild/load BattleEngine data from `data/battle_engine_configuration`. |
| 0x00510e60 | CWorldPhysicsManager__FreeEntryOwnedPtrs_00_0C_20 | Compact free helper used during list teardown (`0x00510a90`): frees/zeroes three owned pointers at offsets `+0x00`, `+0x0C`, and `+0x20`. |
| 0x00511440 | CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName | Spawner gate called by `CSpawnerThng__ProcessSpawnWave`: name-lookup into `DAT_008553fc` then type-allowlist check on enum at `entry+0xE0`. |

### Semantic Wave43 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0047a8b0 | CGillMHead__TryTransitionIdleToOpen | Animation-state gate for Gill head: resolves `idle` state token and only transitions to `open` when current animation and unit-gate checks pass. |
| 0x0047a900 | CGillMHead__AdvanceOpenAttackCloseState | State-advance helper for `open/attack/close/idle` flow: compares current animation token and dispatches next token through animation-set helper under runtime gating checks. |
| 0x004d10b0 | CGillMHead__ResetAnimationStateAndPauseLatch | Pause/unpause reset helper (called by `CGame__UnPause`): clears runtime animation handles/timestamps and updates pause-latch field. |

### Semantic Wave44 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00404210 | CAtmospheric__Process | Main atmospheric instance update loop: snapshots previous pose, steers toward/away from selected target entry, updates orientation vectors, moves position, updates map-who entry, and schedules periodic event `3000`. |
| 0x00404790 | CAtmospheric__UpdateBlendState | Advances atmospheric blend scalar state with mode gating and wrap/clamp behavior, including branch that re-samples blend velocity from helper path when state allows. |
| 0x004048c0 | CAtmospheric__GetInterpolatedBlendValue | Frame-interpolated blend accessor returning previous/current scalar interpolation using global frame blend factor (`DAT_008a9e44`). |


### Semantic Wave45 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x004429a0 | CDestructableSegment__DispatchChildDestructionEvents | Child-destruction dispatch helper: immediate child vfunc dispatch in one state, delayed event-3000 scheduling with jitter in others. |
| 0x00442a80 | CDestructableSegment__SetSubtreeActiveFlagRecursive | Recursive subtree activation helper: sets segment active flag (`+0x1C`) on node and descendants. |
| 0x00442ac0 | CDestructableSegment__PropagateDamageToChildren | Child fanout helper: iterates child list and invokes damage-style vfunc (`+0x0C`) using parent/controller context. |

### Semantic Wave46 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00443fc0 | CDestructableSegmentsController__Ctor | Controller constructor-like init routine (called from `CHiveBoss__Init` after allocation). |
| 0x00444000 | CDestructableSegmentsController__Dtor | Controller teardown helper: frees owned segment-array pointer and dispatches nested object release. |
| 0x004443f0 | CDestructableSegmentsController__TriggerCascadeIfThresholdExceeded | Threshold gate that triggers subtree activation + child damage cascade once current subtree-health crosses configured bound. |
| 0x00444450 | CDestructableSegmentsController__SetSegmentField0CByName | Name/tag-based segment lookup and write to field `+0x0C`. |
| 0x004444b0 | CDestructableSegmentsController__SetSegmentFields0C10ByName | Name/tag-based segment lookup and write to fields `+0x0C/+0x10`, then cached-health refresh. |
| 0x00444520 | CDestructableSegmentsController__FindSegmentByName | Name/tag lookup helper returning tracked segment pointer (used by `CHiveBoss__Init`). |
| 0x00444580 | CDestructableSegmentsController__SetAllSegmentsField0C | Bulk setter over tracked segment array for field `+0x0C`. |
| 0x004445b0 | CDestructableSegmentsController__SetSegmentActiveFlagByName | Name/tag-based segment lookup and write to active flag (`+0x1C`), then cached-health refresh. |

### Semantic Wave47 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x004433f0 | CDestructableSegmentsController__AreCoreChildrenDestroyed | Core-child status gate used by cascade logic; returns false when unresolved child state remains. |
| 0x00444030 | CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold | Indexed damage-dispatch path with shared threshold/callback update logic. |
| 0x00444160 | CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold | Randomized deduplicated segment-damage burst with shared threshold update path. |
| 0x004442d0 | CDestructableSegmentsController__GetSegmentField14ByIndex | Indexed getter for segment field `+0x14`. |
| 0x00444300 | CDestructableSegmentsController__GetSegmentField18ByIndex | Indexed getter for segment field `+0x18`. |
| 0x00444330 | CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive | Returns current subtree-health sum when active segments exist, otherwise zero. |
| 0x00444370 | CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive | Returns root `GetTotalHealth` result when active segments exist, otherwise zero. |
| 0x004443b0 | CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive | Returns cached total-health field when active segments exist, otherwise zero. |

### Semantic Wave48 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00495030 | CMeshPart__PassesBuggyCoreStateForStrictOptimize | Mesh-part optimize gate for buggy CORE/x1 state path used by `CMeshPart__CanOptimizePart_Strict`. |
| 0x00495090 | CMeshPart__PassesBuggyCoreStateForMergeOptimize | Mesh-part merge gate for buggy CORE/x1 state path used by `CMeshPart__CanMergeInOptimizePass`. |
| 0x004956a0 | Mat34__Add | 3x4 matrix block add helper (`dst = lhs + rhs`) used across mech/mesh update paths. |
| 0x00495e00 | Mat34__Subtract | 3x4 matrix block subtract helper (`dst = lhs - rhs`) used across mech/mesh update paths. |
| 0x004e66d0 | CWaypoint__Process_NoOp | No-op process wrapper that tail-calls `CFrontEndPage__Process_NoOp`. |
| 0x004f7cd0 | StringScratch__CopyRotating4K | Copies string into rotating 4-slot 0x1000-byte global scratch ring and returns active slot pointer. |
| 0x004ffe00 | CWaypoint__RandomizeOffsetVectors | Initializes randomized signed waypoint offset vectors and mirrored pairs (`+0x48..+0x5c`). |
| 0x00501360 | CWaypoint__CleanupEndLevelVBufTextures | End-of-level cleanup/report pass for waypoint VBufTexture resources; frees inactive entries and emits debug trace. |
| 0x00505ab0 | CWaypointManager__ReleasePendingObjects | Drains global pending waypoint-manager object set and releases each object via virtual destructor dispatch. |

### Semantic Wave49 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x004144f0 | CCockpit__GetCurrentEntryFlag_544 | Returns current entry-dependent flag value from cockpit-owned table block (`+0x544`) after resolving current/fallback entry. |
| 0x00418120 | CCockpit__AdvanceOpenCloseAnimationState | Advances cockpit open/close/shut animation-state transitions based on current animation token and updates state fields (`+0x254/+0x264`). |
| 0x004a1c30 | CMemoryManager__ReleaseMutexCallback | Thin callback helper that releases heap mutex handles via `ReleaseMutex`. |
| 0x004a2a20 | CMemoryManager__MarkAllocatedBlocksDebug | Iterates managed heap blocks and marks allocated entries with debug flag bit (`| 2`) for diagnostics/reporting paths. |

### Semantic Wave50 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0050f130 | CGroundAttackAircraft__Destructor_VFunc01 | Owner-corrected slot-1 destructor body reached from `CGroundAttackAircraft__VFunc_01_0050ee10`; clears owned sets then dispatches base teardown. |
| 0x0050f1a0 | CInfantryUnit__Destructor_VFunc01 | Owner-corrected slot-1 destructor body reached from `CInfantryUnit__VFunc_01_0050ee30`; removes list/particle state then tears down base unit object. |
| 0x0050f1f0 | CDropship__Destructor_VFunc01 | Owner-corrected slot-1 destructor body reached from `CDropship__VFunc_01_0050ee70`; clears owned sets then dispatches base teardown. |
| 0x0050f260 | CPlane__Destructor_VFunc01 | Owner-corrected slot-1 destructor body reached from `CPlane__VFunc_01_0050eeb0`; clears owned sets then dispatches base teardown. |
| 0x0050f2d0 | CDiveBomber__Destructor_VFunc01 | Owner-corrected slot-1 destructor body reached from `CDiveBomber__VFunc_01_0050eed0`; clears owned sets then dispatches base teardown. |
| 0x0050f340 | CCarver__Destructor_VFunc01 | Owner-corrected slot-1 destructor body reached from `CCarver__VFunc_01_0050eef0`; clears owned sets then dispatches base teardown. |
| 0x0050f3b0 | CFenrir__Destructor_VFunc01 | Owner-corrected slot-1 destructor body reached from `CFenrir__VFunc_01_0050ef10`; clears owned sets then dispatches base teardown. |

### Semantic Wave51 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00440c00 | CDamage__FreeOwnedDamageObjects | Releases nested owned damage-object pointers and nulls them. |
| 0x00440c40 | CDamage__ResetDamageTables | Clears large damage lookup/work tables and restores default runtime flags. |
| 0x004c0940 | CPDSimpleSprite__SetUVFromTileIndex | Computes atlas UV rectangle from packed tile index and tile-grid selector. |
| 0x004c5280 | CPDSimpleSprite__CopyTransformMatrix | Copies sprite transform matrix/basis fields into caller-provided output block. |
| 0x004d30d0 | CInfluenceMap__AccumulateThingFlags | Increments influence counters from thing flag bits (`0x400`, `0x20000`, `0x40000`, `0x4000`, `0x800`). |
| 0x004d39d0 | CInfluenceMap__ResetRuntimeState | Clears runtime accumulators/cached fields and seeds scalar default at `+0x50`. |
| 0x004d3a00 | CInfluenceMap__FreeRuntimeBuffers | Frees influence-map runtime grids/cell buffers and auxiliary allocations. |
| 0x004ebd10 | CStaticShadows__ClearAllShadowEntries | Drains linked shadow-entry list and frees cached 64x64 shadow tiles. |
| 0x004ebe40 | CStaticShadows__UpdateLightVectorAndRebuild | Normalizes light vector from globals and rebuilds static shadow maps for eligible objects. |
| 0x004ec250 | CStaticShadows__DestroyShadowMapNode | Destroys one shadow-map node (including deleting-dtor path) and frees owned bitmap allocations. |

### Semantic Wave52 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00488330 | CIBuffer__CreateConfigured | Configurable index-buffer create path: writes caller-provided fields then dispatches dynamic/static create routine via vtable with HRESULT fatal-check gate. |
| 0x00488aa0 | CIBuffer__GetEntryHeightByOwnerSlot | Resolves owner slot index (`owner->vfunc+0x6c`) and returns per-entry height scalar from CIBuffer-owned entry table. |
| 0x0048a4e0 | CInfantryGuide__dtor | Destructor body reached from `CInfantryGuide__VFunc_01_0048a4c0`; unregisters reader-set node, frees owned pointers, then calls `CMonitor__Shutdown`. |
| 0x0048ace0 | CInfantryGuide__SelectNearestTargetReader | Clears current reader, scans nearby map-who entries, and selects nearest valid target using flag/team distance filters. |
| 0x004c0c70 | CPDSimpleSprite__EvalExpressionNode | Recursive expression evaluator for sprite channels; supports pow/exp/sin/cos/inv/log/rand ops plus clamp/wrap mode outputs. |

### Semantic Wave53 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00428500 | CUnitAI__RefreshCachedComponentTransform | Refreshes cached component transform state used by downstream activation/heading logic. |
| 0x004289b0 | CUnitAI__AdvanceActivationAnimationState | Advances activation animation state machine and returns updated state token. |
| 0x00428bc0 | CUnitAI__GetTargetHeadingWithOffset | Computes target heading with additional runtime offset bias. |
| 0x00429280 | CUnitAI__UpdateHeadingTowardTargetClamped | Updates heading toward target under clamped turn-rate constraints. |
| 0x0048ac80 | CInfantryGuide__SelectTargetAndScheduleRecheck | Selects a target entry and schedules the next selection recheck cadence. |

### Semantic Wave54 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x004a52b0 | CMesh__ClearAllUsageMarkers | Clears usage-marker flags across mesh-owned tracking tables. |
| 0x004a5430 | CMesh__FreeUnusedAndReportLeaks | Frees currently unused mesh resources and emits leak/report diagnostics. |
| 0x004aa900 | CMesh__CreatePolyBucketsForAllParts | Builds polygon-bucket structures for all mesh parts. |
| 0x004ab330 | CMesh__FindByRuntimeId | Finds mesh entry/object by runtime id key. |
| 0x004ac000 | CMeshCollisionVolume__InitDirectionLookupTable | Initializes collision-volume direction lookup table data. |

### Semantic Wave55 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x004aa410 | CMesh__FindTextureByNameSuffixHint | Resolves texture entry by name-suffix hint matching. |
| 0x004aa5a0 | CMesh__GetPartField40ByFlatIndex | Returns mesh-part field `+0x40` by flattened part index. |
| 0x004aa5e0 | CMesh__FindEntryByInclusiveRangeTable | Resolves entry pointer/index through inclusive range-table traversal. |
| 0x004aa7e0 | CMesh__FindEntryValueByTypeId | Resolves entry value by type id from mesh lookup tables. |

### Semantic Wave56 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x004ac140 | CMeshCollisionVolume__TestSweptSphereAgainstBounds | Swept-sphere vs bounds gate with early rejection and hit-state updates on success. |
| 0x004ac4a0 | CMeshCollisionVolume__TestSweptSphereAgainstMeshPart | Mesh-part candidate iteration and swept-sphere intersection test path. |
| 0x004acf30 | CMeshCollisionVolume__ResolveContactNormalAndPlane | Resolves contact normal/plane vector from candidate axes and fallback constraints. |

### Semantic Wave57 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x004acde0 | CMeshCollisionVolume__InitContactOutputRecord | Initializes contact-output structure fields from stack-fed values and sets active/result flag. |

### Semantic Wave58 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00573630 | RBTree__FindLowerBoundByUIntKey | Finds lower-bound node in uint-keyed RB-tree traversal (sentinel-aware). |
| 0x005736a0 | MemCopyU16Elements | Copies `param_2` 16-bit elements from source to destination. |
| 0x0057ca3a | CDXTexture__DecodeBmpFromMemory | Validates in-memory BMP header and dispatches decode path for BMP payload. |

### Semantic Wave59 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0057ca6a | CDXTexture__DecodeFromMemory_WithFallbackCodecs | Tries multiple decode codecs for in-memory texture payload, with cleanup/reset between failed attempts. |
| 0x005894a9 | CTexture__OpenIncludeSourceAndInitBuffer | Opens include source (file or provider callback), allocates working buffers, and initializes parse span fields. |
| 0x00589650 | CTexture__InitBufferFromMemorySpan | Sets memory-span fields and invokes span validation/setup helper before decode use. |
| 0x00591340 | CDXTexture__PumpDecoderStreamAndFinalize | Pumps decoder stream object, dispatches status callbacks, and finalizes state on decode completion. |
| 0x00598749 | CTexture__HasSameFormatClassId | Predicate helper for texture comparators; checks format/class-id equality. |

### Semantic Wave60 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0057d244 | CDXTexture__Downsample2x2Average32 | Software 2x2 box filter over 32-bit pixels using masked per-channel averaging for mip/downscale paths. |
| 0x005818b7 | CDXTexture__PrepareDxtScaleAndQuantizedUV | Detects DXT2/DXT3 block scale, stores reciprocal scale fields, and quantizes UV-related values to codec grid. |
| 0x00582a99 | CTexture__PackTexels_Dither_Bits332 | Dithered texel packer writing 8-bit 3-3-2 packed output from float channels. |
| 0x00582bbe | CTexture__PackTexels_Dither_Bits8 | Dithered texel packer writing 8-bit single-channel output from float channel input. |
| 0x00582c8a | CTexture__PackTexels_Dither_Bits565 | Dithered texel packer writing 16-bit 5-6-5 packed output from float channels. |
| 0x00582dd3 | CTexture__PackTexels_Dither_Bits444 | Dithered texel packer writing 16-bit 4-4-4 packed output from float channels. |
| 0x00582ef8 | CDXTexture__PackTexels_Dither_Bits2_10_10_10 | Dithered texel packer writing 32-bit 2-10-10-10 packed output from float channels. |
| 0x00583041 | CDXTexture__PackTexels_Dither_Bits8888 | Dithered texel packer writing 32-bit 8-8-8-8 packed output from float channels. |
| 0x0058318a | CDXTexture__PackTexels_Dither_Bits888 | Dithered texel packer writing 24-bit 8-8-8 packed output from float channels. |
| 0x005832af | CDXTexture__PackTexels_Dither_Bits1616 | Dithered texel packer writing 32-bit 16-16 packed output from float channels. |

### Semantic Wave61 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x005833a6 | CDXTexture__PackTexels_Dither_Bits2_10_10_10_Alt | Dithered texel packer emitting alternate 2-10-10-10 channel-order packed output. |
| 0x005834ef | CDXTexture__PackTexels_Dither_Bits16_16_16_16 | Dithered texel packer emitting 16-16-16-16 packed output (two dwords per texel). |
| 0x00583670 | CDXTexture__PackTexels_Dither_PaletteIndexA8 | Palette-distance quantizer writing palette index with 8-bit alpha companion byte. |
| 0x005837b7 | CDXTexture__PackTexels_Dither_PaletteIndex8 | Palette-distance quantizer writing 8-bit palette index output. |
| 0x00583a94 | CTexture__PackTexels_Dither_A4L4 | Dithered texel packer writing 4-bit alpha + 4-bit luminance output. |
| 0x00583ba4 | CTexture__PackTexels_Dither_L16 | Dithered texel packer writing 16-bit luminance output. |
| 0x00583c8e | CTexture__PackTexels_Dither_Bits8_8 | Dithered texel packer writing 8-8 packed dual-channel output. |
| 0x00583d89 | CTexture__PackTexels_Dither_Bits5_5_5 | Dithered texel packer writing 5-5-5 packed output. |
| 0x00583eb3 | CTexture__PackTexels_Dither_Bits8_8_8_Alt | Dithered texel packer writing alternate-order 8-8-8 packed output. |
| 0x00583fe5 | CTexture__PackTexels_Dither_Bits8_8_8_8_Alt | Dithered texel packer writing alternate-order 8-8-8-8 packed output. |
| 0x00584535 | CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup | Dithered 8-8 output using auxiliary lookup helper (`CTexture__Helper_00575d99`) per texel. |
| 0x0058463a | CTexture__PackTexels_Dither_L16_Alt | Alternate table-slot variant of dithered 16-bit luminance texel packer. |

### Semantic Wave62 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00584144 | CFastVB__PackTexels_NoDither_Bits16_16 | Non-dither packer writing two 16-bit channels per texel into packed 32-bit output. |
| 0x0058423f | CFastVB__PackTexels_NoDither_Bits2_10_10_10 | Non-dither packer writing 2-10-10-10 packed output from float texel channels. |
| 0x0058439e | CFastVB__PackTexels_NoDither_Bits16_16_16_16 | Non-dither packer writing 16-16-16-16 packed output (two dwords per texel). |
| 0x00584724 | CDXTexture__PackTexels_CallbackPerTexel_RepeatA | Counted per-texel callback-dispatch wrapper using indirect helper `CDXTexture__Helper_005759c3` (repeat path A). |
| 0x00584786 | CDXTexture__PackTexels_CallbackPerTexel_RepeatB | Counted per-texel callback-dispatch wrapper using indirect helper `CDXTexture__Helper_005759c3` (repeat path B). |
| 0x005847e9 | CDXTexture__PackTexels_CallbackPerTexel_Once | Single-invocation callback-dispatch wrapper using indirect helper `CDXTexture__Helper_005759c3`. |
| 0x00584831 | CDXTexture__PackTexels_CopyRaw32 | Raw copy path writing first 32 bits of each 16-byte source texel record. |
| 0x00584886 | CDXTexture__PackTexels_CopyRaw64 | Raw copy path writing first 64 bits of each 16-byte source texel record. |
| 0x005848e3 | CDXTexture__PackTexels_CopyRaw128 | Raw copy path writing full 128 bits of each source texel record. |
| 0x00584936 | CDXTexture__PackTexels_NoDither_A16L16 | Non-dither packer writing A16L16 packed output (alpha + luminance) from float input. |
| 0x00584a4c | CTexture__PackTexels_NoDither_Bits16_16_16 | Non-dither packer writing three 16-bit color channels per texel. |
| 0x00584b5f | CTexture__UnpackTexels_Bgr8ToFloat4 | Unpacks BGR8 texels to float4 (RGBA with alpha=1.0) before optional post-normalization helpers. |


### Semantic Wave63 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00584c04 | CTexture__UnpackTexels_Bgra8ToFloat4 | Unpacks BGRA8 texels to float4 RGBA channels using direct byte normalization. |
| 0x00584cc3 | CTexture__UnpackTexels_Bgr8ToFloat4_AlphaOne | Unpacks BGR8 texels to float4 RGB and forces alpha to 1.0. |
| 0x00584d78 | CFastVB__UnpackTexels_Bits565ToFloat4 | Unpacks 16-bit RGB565 packed texels to normalized float4 channels. |
| 0x00584e32 | CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne | Unpacks 5-5-5 packed texels to float4 with forced alpha lane. |
| 0x00584ee9 | CFastVB__UnpackTexels_Bits1555ToFloat4 | Unpacks 1-5-5-5 packed texels to float4 including alpha-bit expansion. |
| 0x00584fae | CFastVB__UnpackTexels_Bits4444ToFloat4 | Unpacks 4-4-4-4 packed texels to normalized float4 RGBA channels. |
| 0x00585072 | CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4 | Unpacks 2-10-10-10 packed texels into float4 channels with component scaling. |
| 0x00585161 | CFastVB__UnpackTexels_Bits8888ToFloat4 | Unpacks 8-8-8-8 packed texels to float4 RGBA channels. |
| 0x00585220 | CFastVB__UnpackTexels_Bits888ToFloat4_AlphaOne | Unpacks 8-8-8 packed texels to float4 with forced alpha=1.0. |
| 0x005852d5 | CFastVB__UnpackTexels_Bits16_16_ToFloat4_RG | Unpacks dual 16-bit channels into float4 RG lanes with default BA handling. |
| 0x00585380 | CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4_Alt | Alternate channel-order unpacker for 2-10-10-10 packed texels. |
| 0x0058546f | CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4 | Unpacks 16-16-16-16 packed texels to float4 in the same dispatch family. |


### Semantic Wave64 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00585576 | CDXTexture__UnpackTexels_Bits332ToFloat4 | Unpacks 8-bit 3-3-2 packed texels into float4 RGBA channels (alpha=1.0). |
| 0x0058562d | CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB | Unpacks alpha-only 8-bit texels with RGB zeroed and A from source. |
| 0x005856b8 | CDXTexture__UnpackTexels_Bits332A8ToFloat4 | Unpacks paired 3-3-2 + A8 texels into float4 RGBA channels. |
| 0x0058579b | CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne | Unpacks 4-4-4 packed texels into float4 RGB with alpha forced to 1.0. |
| 0x0058586b | CTexture__UnpackTexels_PaletteIndexA8ToFloat4 | Expands indexed texels through palette table and applies per-texel alpha8. |
| 0x005859d8 | CFastVB__UnpackTexels_L8ToFloat4 | Unpacks L8 texels to float4 with replicated RGB and alpha=1.0. |
| 0x00585a7b | CFastVB__UnpackTexels_L8A8ToFloat4 | Unpacks L8A8 texels to float4 with replicated RGB and explicit alpha. |
| 0x00585b35 | CFastVB__UnpackTexels_A4L4ToFloat4 | Unpacks A4L4 texels to float4 RGBA channels. |
| 0x00585c0b | CFastVB__UnpackTexels_L16ToFloat4 | Unpacks 16-bit luminance texels to float4 with replicated RGB and alpha=1.0. |
| 0x00585cb0 | CTexture__UnpackTexels_Signed8_8_ToFloat4_RG | Unpacks signed 8-8 texels into float4 RG lanes (Z/A initialized). |
| 0x00585da3 | CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4 | Unpacks signed 5-5 + alpha6 packed texels into float4 channels. |
| 0x00585e9f | CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG | Unpacks signed 8-8 + alpha8 texels into float4 RG lanes with scalar alpha. |


### Semantic Wave65 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00585fa3 | CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4 | Unpacks signed 8-8-8-8 packed texels into float4 channels with signed normalization. |
| 0x005860ba | CTexture__UnpackTexels_Signed16_16_ToFloat4_RG | Unpacks signed 16-16 texels into float4 RG lanes with Z/A initialized to 1.0. |
| 0x005861b4 | CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4 | Unpacks signed 2-10-10-10 packed texels into float4 channels with sign expansion. |
| 0x00586305 | CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4 | Unpacks signed 16-16-16-16 packed texels into float4 channels. |
| 0x00586438 | CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ | Unpacks signed XY normal components and reconstructs Z via sqrt clamp path. |
| 0x0058686f | CTexture__UnpackTexels_CopyRaw128 | Raw-copy unpack path that copies 128-bit texel records directly. |
| 0x005868d1 | CFastVB__UnpackTexels_L16A16_ToFloat4 | Unpacks L16/A16 texels into float4 with replicated luminance and scalar alpha. |
| 0x005869b0 | CTexture__UnpackTexels_Bits16_16_16_ToFloat4 | Unpacks 16-16-16 packed texels into float4 RGB with alpha forced to 1.0. |


### Semantic Wave66 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00585908 | CFastVB__InitTexelUnpackVTable_005e9f5c | Initializes texel-unpack profile object and binds vtable 0x005e9f5c. |
| 0x00585924 | CFastVB__InitTexelUnpackVTable_005e9f6c | Initializes texel-unpack profile object and binds vtable 0x005e9f6c. |
| 0x005859bc | CFastVB__InitTexelUnpackVTable_005e9f7c | Initializes texel-unpack profile object and binds vtable 0x005e9f7c. |
| 0x00585bd3 | CFastVB__TexelUnpackProfile_scalar_deleting_dtor | Scalar-deleting destructor for texel-unpack profile objects. |
| 0x00585bef | CFastVB__InitTexelUnpackVTable_005e9fac | Initializes texel-unpack profile object and binds vtable 0x005e9fac. |
| 0x00585c94 | CFastVB__InitTexelUnpackVTable_005e9fbc | Initializes texel-unpack profile object and binds vtable 0x005e9fbc. |
| 0x0058617c | CFastVB__InitTexelUnpackVTable_005ea034 | Initializes texel-unpack profile object and binds vtable 0x005ea034. |
| 0x005862e9 | CFastVB__InitTexelUnpackVTable_005ea068 | Initializes texel-unpack profile object and binds vtable 0x005ea068. |
| 0x00586609 | CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne | Callback wrapper for stride-2 records with post-fill defaults. |
| 0x0058669a | CFastVB__InitTexelUnpackVTable_005ea0c8 | Initializes texel-unpack profile object and binds vtable 0x005ea0c8. |
| 0x005866b6 | CFastVB__InitTexelUnpackVTable_005ea0d8 | Initializes texel-unpack profile object and binds vtable 0x005ea0d8. |
| 0x005866d2 | CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne | Callback wrapper for stride-4 records with Z/A one-fill. |
| 0x0058675f | CFastVB__InitTexelUnpackVTable_005ea0e8 | Initializes texel-unpack profile object and binds vtable 0x005ea0e8. |
| 0x0058677b | CDXTexture__UnpackTexels_CallbackSingleTexel | Single-texel callback wrapper for helper-dispatched unpack. |
| 0x00586994 | CFastVB__InitTexelUnpackVTable_005ea118 | Initializes texel-unpack profile object and binds vtable 0x005ea118. |
| 0x00586ec7 | CFastVB__InitTexelUnpackVTable_005ea198 | Initializes texel-unpack profile object and binds vtable 0x005ea198. |


### Semantic Wave67 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00586bb7 | CFastVB__FlushPendingConvertedRows16 | Flushes pending converted float rows to 16-bit destination pairs and clears dirty marker. |
| 0x0058735a | CFastVB__StoreDecodedBlockToScratch | Stores decoded texel block into internal scratch buffer after bounds/block checks. |
| 0x005873f8 | CFastVB__LoadDecodedBlockFromScratch | Loads decoded texel block from internal scratch buffer to output span. |
| 0x005876ab | CTexture__WriteTexelBlockWithQuadCache | Writes texels through 4-column quad cache and flushes completed tile rows. |
| 0x00587af0 | CTexture__ReadTexelBlockWithQuadCache | Reads texels through quad cache with optional compare-and-zero postfilter. |
| 0x00587daf | CFastVB__TexelPackProfile_scalar_deleting_dtor | Scalar-deleting destructor for texel pack profile object. |
| 0x00587dee | CFastVB__InitTexelUnpackVTable_005ea264 | Initializes texel-unpack profile object and binds vtable 0x005ea264. |
| 0x00587e06 | CFastVB__InitTexelUnpackVTable_005ea274 | Initializes texel-unpack profile object and binds vtable 0x005ea274. |
| 0x00587e66 | CFastVB__TexelCodecProfile_scalar_deleting_dtor | Scalar-deleting destructor for texel codec profile objects. |
| 0x00587e82 | CFastVB__CreateTexelUnpackProfileByFormat | Factory selecting/allocating texel unpack profiles by format id and invoking setup callback. |


### Semantic Wave68 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00580120 | CFastVB__RunDualProfileConversionStage | Runs dual-profile conversion stage with compatibility checks and staging allocations. |
| 0x0058070e | CFastVB__InitDualTexelConversionPipeline | Initializes paired unpack profiles and conversion pipeline for dual-source texture conversion. |
| 0x005809de | CFastVB__ShutdownActiveProfile | Releases active profile through vtable callbacks and clears profile pointer. |
| 0x00580eef | CFastVB__ShutdownActiveProfile_Thunk | Alias thunk to active-profile shutdown routine. |
| 0x00581d49 | CDXTexture__ProbeTexelProfileSample | Swaps profile context temporarily and probes callback conversion on local sample state. |

### Semantic Wave69 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0058864a | CDXTexture__InitMappedFileContext | Initializes mapped-file context fields and prepares open/state bookkeeping for file-backed texture decode paths. |
| 0x0058865c | CDXTexture__OpenMappedFileReadOnly | Opens mapped file in read-only mode and binds map-view pointers for downstream decode helpers. |
| 0x00588cc6 | CDXTexture__ProjectPointToPlaneAndScale | Projects a 3D point onto a plane basis and returns scaled 2D coordinates used by texture-space math helpers. |

### Semantic Wave70 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x005890f1 | CDXTexture__CpuHasMmxFeature | CPUID feature-bit probe helper returning MMX support flag. |
| 0x00589116 | CDXTexture__IsMmxEnabledBySystemConfig | Applies `DisableMMX` registry override + CPU/system checks and caches MMX enable state. |
| 0x00589367 | CTexture__ReleaseIncludeNodeTreeRecursive | Recursively releases include-node interfaces and child nodes. |
| 0x005893d1 | CTexture__FreeChildIncludeNodeChainRecursive | Recursively frees child include-node chain through `+0x0c` linkage. |
| 0x005893e9 | CTexture__IncludeNodeChain_scalar_deleting_dtor | Scalar-deleting destructor wrapper for include-node chain objects. |
| 0x00589438 | CTexture__CleanupIncludeContextRecursive | Recursively tears down include-context tree and mapped-file resources. |
| 0x00589689 | CTexture__FreeIncludeFileChainRecursive | Recursively frees include-file chain through `+0x04` linkage. |
| 0x00589cab | CTexture__HandleDirective_Include | Preprocessor `#include` handler (nested-depth guard + source-open dispatch). |
| 0x00589e73 | CTexture__HandleDirective_Error | Preprocessor `#error` handler with line-continuation folding and diagnostic emission. |

### Semantic Wave71 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0058b3c7 | CTexture__ExecuteDirectiveParserAction | Executes parser reduction actions for preprocessor directives/operators and evaluation stack updates. |
| 0x0058b812 | CTexture__RunDirectiveParser | Table-driven YACC-style parser loop for directive expression/reduction flow. |
| 0x0058bd25 | CTexture__InitializePreprocessorStateFromMemorySpan | Builds parser/preprocessor state from in-memory source span and seeds core macro definitions. |
| 0x0058bd87 | CTexture__GetNextTokenWithPreprocessor | Integrates lexer token stream with preprocessor stack, include transitions, and directive parsing handoff. |

### Semantic Wave72 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0058c3fe | CTexture__SkipLineContinuationAndAdvance | Scanner helper that advances past escaped newline continuations and increments line counters. |
| 0x0058d2ad | CTexture__ReadNextLexToken | Core lexer/token reader classifying next token kind and advancing source/token metadata state. |

### Semantic Wave73 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0058c2b9 | CTexture__AppendDiagnosticTextLine | Appends formatted diagnostic/error text lines into the preprocessor/compiler message buffer. |
| 0x0058c457 | CTexture__ParseFloatingLiteral | Parses float literal text (including exponent form) and optionally emits numeric value. |
| 0x0058c5d3 | CTexture__ParseIdentifierToken | Parses identifier token text and stores/returns allocated token string. |
| 0x0058c652 | CTexture__ParseOperatorToken | Parses one/two/three-char operator and punctuator tokens (`==`, `<=`, `>>=`, `##`, etc.). |
| 0x0058d18b | CTexture__ParseCharLiteralToken | Parses single-quoted character literal tokens with closing-quote validation. |
| 0x0058d1ca | CTexture__ParseStringLiteralToken | Parses quoted/include-style string tokens with escape handling and newline/EOF diagnostics. |
| 0x0058d419 | CTexture__ParseVertexSemanticUsageToken | Parses vertex semantic usage tokens (`POSITION`, `NORMAL`, `TEXCOORD`, etc.) and usage index. |

### Semantic Wave74 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0056a1cd | CRT__ParseFloatTextToLongDouble | Stateful numeric parser converting float text to long-double-style intermediate representation. |
| 0x0056a69e | CRT__GetStringTypeACompat | CRT locale/codepage wrapper selecting ANSI/Wide string-type APIs. |
| 0x0056be17 | CRT__InitCTypeTablesFromCodePage | Initializes CRT ctype classification/case tables from active codepage metadata. |
| 0x0056ce69 | CRT__IsInDst_WrapperLocked | Lock-scoped wrapper around DST interval predicate logic. |
| 0x0056ce8a | CRT__IsInDst | Determines whether a time struct falls within computed DST boundaries. |
| 0x0056d036 | CRT__ComputeDstTransitionDayMillis | Computes DST transition day/time millisecond boundaries from rule fields. |
| 0x0056d8da | CRT__LongDoubleMultiply10Byte | Multiplies two 10-byte extended-precision floating values. |
| 0x0056dafa | CRT__LongDoubleScaleByPowerOf10 | Applies decimal exponent scaling to 10-byte extended floating value via lookup tables. |

### Semantic Wave75 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0056c70a | CRT__InitLocaleDefaults | Initializes locale defaults using user LCID and updates CRT locale state flags. |
| 0x0056c724 | CRT__ResolveLocaleCodePageToken | Resolves `ACP`/`OCP` or explicit codepage token strings into numeric codepage values. |
| 0x0056c78a | CRT__IsCodePageSupportedByLocaleMap | Checks codepage id against CRT locale support/exclusion map. |
| 0x0056c80b | CRT__IsWindowsNtPlatform | Returns true when running on NT-class Windows platform. |
| 0x0056c841 | CRT__GetLocaleInfoACompatFallback | Compatibility `GetLocaleInfoA` wrapper with CRT internal fallback table lookup. |
| 0x0056c981 | CRT__StrToLong | Entry wrapper to CRT signed integer parser (`strtol`-style base/whitespace/sign handling). |
| 0x0056d176 | CRT__IsFiniteDoubleWords | Bitwise finite check for IEEE-754 double word-pair representation. |
| 0x0056d18a | CRT__ClassifyDoubleWords | Classifies IEEE-754 double word-pair into CRT floating-point class codes. |
| 0x0056e0ec | CRT__UIntToAsciiBase | Converts unsigned integer to ASCII text in caller-provided radix with optional sign flag. |
| 0x0056e148 | CRT__UIntToAsciiBase_ReturnBuffer | Wrapper around `CRT__UIntToAsciiBase` returning destination buffer pointer. |

### Semantic Wave76 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0056614c | CRT__SelectHeapStrategy | Chooses CRT heap strategy from OS/version checks and `__MSVCRT_HEAP_SELECT` environment parsing. |
| 0x00566294 | CRT__InitializeHeapSubsystem | Creates process heap, selects strategy, and dispatches heap-subsystem initialization path. |
| 0x005662f1 | CRT__InitSmallBlockHeap | Allocates and initializes small-block heap descriptor table and related globals. |
| 0x00566339 | CRT__FindSmallBlockHeapEntryForPtr | Scans small-block heap region records and returns the matching entry for a pointer range. |
| 0x00569449 | CRT__ControlFp | Applies floating-point control-word mask/update (`(old & ~mask) | (new & mask)`) and writes back state. |
| 0x0056aff4 | CRT__AllocOsHandleSlot | Allocates/initializes a lowio slot entry and returns its handle index. |
| 0x0056b117 | CRT__SetOsHandle | Stores OS handle into a lowio slot and updates std handle aliases for slots 0/1/2. |
| 0x0056b193 | CRT__FreeOsHandle | Releases lowio slot handle state and clears std handle aliases for slots 0/1/2. |
| 0x0056cbb4 | CRT__EnsureTzsetInitialized | One-time lock-gated wrapper that ensures timezone globals are initialized. |
| 0x0056cbe2 | CRT__Tzset | Populates timezone/daylight globals from `TZ` env string or Win32 `GetTimeZoneInformation` fallback. |

### Semantic Wave77 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00582244 | CFastVB__PackTexels_Dither_Bits8_8_8_BGR | Dithered texel packer writing B,G,R byte output (3-byte format). |
| 0x00582355 | CFastVB__PackTexels_Dither_Bits8_8_8_8_ARGB | Dithered texel packer writing packed ARGB8888 output. |
| 0x0058249e | CFastVB__PackTexels_Dither_Bits8_8_8_RGB | Dithered texel packer writing R,G,B byte output (3-byte format). |
| 0x005825c3 | CFastVB__PackTexels_Dither_Bits5_6_5 | Dithered texel packer writing RGB565 output. |
| 0x005826e8 | CFastVB__PackTexels_Dither_Bits5_5_5 | Dithered texel packer writing RGB555 output. |
| 0x0058280d | CFastVB__PackTexels_Dither_A1R5G5B5 | Dithered texel packer writing A1R5G5B5 output. |
| 0x00582950 | CFastVB__PackTexels_Dither_A4R4G4B4 | Dithered texel packer writing A4R4G4B4 output. |
| 0x00583891 | CFastVB__PackTexels_Dither_L8 | Dithered texel packer writing 8-bit luminance output. |
| 0x00583979 | CFastVB__PackTexels_Dither_A8L8 | Dithered texel packer writing 16-bit A8L8 output. |

### Semantic Wave78 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0056f260 | CFastVB__ReleaseBufferAndResetTriplet_0056f260 | Releases owned buffer pointer at `+0x04` then clears `+0x04/+0x08/+0x0c` fields. |
| 0x0056f520 | CFastVB__ReleaseBufferAndResetTriplet_0056f520 | Releases owned buffer pointer at `+0x04` then clears `+0x04/+0x08/+0x0c` fields. |
| 0x00573310 | CFastVB__CountDwordsFromPointerSpan | Returns dword count from pointer span (`(end - begin) >> 2`) with null-span guard. |
| 0x005759c9 | CFastVB__ConvertFloat32ArrayToFloat16 | Converts float32 array entries into 16-bit half-float representation. |
| 0x00575dc9 | CFastVB__HermiteInterpolateVec3 | Evaluates cubic Hermite basis and blends four vec3 inputs at parameter `t`. |

### Semantic Wave79 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x005759b6 | CFastVB__DispatchIndirect_00657014 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657014`. |
| 0x00575a58 | CFastVB__DispatchIndirect_00657018 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657018`. |
| 0x00575cae | CFastVB__DispatchIndirect_00656ff0_ReturnInt | Guarded indirect-dispatch thunk forwarding args to `DAT_00656ff0` and returning int result. |
| 0x0057609c | CFastVB__DispatchIndirect_00657028 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657028`. |
| 0x00576154 | CFastVB__DispatchIndirect_00656f58 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f58`. |
| 0x00576698 | CFastVB__DispatchIndirect_00656f38 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f38`. |
| 0x0057674a | CFastVB__DispatchIndirect_00657034 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657034`. |

### Semantic Wave80 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00574296 | CFastVB__ComputeFormatMatchPenalty | Compares candidate format fields and computes weighted mismatch penalty; returns `-1` when compatibility gate fails. |
| 0x0057437a | CFastVB__SelectBestFormatHandler | Iterates format-handler table, probes callback compatibility, scores candidates via `CFastVB__ComputeFormatMatchPenalty`, and returns selected handler id. |

### Semantic Wave81 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x005768f1 | CFastVB__DispatchIndirect_00656f3c | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f3c`. |
| 0x00576b3a | CFastVB__DispatchIndirect_00656fc4 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fc4`. |
| 0x00576dfd | CFastVB__DispatchIndirect_00656f78 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f78`. |
| 0x005771af | CFastVB__DispatchIndirect_00656fb4 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fb4` with four forwarded args. |
| 0x005775b0 | CFastVB__DispatchIndirect_00656fc8 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fc8`. |
| 0x005776d3 | CFastVB__DispatchIndirect_00656fcc | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fcc`. |
| 0x005776e4 | CFastVB__DispatchIndirect_00656fd4_ReturnInt | Guarded indirect-dispatch thunk forwarding args to `DAT_00656fd4` and returning int result. |
| 0x0057798e | CFastVB__DispatchIndirect_00656fa4 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fa4` with three forwarded args. |
| 0x00577a0a | CFastVB__DispatchIndirect_00656f94 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f94` with four forwarded args. |
| 0x005784a9 | CFastVB__DispatchIndirect_00657044 | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657044`. |
| 0x00579184 | CFastVB__NormalizeQuaternionCopy | Normalizes quaternion source (or zeroes near-zero input) and copies the result into destination. |

### Wave56 Prep Create-Function Probe (Headless 2026-02-26)

| Address | Result | Notes |
|---------|--------|-------|
| 0x004ac6b0 | historical create failure (closed) | Initial probe returned `createFunction returned null after disassemble`; keep as archived note only (coverage closure is tracked in `functions/FUNCTION_COVERAGE_STATE.md`). |
| 0x004acde0 | create succeeded | Function object was created as `FUN_004acde0` and later promoted in wave57 to `CMeshCollisionVolume__InitContactOutputRecord`. |


### Headless Semantic Wave134 Promotions (2026-02-27)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0050a870 | CSPtrSetArray19__ClearAll | Clears 19 embedded `CSPtrSet` slots in a fixed contiguous object layout. |
| 0x0050a9c0 | CSPtrSetArray19__InitAndResetState | Initializes 19 embedded `CSPtrSet` slots and resets associated state fields/counters. |
| 0x00511ca0 | CWorldPhysicsManager__ResolveLoadedDefRefLinks_TypeA | Resolves loaded world-definition and battle-engine reference IDs into runtime pointers (layout variant A). |
| 0x00511d20 | CWorldPhysicsManager__ResolveLoadedDefRefLinks_TypeB | Resolves loaded world-definition and battle-engine reference IDs into runtime pointers (layout variant B). |
| 0x00512040 | CLTShell__InitUnhandledExceptionLogFile | Installs unhandled-exception filter and opens `OnslaughtException.txt` logging handle during shell startup. |


### Headless Semantic Wave135 Promotions (2026-02-27)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00512470 | PlatformInput__ClearTransientKeyStateTable | Clears a single 256-byte transient key-state table each frame (`+0x332e4`). |
| 0x00512630 | Platform__HandleDeviceLostAndRestore | Detects Direct3D device-loss sentinel and waits/restores through device callback path. |
| 0x00512fc0 | PlatformInput__ClearAllKeyStateTables | Clears three adjacent 256-byte key/input state tables in one pass. |
| 0x00523bc0 | Input__DispatchClickInRect | Rect-gated click dispatcher that consumes click state and triggers menu callback with payload id. |
| 0x00523d40 | Input__GetCursorStateInRectAndConsume | Rect test for alternate cursor/click latch (`DAT_0089bdf4`) with consume-on-hit behavior. |


### Headless Semantic Wave136 Promotions (2026-02-27)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x00523df0 | OggVorbisStream__InitDecoder | Initializes ogg/vorbis stream state, parses headers, and prepares synthesis/block contexts. |
| 0x00524180 | OggVorbisStream__ReadPcmSamples | Decodes ogg/vorbis packets to PCM samples into caller buffer with internal spill buffering. |
| 0x005234e0 | Input__HandleMouseWindowMessage | Windows message handler for mouse move/button/wheel state latches and normalized cursor coordinates. |
| 0x00528b60 | CBinkOpenThread__WorkerMain | Event-driven worker thread loop for queued Bink-open work; executes callback under mutex + signals completion. |
| 0x00527c90 | CReconnectInterface__ctor | Constructor initializes reconnect interface object, vtable, and retry-state fields. |
