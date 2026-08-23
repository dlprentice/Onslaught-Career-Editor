# CParticleSet__FindByNameAndTrackLinkSlot

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CParticleSet__FindByNameAndTrackLinkSlot` at `0x004cd7a0` in the particle/effects runtime cohort; lifecycle, update, render-support, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004cd7a0`

## Identity
- Body `[0x004cd7a0,0x004cd7e0]`, 65 bytes, 28 closure instructions. Raw pristine-body SHA-256 `32f9604d2c22e5ed5239b571d62343e3084252ac42ea3e679eace31af627f76c`; closure range SHA-256 `7e366eab57bb30aef6c646f2a706ba0f370453b3dd6da0c3ef3653c4f044d3ba`; packet range-plus-bytes SHA-256 `140099bcb8f025481ac1a367d240c7b432744cac71d50e09469f7f5b7f61b4a2`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CParticleSet__FindByNameAndTrackLinkSlot`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `090284202c6722935a805c51f1ddefb9b32ca72ff008e4b3bc41a4badac76318` and decompile SHA-256 `3a72fbae2bd96ab728a49cd019189b95671ee0311cf4d6a43ef54e702152769b` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `PREEXISTING_GEN19_C1_OR_C2` / packet confidence `CANDIDATE_CONTRACT`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CParticleSet__FindByNameAndTrackLinkSlot(void * this, char * set_name)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void * __thiscall CParticleSet__FindByNameAndTrackLinkSlot(void * this, char * set_name)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, and nullability remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The packet signature declares `void *`. The analyst comment quoted in Behavior summary is bounded evidence for its interpretation; exact ABI domain, sentinel behavior, and caller expectations remain not_determinable unless explicitly stated there.

## Globals read/written
- Decompile symbol references: `DAT_0082b3f8`, `DAT_0082b400`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `stricmp` `0x00568390` x1 site(s) (STATIC_DIRECT).
- Caller `CBattleEngine__Init` `0x00404dd0` x5 site(s) (instruction-flow).
- Caller `CBattleEngine__StartDieProcess` `0x0040bfd0` x1 site(s) (instruction-flow).
- Caller `CBuilding__VFunc_50_00417a40` `0x00417a40` x2 site(s) (instruction-flow).
- Caller `CDestroyableSegment__VFunc_10_SpawnRubbleEffects` `0x00442f60` x1 site(s) (instruction-flow).
- Caller `CDestroyableExtraUseMeshSegment__VFunc_10_SpawnEndRubbleEffects` `0x00443a20` x1 site(s) (instruction-flow).
- Caller `CDropship__Init` `0x00446d70` x1 site(s) (instruction-flow).
- Caller `CEscapePod__InitRocketMeshAndEngineEffect` `0x0044aab0` x1 site(s) (instruction-flow).
- Caller `CFEPDebriefing__Process` `0x00456930` x1 site(s) (instruction-flow).
- Caller `CFEPDevelopment__VFunc_2_00458230` `0x00458230` x1 site(s) (instruction-flow).
- Caller `CFEPMain__Process` `0x00462640` x1 site(s) (instruction-flow).
- Caller `CMech__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0` `0x0049fdb0` x1 site(s) (instruction-flow).
- Caller `CRocket__VFunc_22_CreateBigRocketEngineEffects` `0x004d8040` x1 site(s) (instruction-flow).
- Caller `CRTMesh__Init` `0x004dc370` x1 site(s) (instruction-flow).
- Caller `CSpawnPoint__SpawnBattleEngine` `0x004e47e0` x1 site(s) (instruction-flow).
- Caller `CSphereTrigger__OnTriggered` `0x004e5540` x1 site(s) (instruction-flow).
- Caller `CStart__SpawnBattleEngine` `0x004eaf20` x1 site(s) (instruction-flow).
- Caller `CTentacle__VFunc_22_004f0e40` `0x004f0e40` x1 site(s) (instruction-flow).
- Caller `CTree__UpdateFallingTree` `0x004f6b80` x1 site(s) (instruction-flow).
- Caller `CWorldPhysicsManager__ResolveLoadedDefinitionReferences` `0x00510520` x3 site(s) (instruction-flow).
- Caller `CWorldPhysicsManager__ResolveWeaponModeStatementRefs` `0x00511ca0` x2 site(s) (instruction-flow).
- Caller `CWorldPhysicsManager__ResolveTagDefinitionRefs` `0x00511d20` x4 site(s) (instruction-flow).
- Caller `CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs` `0x00511db0` x11 site(s) (instruction-flow).
- Caller `IScript__SpawnParticle` `0x00536b70` x1 site(s) (instruction-flow).
- Caller `CDXEngine__InitResources` `0x0053d6d0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: neither the exact-base canonical crosswalk nor any of the five landed source-wave receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope; no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave823 static read-back/name/signature correction: ECX is the particle-set/effect sorted-list head slot, observed callers pass &DAT_0082b400, and the only stack argument is set_name (RET 0x4). The helper stores the current link slot in DAT_0082b3f8, walks nodes through +0x38, compares set_name with the node name at +0x4 by stricmp, returns the matching node, and returns null early when the sorted comparison proves the name is absent. This replaces the older CWorldPhysicsManager-owned label and removes the unused_ctx phantom parameter. Static retail Ghidra evidence only; exact particle-set node layout, link-slot ownership, runtime particle/effect lookup behavior, source-body identity, BEA patching, and rebuild parity remain deferred.”
- The non-empty packet decompile is bound by SHA-256 `3a72fbae2bd96ab728a49cd019189b95671ee0311cf4d6a43ef54e702152769b`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 24 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device/file failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof. Any runtime addendum quoted from the packet comment remains bounded to that packet's named receipt.

## Evidence
- Writer authority: task `t_23f3c22a`, immutable cohort-10 manifest SHA-256 `6bb51e4b90110ea4847a777e8e0106d6fcee4fa99ce79eb462e70f032bae3f9b`, row 24; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `090284202c6722935a805c51f1ddefb9b32ca72ff008e4b3bc41a4badac76318`, and packet decompile SHA-256 `3a72fbae2bd96ab728a49cd019189b95671ee0311cf4d6a43ef54e702152769b`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004cd7a0:004cd7e0;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `OPEN_EXECUTED` and confidence `CANDIDATE_CONTRACT`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
