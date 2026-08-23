# CWorld__LoadWorld

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CWorld__LoadWorld` at `0x0050b9c0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0050b9c0`

## Identity
- Body `[0x0050b9c0,0x0050d4b1]`, 6898 bytes, 2023 closure instructions. Raw pristine-body SHA-256 `8deeac85f88c5a505f4b65dc2ff05b2c485aea78cd93523558949c0de3f96e5d`; closure range SHA-256 `13d017c00140f51a52ae2c58de81bc208f47f3cad2ef84455246219f75118f20`; packet range-plus-bytes SHA-256 `7d462e10b1c883f2aa23dfafaec38f83f609f0302c931f63fa3fde4e10bf0ef7`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CWorld__LoadWorld` comes from the current closure/register row. Packet label matches canonical tracked name `CWorld__LoadWorld`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `bool __thiscall CWorld__LoadWorld(void * this, void * mem_buffer, int is_base_world, int initialize_world_state)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
bool __thiscall CWorld__LoadWorld(void * this, void * mem_buffer, int is_base_world, int initialize_world_state)
```
- Packet-declared parameter list: `void * this, void * mem_buffer, int is_base_world, int initialize_world_state`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `bool`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_006245cc`, `DAT_00633a6c`, `DAT_00633a74`, `DAT_00663498`, `DAT_0067a078`, `DAT_0067a07c`, `DAT_0067a748`, `DAT_006fadc8`, `DAT_00855090`, `DAT_00855290`, `DAT_00855294`, `DAT_00855298`, `DAT_008553fc`, `DAT_00855404`, `DAT_00855408`, `DAT_0089c9a0`, `DAT_008a9abc`, `DAT_008a9ac8`, `DAT_008a9d9c`, `DAT_009c3df0`, `_DAT_008a9b84`, `_DAT_008a9b88`, `_DAT_008a9b90`, `_DAT_008a9b94`, `_DAT_008a9b9c`, `_DAT_008a9ba0`, `_DAT_008a9ba4`, `_DAT_008a9ba8`, `_DAT_008a9bb0`, `s_C__dev_ONSLAUGHT2_world_cpp_0063d2ac`, `s_DefaultTree0_0062d7a0`, `s_Loading_trees_0063d418`, `s_Loading_units_0063d450`, `s____Unable_to_find_thing_in_physi_0063d428`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__First` `0x00406d20` ×3 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__Next` `0x00406d30` ×1 site(s) (STATIC_DIRECT).
- Callee `DebugTrace` `0x0040c640` ×2 site(s) (STATIC_DIRECT).
- Callee `CCareer__DoesBaseThingExist` `0x0041bb20` ×1 site(s) (STATIC_DIRECT).
- Callee `CCareer__IsWorldLater` `0x0041bbb0` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__Status` `0x0042b500` ×2 site(s) (STATIC_DIRECT).
- Callee `CConsole__StatusDone` `0x0042b800` ×2 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoadingFraction` `0x0042cf70` ×3 site(s) (STATIC_DIRECT).
- Callee `CEngine__LoadAllNamedMeshes` `0x00449dc0` ×1 site(s) (STATIC_DIRECT).
- Callee `CInfluenceMapManager__Load` `0x0048b010` ×1 site(s) (STATIC_DIRECT).
- Callee `CInfluenceMapManager_T3_0048b660` `0x0048b660` ×1 site(s) (STATIC_DIRECT).
- Callee `CInfluenceMapManager_T3_0048b7d0` `0x0048b7d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CInfluenceMapManager_T3_0048b8e0` `0x0048b8e0` ×1 site(s) (STATIC_DIRECT).
- Callee `InitThing__CreateThingByType` `0x0048c650` ×7 site(s) (STATIC_DIRECT).
- Callee `CInitThing__ctor` `0x0048dcf0` ×3 site(s) (STATIC_DIRECT).
- Callee `CHeightField__TraceMapLoadRequestAndCheckLoadedFlags` `0x00490f50` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__ClearOccupancyBitsUsingHeightBands` `0x004bc8d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__ApplyStaticMaskToOccupancyBitplanes` `0x004bcbf0` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__RebuildOccupancyGridFromDynamicSet` `0x004bcd60` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__SkipLegacyOccupancyChunk` `0x004bdff0` ×3 site(s) (STATIC_DIRECT).
- Callee `CWorld__LoadOccupancyBitplaneChunk` `0x004be050` ×3 site(s) (STATIC_DIRECT).
- Callee `CWorld__SkipOccupancyChunkHeader` `0x004be170` ×1 site(s) (STATIC_DIRECT).
- Callee `OID__CreateObject` `0x004bf090` ×4 site(s) (STATIC_DIRECT).
- Callee `RandomSeedPair__Set` `0x004de8c0` ×1 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×4 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__Init` `0x004e5840` ×2 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__AddToTail` `0x004e5b20` ×2 site(s) (STATIC_DIRECT).
- Callee `CWaypointManager__LoadWaypoints` `0x00505ae0` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__LoadScriptEvents` `0x0050ac70` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__LoadWorldFile` `0x0050b520` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__LoadWorldHeader` `0x0050d4c0` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__InitLODLists` `0x0050d580` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorldMeshList__Add` `0x0050d9e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorld__SpawnInitialThings` `0x0050dcb0` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorldPhysicsManager__CreateThingByType` `0x0050df80` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorldPhysicsManager__CreateSquad` `0x0050f4b0` ×2 site(s) (STATIC_DIRECT).
- Callee `CWorldPhysicsManager__CreateFeature` `0x00510060` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorldPhysicsManager__CreateHazard` `0x00510150` ×1 site(s) (STATIC_DIRECT).
- Callee `CScriptObjectCode__CollectSpawnThings` `0x005392a0` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__ApplyLandscapeDamageStamp` `0x005475d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXMemBuffer__Read` `0x00548570` ×123 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` ×5 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` ×7 site(s) (STATIC_DIRECT).
- Callee `sprintf` `0x0055de9b` ×3 site(s) (STATIC_DIRECT).
- Callee `CRT__AllocaProbe` `0x0055def0` ×1 site(s) (STATIC_DIRECT).
- Callee `CRT__StrNICmpWithLocaleLock` `0x0056e170` ×2 site(s) (STATIC_DIRECT).
- Caller `CWorld__LoadWorldFile` `0x0050b520` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “=== 2026-07-28 runtime corroboration (name and signature unchanged) === MEASURED, TTD trace G:/bea-ttd/play-level100/play-level100.run (32 GiB, -skipfmv -level 100), written up in local-lab/TTD-LEVEL100-FINDINGS-2026-07-28.md: this function executed exactly 2 times in a Level 100 load, and its CWorldPhysicsManager__CreateThingByType call site 0x0050ca9d accounts for 30 of the 33 creations in the whole trace. The 30 fall into two disjoint bursts, which are the two worlds: calls 0-26, positions 16ACFF-16AE28 (22.652% - 22.657%): 19 CBuilding, 5 CSimpleBuilding, 4 CCannon turrets. The BASE world. calls 27-29, positions 1736BD-1737AE (23.190% - 23.193%): Warehouse; U-17 Highside Transporter (CDropship, script "Transporter"); Air Trainer (CPlane, script "Flyby"). The LEVEL world. INFERRED (strong): burst 1 is the base-world BSWD chunk, burst 2 the level RLWD chunk, matching the two executions. The four turrets are three distinct definitions - SAT Turret x1, Blaster Turret x2, Pulse Turret x1 - which was predicted from the world data before the trace was read. Do not implement retail's turrets as one type. GRADE: RUNTIME-OBSERVED, corroborating a name that was already static-backed. The chunk attribution is inferred, not measured.”
- The displayed decompile is non-empty and SHA-256 `9a1f5629cc5e2c5f383f3bc38237d1d7740192c1abde151285806b3c894460b6`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 47 callee record(s), and 5 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `all level-openings`; question `corpus-open-core`; value: invariant across all 66 openings; 244,305 cumulative covered bytes; evidence `name=CWorld__LoadWorld`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 25; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0050b9c0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `9a1f5629cc5e2c5f383f3bc38237d1d7740192c1abde151285806b3c894460b6`.
- Digest derivation: closure SHA-256 hashes canonical range text `0050b9c0:0050d4b1;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `OPEN_EXECUTED` and confidence `MEDIUM`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062d7a0` length 16 SHA-256 `00fa675a5d4259cc9d3c5bc22c3f6fa3ba1a78fc9da125a13d2d13fcd56dad2c` value “DefaultTree0”.
- Packet string ref `0x0063d2ac` length 28 SHA-256 `a612294c24bbe67a6527c1cf63d95a322da7b3232c2ddd95d9857006f4e8a5ca` value “C:\\dev\\ONSLAUGHT2\\world.cpp”.
- Packet string ref `0x0063d418` length 14 SHA-256 `829b65abc1b5ff070c9cf289fcd042a439bb96ef379b451337a9b572890525d6` value “Loading trees”.
- Packet string ref `0x0063d428` length 40 SHA-256 `be00c17a08cc9a80837b09e0cb75208450c4aada89d544e72a1ccf258f79aaca` value “** Unable to find thing in physics: %s\n”.
- Packet string ref `0x0063d450` length 14 SHA-256 `42f2e810b9c21fcab5784d671e8ce554c9c19f080dd93ac91bef0fd9ea9bbd09` value “Loading units”.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
