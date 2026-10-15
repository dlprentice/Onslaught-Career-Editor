# CParticleManager__CreateEffect

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticleManager__CreateEffect` at `0x004cb3d0` in the particle/effects runtime cohort; lifecycle, update, render-support, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cb3d0`

## Identity
- Body `[0x004cb3d0,0x004cb5b4]`, 485 bytes, 132 closure instructions. Raw pristine-body SHA-256 `eadfd3493f6774eba3132be76ff06075ca514210595a5eb8cd7d11932acdafb8`; closure range SHA-256 `e5ee99ebcc608bf6482968445a5bb1dedea1cf6296a0d9cadd3b6396b1772b5f`; packet range-plus-bytes SHA-256 `e19e9c4ebee40d71279dc14ea4172422cbc3152ea4ee075169f1ab90d37a45e1`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticleManager__CreateEffect`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `2ef9633e95c1442c288d8959724d9ab1d98185a79f430856b4ebcadbbf28d181` and decompile SHA-256 `8ca5c0bbbe8b8b2958e1c3cd92d4fdcf9fcd769cc5fca1e838afa7cae57ae012` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet field records `__stdcall` for `void __stdcall CParticleManager__CreateEffect(void * manager, void * out_handle_slot, float spawn_x, float spawn_y, float spawn_z, float spawn_w, int looping_flag, int force_allocate)`. The packet analyst comment explicitly refutes the packet field's `void __stdcall ... (manager, ...)` form: ECX carries the manager receiver and `RET 0x20` proves eight stack dwords after `this`. The bounded reconciled form keeps the comment's untyped particle-set/handle slots and invents no stronger object types.

## Prototype and parameter semantics
```c
void __thiscall CParticleManager__CreateEffect(void * this, void * particle_set, void * out_handle_slot, float spawn_x, float spawn_y, float spawn_z, float spawn_w, int looping_flag, int force_allocate)
```
- Reconciled bounded ABI from the packet's own analyst comment: `void __thiscall CParticleManager__CreateEffect(void * this, void * particle_set, void * out_handle_slot, float spawn_x, float spawn_y, float spawn_z, float spawn_w, int looping_flag, int force_allocate)`. The packet field's declared `void __stdcall CParticleManager__CreateEffect(void * manager, void * out_handle_slot, float spawn_x, float spawn_y, float spawn_z, float spawn_w, int looping_flag, int force_allocate)` remains preserved above as metadata, not asserted as true.

## Return value meaning
The reconciled bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0082b3a0`, `DAT_0082b3d0`, `DAT_0082b3d4`, `DAT_0082b3d8`, `DAT_0082b3dc`, `DAT_0082b3e4`, `DAT_0089ce58`, `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_ParticleManage_00630e60`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `vector_constructor_iterator_nothrow` `0x004011b0` x2 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__AllocateParticle` `0x004cb5c0` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` x1 site(s) (STATIC_DIRECT).
- Caller `CAirUnit__UpdateMotionAndTrailEffects` `0x00402fa0` x2 site(s) (instruction-flow).
- Caller `CAirUnit__ApplyDamageAndResolveSlot19Vector_004037a0` `0x004037a0` x1 site(s) (instruction-flow).
- Caller `CBattleEngine__StartDieProcess` `0x0040bfd0` x1 site(s) (instruction-flow).
- Caller `CMonitor__UpdateTrackedList_59C` `0x0040e940` x1 site(s) (instruction-flow).
- Caller `CMonitor__UpdateTrackedList_620` `0x0040ebf0` x2 site(s) (instruction-flow).
- Caller `CBattleEngine__GroundParticleEffect` `0x0040ef20` x1 site(s) (instruction-flow).
- Caller `CBuilding__VFunc_50_00417a40` `0x00417a40` x2 site(s) (instruction-flow).
- Caller `CDestroyableSegment__VFunc_10_SpawnRubbleEffects` `0x00442f60` x1 site(s) (instruction-flow).
- Caller `CDestroyableExtraUseMeshSegment__VFunc_10_SpawnEndRubbleEffects` `0x00443a20` x1 site(s) (instruction-flow).
- Caller `CDropship__ProcessDoorThrustersAndChildUnits` `0x00447120` x2 site(s) (instruction-flow).
- Caller `CDropship__TraceGroundAndSpawnThrusterDust` `0x00448170` x1 site(s) (instruction-flow).
- Caller `CEscapePod__InitRocketMeshAndEngineEffect` `0x0044aab0` x1 site(s) (instruction-flow).
- Caller `CExplosion__VFunc_9_0044b930` `0x0044b930` x2 site(s) (instruction-flow).
- Caller `CFEPDebriefing__Process` `0x00456930` x1 site(s) (instruction-flow).
- Caller `CFEPDevelopment__VFunc_2_00458230` `0x00458230` x1 site(s) (instruction-flow).
- Caller `CFEPMain__Process` `0x00462640` x1 site(s) (instruction-flow).
- Caller `CGroundUnit__UpdateLinkedEffectsByHeightClearance` `0x0047c970` x1 site(s) (instruction-flow).
- Caller `CHazard__VFunc_9_0047e530` `0x0047e530` x1 site(s) (instruction-flow).
- Caller `CInfantryUnit__VFunc50_HandleDeathPickupAndEffects` `0x00489b40` x1 site(s) (instruction-flow).
- Caller `CMech__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0` `0x0049fdb0` x1 site(s) (instruction-flow).
- Caller `CMeshRenderer__RenderMesh` `0x004b6350` x1 site(s) (instruction-flow).
- Caller `CMine__VFunc_66_004ba4d0` `0x004ba4d0` x1 site(s) (instruction-flow).
- Caller `CPDFoR__Update` `0x004c5410` x1 site(s) (instruction-flow).
- Caller `CPlane__VFunc_66_004d1cd0` `0x004d1cd0` x1 site(s) (instruction-flow).
- Caller `CRocket__VFunc_22_CreateBigRocketEngineEffects` `0x004d8040` x1 site(s) (instruction-flow).
- Caller `CRound__Init` `0x004d8410` x1 site(s) (instruction-flow).
- Caller `CRound__UpdateEffectTransformByMode_004d9f30` `0x004d9f30` x1 site(s) (instruction-flow).
- Caller `CRound__ArmProjectileAndSpawnTrailEffect` `0x004db630` x1 site(s) (instruction-flow).
- Caller `CSpawnPoint__SpawnBattleEngine` `0x004e47e0` x1 site(s) (instruction-flow).
- Caller `CSphereTrigger__OnTriggered` `0x004e5540` x1 site(s) (instruction-flow).
- Caller `CStart__SpawnBattleEngine` `0x004eaf20` x1 site(s) (instruction-flow).
- Caller `CMonitor__SpawnParticleEffectFromIndexedListInHeightBand` `0x004ef120` x1 site(s) (instruction-flow).
- Caller `CTentacle__VFunc_22_004f0e40` `0x004f0e40` x1 site(s) (instruction-flow).
- Caller `CTree__UpdateFallingTree` `0x004f6b80` x1 site(s) (instruction-flow).
- Caller `CUnit__ApplyDamage` `0x004f9a90` x1 site(s) (instruction-flow).
- Caller `CUnit__UpdateMotionAttachmentsAndEffects` `0x004fa8d0` x1 site(s) (instruction-flow).
- Caller `CUnit__UpdateDeployStateAndChargeEffects` `0x004fbcb0` x1 site(s) (instruction-flow).
- Caller `CUnit__SpawnComponentEffectsRecursive` `0x004fc220` x1 site(s) (instruction-flow).
- Caller `ProjectileBurst__SpawnFromCurrentPreset` `0x005069f0` x2 site(s) (instruction-flow).
- Caller `IScript__SpawnParticle` `0x00536b70` x1 site(s) (instruction-flow).
- Caller `CDXEngine__Render` `0x0053e2e0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: neither the exact-base canonical crosswalk nor any of the five landed source-wave receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope; no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “CParticleManager effect create (AllocateParticle when DAT_0089ce58==0; write spawn into particle+0x38..+0x44; optional 0xb8 handle link onto DAT_0082b3e4). ECX receiver (manager); terminator `RET 0x20` proves eight stack dwords after this. Declared `void __stdcall` with stack `manager` is false — AllocateParticle keeps manager in ECX; first stack slot is particle_set. Shape is `__thiscall (void * this, void * particle_set, void * out_handle_slot, float spawn_x, float spawn_y, float spawn_z, float spawn_w, int looping_flag, int force_allocate)` (do not invent typed handle/set formals beyond that plate). Static retail evidence only; exact handle ownership, runtime effect UX, and rebuild parity remain unproven. Generation 23 bounded runtime addendum: writer PC 0x004CB525 produced an exact receiver write at +0xE4 in each selected event-4000 invocation. Both lanes cross ledgered continuity barriers; this proves the bounded receiver-slot write only, not allocation, particle lifetime, external memory effects, or general CreateEffect behavior. Gen23 READY 4471fdfe1053; proof 974cbb86f885; refuter SURVIVED 222898ab3660. C2_BOUNDED_RUNTIME; PARTIAL_CONTRACT.”
- The non-empty packet decompile is bound by SHA-256 `8ca5c0bbbe8b8b2958e1c3cd92d4fdcf9fcd769cc5fca1e838afa7cae57ae012`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 41 caller record(s), 3 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device/file failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof. Any runtime addendum quoted from the packet comment remains bounded to that packet's named receipt.

## Evidence
- Writer authority: task `t_23f3c22a`, immutable cohort-10 manifest SHA-256 `6bb51e4b90110ea4847a777e8e0106d6fcee4fa99ce79eb462e70f032bae3f9b`, row 10; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `2ef9633e95c1442c288d8959724d9ab1d98185a79f430856b4ebcadbbf28d181`, and packet decompile SHA-256 `8ca5c0bbbe8b8b2958e1c3cd92d4fdcf9fcd769cc5fca1e838afa7cae57ae012`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cb3d0:004cb5b4;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00630e60` length 38 SHA-256 `c1807ca6bc166c0c0bb6801fe91470d2c70fb7abc1d73c6934b80f449aea18e0` value `C:\\dev\\ONSLAUGHT2\\ParticleManager.cpp`.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
