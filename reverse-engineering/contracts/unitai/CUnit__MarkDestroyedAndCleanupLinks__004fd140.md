# CUnit__MarkDestroyedAndCleanupLinks

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnit__MarkDestroyedAndCleanupLinks` at `0x004fd140`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004fd140`

## Identity
- Body `[0x004fd140,0x004fd225]`, 230 bytes, 71 closure instructions. Raw pristine-body SHA-256 `e46dc856ae589724b790f97c4232a8675fa3d96d078d2b9abf09883a1a56ccb8`; closure range SHA-256 `559f054b3a36d35451c509bea3ff391c857f9b031532cc3a75ee8879e48b4b84`; packet range-plus-bytes SHA-256 `de3a4d0645031d07bba63410331c57d13adf5066d86bab6cc41db1def54a4651`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnit__MarkDestroyedAndCleanupLinks` comes from the current closure/register row. Packet label matches canonical tracked name `CUnit__MarkDestroyedAndCleanupLinks`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `int __fastcall CUnit__MarkDestroyedAndCleanupLinks(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __fastcall CUnit__MarkDestroyedAndCleanupLinks(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_008551c0`, `DAT_00855228`, `DAT_00896988`, `DAT_008a9b8c`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×1 site(s) (STATIC_DIRECT).
- Callee `CDestructableSegmentsController__TriggerCoreCascadeIfEligible` `0x004443f0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__KillSamplesForThing` `0x004e1130` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__Remove` `0x004e5bd0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__GetTypePriorityWeight` `0x00511510` ×2 site(s) (STATIC_DIRECT).
- Callee `IScript__CallEventId5_OrReset` `0x00533660` ×1 site(s) (STATIC_DIRECT).
- Caller `CAirUnit__ReleaseAllAttachedParticleNodes` `0x00403690` ×1 site(s) (instruction-flow).
- Caller `CBuilding__VFunc_50_00417a40` `0x00417a40` ×1 site(s) (instruction-flow).
- Caller `CComponent__HandleTriggerEventAndMoveToOffset` `0x00428800` ×2 site(s) (instruction-flow).
- Caller `CGroundUnit__MarkDestroyedAndResetState` `0x0047ce80` ×1 site(s) (instruction-flow).
- Caller `CHiveBoss__MaybeScheduleEvent1388ForField74_004802f0` `0x004802f0` ×1 site(s) (instruction-flow).
- Caller `CPod__TryDestroyedCleanupAndResetDeploymentGraph` `0x004d38c0` ×1 site(s) (instruction-flow).
- Caller `CSimpleBuilding__TryActivateAndEnableShadows` `0x004dfce0` ×1 site(s) (instruction-flow).
- Caller `CTentacle__VFunc_50_004f1050` `0x004f1050` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave525 signature/comment hardening: register-this helper returns 0 when this+0x2c destroyed flag bit 2 is already set; otherwise it kills sounds for this, marks that flag, adjusts global type/side counters through this+0x164 and +0x138, triggers destructible-segment cascade at +0x178, calls script event id 5 on +0x74, clears +0x144, drains +0x18c, and returns 1. Exact counter semantics, script meaning, runtime destruction behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `05e15225c183eb732ac51d7bef990afa8dfdfbb0b5f1031d790041476549be2e`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 8 caller record(s), 6 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-2`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-3`; question `contract-damage`; value: corroborated in 1/10 coverage sessions; evidence `level-opening-3m-v1-level512`.
- Session `batch-4`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-5`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-6`; question `contract-damage`; value: corroborated in 1/11 coverage sessions; evidence `level-opening-3m-v1-level862`.
- Session `batch-7`; question `contract-damage`; value: corroborated in 1/7 coverage sessions; evidence `level521-native-20260802-0018-take2`.
- Session `batch-8`; question `contract-damage`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 3 BEA.exe coverage bitmaps`.
- Session `batch-10`; question `contract-damage`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 13; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004fd140.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `05e15225c183eb732ac51d7bef990afa8dfdfbb0b5f1031d790041476549be2e`.
- Digest derivation: closure SHA-256 hashes canonical range text `004fd140:004fd225;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `OPEN_EXECUTED` and confidence `MEDIUM`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
