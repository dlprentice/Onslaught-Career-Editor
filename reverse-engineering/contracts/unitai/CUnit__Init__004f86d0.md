# CUnit__Init

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnit__Init` at `0x004f86d0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004f86d0`

## Identity
- Body `[0x004f86d0,0x004f91f1]`, 2850 bytes, 825 closure instructions. Raw pristine-body SHA-256 `dc3c02ae147e701c9840db77698dd0277501cab30f94f897179c06c762f7b7fd`; closure range SHA-256 `09eec45917c6edc2bd2e7ecaef0855b54b29e1b85b6cc9559d03d89959be6043`; packet range-plus-bytes SHA-256 `81071265e76ae2b88fb2a37988c31bd93dc55349d6223366f2007ccfbc1ef28b`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnit__Init` comes from the current closure/register row. Packet label matches canonical tracked name `CUnit__Init`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CUnit__Init(void * this, void * init)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CUnit__Init(void * this, void * init)
```
- Packet-declared parameter list: `void * this, void * init`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0062dd20`, `DAT_00633afc`, `DAT_00633b04`, `DAT_00633b24`, `DAT_00633b2c`, `DAT_00633b34`, `DAT_00633b3c`, `DAT_00633b44`, `DAT_00633b4c`, `DAT_00633b54`, `DAT_00633b5c`, `DAT_00633b64`, `DAT_00662b2c`, `DAT_008550b0`, `DAT_008550c0`, `DAT_008550d0`, `DAT_008551c0`, `DAT_00855228`, `DAT_00855400`, `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_Unit_cpp_00633b6c`, `s_X1_Barrel_00633b0c`, `s_X1_Turret_00633b18`, `s_barrel_0062dd18`, `s_nexus_00633af4`, `s_weakpoint_00633ae8`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×1 site(s) (STATIC_DIRECT).
- Callee `CActor__Init` `0x004011e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__SetReaderAndComputeRelativeYaw` `0x00428b50` ×1 site(s) (STATIC_DIRECT).
- Callee `CDestructableSegmentsController__Init` `0x00444660` ×1 site(s) (STATIC_DIRECT).
- Callee `CEulerAngles__ctor_from_FMatrix` `0x0044adb0` ×2 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 site(s) (STATIC_DIRECT).
- Callee `CInitThing__ctor` `0x0048dcf0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMesh__FindPartField40ByNameAndOwner` `0x004aa820` ×1 site(s) (STATIC_DIRECT).
- Callee `ParticleEffectLink_T3_004cb040` `0x004cb040` ×3 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__AddToHead` `0x004e5a80` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__AddToTail` `0x004e5b20` ×7 site(s) (STATIC_DIRECT).
- Callee `CUnit__UpdateFireControlYawAndQueueEvent` `0x004fb280` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorldMeshList__MarkUsed` `0x0050dc20` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorldPhysicsManager__CreateWeaponByIndex` `0x0050f6d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorldPhysicsManager__CreateSpawner` `0x0050f970` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorldPhysicsManager__CreateCharacter` `0x0050fa40` ×1 site(s) (STATIC_DIRECT).
- Callee `PCRTID__CreateObject` `0x00516580` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` ×6 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Free` `0x00549220` ×2 site(s) (STATIC_DIRECT).
- Callee `CRT__EhVectorDestructorIterator_WithUnwind` `0x0055db0a` ×1 site(s) (STATIC_DIRECT).
- Callee `eh_vector_constructor_iterator` `0x0055dc20` ×1 site(s) (STATIC_DIRECT).
- Callee `_strncmp` `0x0055e560` ×1 site(s) (STATIC_DIRECT).
- Callee `stricmp` `0x00568390` ×2 site(s) (STATIC_DIRECT).
- Callee `CRT__StrNICmpWithLocaleLock` `0x0056e170` ×2 site(s) (STATIC_DIRECT).
- Caller `CAirUnit__Init` `0x00402ad0` ×1 site(s) (instruction-flow).
- Caller `CBattleEngine__Init` `0x00404dd0` ×1 site(s) (instruction-flow).
- Caller `CBuilding__VFunc_9_00417190` `0x00417190` ×1 site(s) (instruction-flow).
- Caller `CComponent__VFunc_09_00427b80` `0x00427b80` ×1 site(s) (instruction-flow).
- Caller `CGroundUnit__Init` `0x0047c730` ×1 site(s) (instruction-flow).
- Caller `CHiveBoss__Init` `0x0047fe30` ×1 site(s) (instruction-flow).
- Caller `CPod__FlagArg70AndSeedMotion250_004d35d0` `0x004d35d0` ×1 site(s) (instruction-flow).
- Caller `CRadar__FlagArg70AndSeedMotion280_004d6360` `0x004d6360` ×1 site(s) (instruction-flow).
- Caller `CUnit__VFunc08_InitAndAddToWorld` `0x004dfa40` ×1 site(s) (instruction-flow).
- Caller `CSubmarine__Init` `0x004eec80` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “=== 2026-07-28 runtime observation === MEASURED, TTD trace G:/bea-ttd/play-level100/play-level100.run (32 GiB, -skipfmv -level 100), written up in local-lab/TTD-LEVEL100-FINDINGS-2026-07-28.md: 34 executions in Level 100 - one MORE than the 33 objects the definition factory built. INFERRED (strong, not measured here): the 34th is the player. CBattleEngine derives from CUnit but is not built by CWorldPhysicsManager__CreateThingByType, so 33 factory units plus 1 player = 34. Confirming it needs the per-call this pointer, which this pass did not read. GRADE: RUNTIME-OBSERVED for the count 34; INFERRED for the identity of the extra one.”
- The displayed decompile is non-empty and SHA-256 `f9ea35f7c5454bcb8e09ba13deeb5fe5bd7524013c6a742359f2c130c3562de7`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 10 caller record(s), 24 callee record(s), and 6 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `all level-openings`; question `corpus-open-core`; value: invariant across all 66 openings; 152,343 cumulative covered bytes; evidence `name=CUnit__Init`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 10; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004f86d0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `f9ea35f7c5454bcb8e09ba13deeb5fe5bd7524013c6a742359f2c130c3562de7`.
- Digest derivation: closure SHA-256 hashes canonical range text `004f86d0:004f91f1;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062dd18` length 7 SHA-256 `e8bbe6423a622988680db31fa80a400b1e6eeca803831711afa17cf332c24918` value `barrel`.
- Packet string ref `0x00633ae8` length 10 SHA-256 `aa44c587a7af347111f7802a8998287274f4f2ac1d042c14934c3be4af5a1eee` value `weakpoint`.
- Packet string ref `0x00633af4` length 6 SHA-256 `f5cfcb570b7edac2ed16e1a025d50155d6148de7397f4068790cdfc142300070` value `nexus`.
- Packet string ref `0x00633b0c` length 10 SHA-256 `2d5e6f918e3551bba8decf072bbafc26a53487261cf0e97f4c4b8578043dfc24` value `X1 Barrel`.
- Packet string ref `0x00633b18` length 10 SHA-256 `79db273aa2c7d320d9ba18c028a63c86e7fb682c630b240ae6e427a7744ac374` value `X1 Turret`.
- Packet string ref `0x00633b6c` length 27 SHA-256 `322972ddbfcd9f5c5e7e9c684df9cbcf950ff4a31bec83e6607513f33d816757` value `C:\\dev\\ONSLAUGHT2\\Unit.cpp`.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
