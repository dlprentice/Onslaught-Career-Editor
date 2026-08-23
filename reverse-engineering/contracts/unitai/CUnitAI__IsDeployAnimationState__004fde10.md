# CUnitAI__IsDeployAnimationState

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CUnitAI__IsDeployAnimationState` at `0x004fde10`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004fde10`

## Identity
- Body `[0x004fde10,0x004fde2d]`, 30 bytes, 11 closure instructions. Raw pristine-body SHA-256 `77e6235364fe52855fe7f7f6778245efc47acb26dc65baf959d9e04d7e7a8e1d`; closure range SHA-256 `4022ffe3263d9ea15b1417a75828e2366933b99fc2fa5747aec5afb7cea92557`; packet range-plus-bytes SHA-256 `b7089f58cfc775f6abd21efce06b48b5385813a4c69039d02595607adb5b2fae`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CUnitAI__IsDeployAnimationState` comes from the current closure/register row. Packet label matches canonical tracked name `CUnitAI__IsDeployAnimationState`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `PREEXISTING_GEN19_C1_OR_C2` / packet confidence `CANDIDATE_CONTRACT`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `bool __fastcall CUnitAI__IsDeployAnimationState(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
bool __fastcall CUnitAI__IsDeployAnimationState(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `bool`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `CComponentGuide__UpdateHeadingTowardTargetClamped` `0x00429270` ×1 site(s) (instruction-flow).
- Caller `CGroundUnit__UpdateLinkedEffectsByHeightClearance` `0x0047c970` ×1 site(s) (instruction-flow).
- Caller `CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750` `0x0047d750` ×1 site(s) (instruction-flow).
- Caller `CTentacleGuide__VFunc_3_004f19a0` `0x004f19a0` ×1 site(s) (instruction-flow).
- Caller `CTerrainGuide__VFunc03_UpdateGuidanceState_004f1ee0` `0x004f1ee0` ×1 site(s) (instruction-flow).
- Caller `CThunderheadGuide__VFunc_03_004f4e40` `0x004f4e40` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Register-this predicate: returns true when state field this+0x244 is 3, 4, or 5, else false. Sibling writer CUnit__BeginDeployAnimationIfIdle is Unit-owned on the same field. Callers include UnitAI plus GroundUnit/Guide helpers, but this is Unit-state-shaped — CUnitAI__ owner is weak. Rename toward CUnit__IsDeployAnimationState (or SharedUnit predicate) remains propose-only outside this comment lane. Static retail evidence only; deploy animation enum names, runtime animation behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `28a647764a0172f91a4b2d277855605d44e1578c677627a94eea0f7cee64ab80`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 6 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 15; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004fde10.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `28a647764a0172f91a4b2d277855605d44e1578c677627a94eea0f7cee64ab80`.
- Digest derivation: closure SHA-256 hashes canonical range text `004fde10:004fde2d;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `OPEN_EXECUTED` and confidence `CANDIDATE_CONTRACT`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
