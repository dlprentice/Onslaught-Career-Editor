# CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0` at `0x004ff4f0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004ff4f0`

## Identity
- Body `[0x004ff4f0,0x004ff70a]`, 539 bytes, 185 closure instructions. Raw pristine-body SHA-256 `4bf6a880bceb0db303c5adab07deb05430df97d61a8bdbe34b99cb608958f60d`; closure range SHA-256 `eb32db4fa13f563e916c95412e477857feba7ff1609e22446facfc8c38e8e3fc`; packet range-plus-bytes SHA-256 `1d4d079d3222ad9c0d84b5284dbf21cd3b748085c0f4f416686c7a99055a2521`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_008550a0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×2 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__IsValidLinkedSupportForTarget` `0x004fb3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__CanFireAtTarget_BallisticArcA` `0x004fb500` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__CanFireAtTarget_BallisticArcB` `0x004fb5a0` ×2 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__SelectBestSupportOrEscort` `0x004fb840` ×2 site(s) (STATIC_DIRECT).
- Callee `CUnit__IsCandidateSideCompatibleForTargeting` `0x004fd3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__IsActiveAndNotInState12` `0x004fd5b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__TrySpawnMembersForTarget` `0x004fdad0` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Shared CUnitAI-family update: may clear this+0xc reader when target flag bit2 set; if owner linked support missing/invalid, scans DAT_008550a0 candidates for side-compatible support, may CUnit__TrySpawnMembersForTarget, then evaluates CanFireAtTarget_BallisticArcB/A into this+0x1c/0x18 or calls this vfunc +0x2c; else clears fire flags and refreshes escort/fire gates on current reader. Static listing/xref/vtable evidence only; exact source virtual name, AI layout, runtime behavior, BEA patching, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `0d1500f4ad1433d6278da11d13d8de764daa6a251a23cfc38f16399ce799f7f9`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 8 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level100, level-opening-3m-v1-level110, level-opening-3m-v1-level200, level-opening-3m-v1-level201 …`.
- Session `batch-2`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level300, level-opening-3m-v1-level311, level-opening-3m-v1-level312, level-opening-3m-v1-level321 …`.
- Session `batch-3`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level421, level-opening-3m-v1-level422, level-opening-3m-v1-level431, level-opening-3m-v1-level432 …`.
- Session `batch-4`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level524, level-opening-3m-v1-level600, level-opening-3m-v1-level611, level-opening-3m-v1-level612 …`.
- Session `batch-5`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level732, level-opening-3m-v1-level741, level-opening-3m-v1-level742, level-opening-3m-v1-level800 …`.
- Session `batch-6`; question `contract-unit-ai`; value: corroborated in 10/11 coverage sessions; evidence `level-opening-3m-v1-level856, level-opening-3m-v1-level858, level-opening-3m-v1-level859, level-opening-3m-v1-level860 …`.
- Session `batch-7`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level901, level-opening-3m-v1-level902, level-opening-3m-v1-level903, level-opening-3m-v1-level904 …`.
- Session `batch-8`; question `contract-unit-ai`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-unit-ai`; value: CORROBORATED live in every coverage session of batch; evidence `q-pilot-cov-l700-20260731, q-pilot-cov-l742-20260731, q-pilot-cov-l742-rep2-20260731`.
- Session `batch-10`; question `contract-unit-ai`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 22; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004ff4f0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `0d1500f4ad1433d6278da11d13d8de764daa6a251a23cfc38f16399ce799f7f9`.
- Digest derivation: closure SHA-256 hashes canonical range text `004ff4f0:004ff70a;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
