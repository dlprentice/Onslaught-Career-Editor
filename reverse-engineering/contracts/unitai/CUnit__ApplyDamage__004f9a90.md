# CUnit__ApplyDamage

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnit__ApplyDamage` at `0x004f9a90`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004f9a90`

## Identity
- Body `[0x004f9a90,0x004fa4a9]`, 2586 bytes, 771 closure instructions. Raw pristine-body SHA-256 `c00c805fc86ad1f52e6ab7d8fc739c456983914319ad99870d49c88b8733f859`; closure range SHA-256 `6d887e5b714b5c78474870ba56e04925a0b1652f2464f9484a4d03d26e353e45`; packet range-plus-bytes SHA-256 `4a3d778ea9d637633abb7727bab4746eaac74f0c62a5eb7399f82894ed170999`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnit__ApplyDamage` comes from the current closure/register row. Packet label matches canonical tracked name `CUnit__ApplyDamage`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C2_BOUNDED_RUNTIME` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CUnit__ApplyDamage(void * this, float damage_amount, void * damage_source, int apply_shields, int mesh_part_index)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CUnit__ApplyDamage(void * this, float damage_amount, void * damage_source, int apply_shields, int mesh_part_index)
```
- Packet-declared parameter list: `void * this, float damage_amount, void * damage_source, int apply_shields, int mesh_part_index`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00855090`, `DAT_008a9d84`, `DAT_008a9d9c`, `DAT_009c3df0`, `s_Billy_Fighter_00633b88`, `s_C__dev_ONSLAUGHT2_Unit_cpp_00633b6c`, `s_Tara_Fighter_00633b98`, `s_nexus_00633af4`, `s_weakpoint_00633ae8`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CLine__ctor_copy` `0x004098e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold` `0x00444030` ×1 site(s) (STATIC_DIRECT).
- Callee `CMCMech__BuildInterpolatedPoseAndAnchor` `0x004b0fb0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMessage__ctor_base` `0x004b6e50` ×1 site(s) (STATIC_DIRECT).
- Callee `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance` `0x004b7ca0` ×1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__CreateEffect` `0x004cb3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__ResetDamageCooldownTimer` `0x004e6660` ×1 site(s) (STATIC_DIRECT).
- Callee `CText__GetStringById` `0x004f2580` ×4 site(s) (STATIC_DIRECT).
- Callee `CWorld__FindFirstThingToHitLine` `0x0050b030` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` ×1 site(s) (STATIC_DIRECT).
- Callee `stricmp` `0x00568390` ×3 site(s) (STATIC_DIRECT).
- Caller `CAirUnit__ApplyDamageAndResolveSlot19Vector_004037a0` `0x004037a0` ×1 site(s) (instruction-flow).
- Caller `CBuilding__VFunc_40_004179a0` `0x004179a0` ×1 site(s) (instruction-flow).
- Caller `CHiveBoss__ForwardApplyDamageUnlessFlag01000000_00480050` `0x00480050` ×1 site(s) (instruction-flow).
- Caller `CInfantryUnit__VFunc40_HandleCollisionDamageReaction` `0x00489650` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave835 static read-back/signature/comment hardening: CUnit__ApplyDamage is important shared CUnit damage/lifetime infrastructure, not throwaway tail code. RET 0x10 at 0x004fa4a7 plus direct callsite pushes at 0x004037be, 0x00417a16, 0x0048006d, and 0x004898b0 prove four explicit stack arguments after ECX: damage_amount, damage_source, apply_shields, and mesh_part_index. Nineteen DATA slots at 0x005dd828/0x005dfa38/0x005dfddc/0x005e002c/0x005e027c/0x005e0724/0x005e0980/0x005e0bd0/0x005e1080/0x005e1530/0x005e1c24/0x005e232c/0x005e257c/0x005e2a1c/0x005e3114/0x005e3374/0x005e3de0/0x005e403c/0x005e4298 point at this body. Observed static behavior resets a damage cooldown helper through this+0x148, scales damage by profile/state fields, repairs health-like this+0xf8 for non-positive damage, applies nexus/weakpoint mesh-part gates using s_nexus_00633af4 and s_weakpoint_00633ae8, forwards to CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold when this+0x178 exists, otherwise applies shield-like this+0x100 before life-like this+0xf8, dispatches death/cleanup vfuncs, emits a particle effect when the profile effect pointer is present, and queues profile/Tara/Billy damage text through CMessageBox with the Unit.cpp debug allocation anchor 0x00633b6c line 0x44d. Static retail Ghidra evidence only; exact source body identity, concrete CUnit/profile/damage-source/segment layouts, exact message text semantics, runtime damage/shield/death behavior, BEA patching, and rebuild parity remain deferred.”
- The displayed decompile is non-empty and SHA-256 `e59ee512abfe4b401230496836d6a92900bcdc6127eea52c06875152476c52f5`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 4 caller record(s), 12 callee record(s), and 5 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-damage`; value: corroborated in 4/10 coverage sessions; evidence `level-opening-3m-v1-level110, level-opening-3m-v1-level201, level-opening-3m-v1-level231, level-opening-3m-v1-level232`.
- Session `batch-2`; question `contract-damage`; value: corroborated in 3/10 coverage sessions; evidence `level-opening-3m-v1-level311, level-opening-3m-v1-level312, level-opening-3m-v1-level322`.
- Session `batch-3`; question `contract-damage`; value: corroborated in 6/10 coverage sessions; evidence `level-opening-3m-v1-level421, level-opening-3m-v1-level422, level-opening-3m-v1-level431, level-opening-3m-v1-level432 …`.
- Session `batch-4`; question `contract-damage`; value: corroborated in 2/10 coverage sessions; evidence `level-opening-3m-v1-level720, level-opening-3m-v1-level731`.
- Session `batch-5`; question `contract-damage`; value: corroborated in 2/10 coverage sessions; evidence `level-opening-3m-v1-level732, level-opening-3m-v1-level855`.
- Session `batch-6`; question `contract-damage`; value: corroborated in 1/11 coverage sessions; evidence `level-opening-3m-v1-level862`.
- Session `batch-7`; question `contract-damage`; value: corroborated in 2/7 coverage sessions; evidence `level521-native-20260802-0018-take1, level521-native-20260802-0018-take2`.
- Session `batch-8`; question `contract-damage`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 3 BEA.exe coverage bitmaps`.
- Session `batch-10`; question `contract-damage`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 11; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004f9a90.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `e59ee512abfe4b401230496836d6a92900bcdc6127eea52c06875152476c52f5`.
- Digest derivation: closure SHA-256 hashes canonical range text `004f9a90:004fa4a9;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `OPEN_EXECUTED` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00633ae8` length 10 SHA-256 `aa44c587a7af347111f7802a8998287274f4f2ac1d042c14934c3be4af5a1eee` value `weakpoint`.
- Packet string ref `0x00633af4` length 6 SHA-256 `f5cfcb570b7edac2ed16e1a025d50155d6148de7397f4068790cdfc142300070` value `nexus`.
- Packet string ref `0x00633b6c` length 27 SHA-256 `322972ddbfcd9f5c5e7e9c684df9cbcf950ff4a31bec83e6607513f33d816757` value `C:\\dev\\ONSLAUGHT2\\Unit.cpp`.
- Packet string ref `0x00633b88` length 16 SHA-256 `8d558af3c616d701b83353910445b32544c36ea30e623178410a8911bbd2b1e1` value `Billy Fighter`.
- Packet string ref `0x00633b98` length 16 SHA-256 `4cc8be2584c8a75aad43360265f457f28aa330eef7ff6fada830cace657d765e` value `Tara Fighter`.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
