# CUnitAI__SelectOrRefreshCloseTarget_004ff710

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__SelectOrRefreshCloseTarget_004ff710` at `0x004ff710`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004ff710`

## Identity
- Body `[0x004ff710,0x004ffb57]`, 1096 bytes, 353 closure instructions. Raw pristine-body SHA-256 `e4f2106e542daa0af8b3f92409641169e35f6c7a573c73956693545756703d05`; closure range SHA-256 `7ead23272dbaf8201b08bb45deb8c3a1f7bf1e62842f6d0383ef85995f2cf4ae`; packet range-plus-bytes SHA-256 `e4ec1b24639842f436ba85fc37bc9615aa0c0f1dab6c0fa1da9928db5ba92147`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__SelectOrRefreshCloseTarget_004ff710` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__SelectOrRefreshCloseTarget_004ff710`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CUnitAI__SelectOrRefreshCloseTarget_004ff710(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CUnitAI__SelectOrRefreshCloseTarget_004ff710(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00855090`, `DAT_008550b0`, `DAT_008550c0`, `DAT_008a9d9c`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×2 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__IsValidLinkedSupportForTarget` `0x004fb3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__CanFireAtTarget_BallisticArcA` `0x004fb500` ×2 site(s) (STATIC_DIRECT).
- Callee `CUnit__CanFireAtTarget_BallisticArcB` `0x004fb5a0` ×2 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__GetSupportMinEngageDistance` `0x004fb780` ×1 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__GetSupportMaxEngageDistance` `0x004fb7e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSquadNormal__SelectBestSupportOrEscort` `0x004fb840` ×4 site(s) (STATIC_DIRECT).
- Callee `CUnit__IsCandidateSideCompatibleForTargeting` `0x004fd3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__IsActiveAndNotInState12` `0x004fd5b0` ×3 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Shared CUnitAI-family close-target selector/refresher (reader distance gates, ballistic fire flags this+0x18/0x1c, side-keyed scan + SetReader, returns *(this+0xc) pointer may be null). ECX receiver; bare `RET` (caller cleanup). Declared `int __thiscall ...(void * this)` / boolean tag is false — returns a target/reader pointer, not a predicate. Shape is `void * __thiscall (void * this)` (do not invent typed unit/reader typedef beyond that plate). Static retail evidence only; exact scoring policy, runtime targeting UX, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `60e225ebd37a289c14b627b7c69c3984180efb23b6bf4687ed7941c12295ad99`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 10 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 23; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004ff710.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `60e225ebd37a289c14b627b7c69c3984180efb23b6bf4687ed7941c12295ad99`.
- Digest derivation: closure SHA-256 hashes canonical range text `004ff710:004ffb57;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
