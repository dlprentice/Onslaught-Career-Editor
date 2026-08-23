# CBattleEngine__ComputeProjectileMetricFromTargetProfile

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__ComputeProjectileMetricFromTargetProfile` at `0x00509c80`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00509c80`

## Identity
- Body `[0x00509c80,0x00509e36]`, 439 bytes, 172 closure instructions. Raw pristine-body SHA-256 `82c0c2af9a42d6b564ac3044da78dcb5239d49bd1cf200bc777f1bcd5df8f628`; closure range SHA-256 `afd134dcb67d4b1696859dd9f99a5af136d205b0d581afc1c1cc30c42c68d603`; packet range-plus-bytes SHA-256 `fd52cd3a8197b01b72f83e6b936c71fa634ab17e14018499f6646136b9f29bd6`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__ComputeProjectileMetricFromTargetProfile` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__ComputeProjectileMetricFromTargetProfile`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `double __thiscall CBattleEngine__ComputeProjectileMetricFromTargetProfile(void * this, float target_x, float target_y, float target_z, float target_w)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
double __thiscall CBattleEngine__ComputeProjectileMetricFromTargetProfile(void * this, float target_x, float target_y, float target_z, float target_w)
```
- Packet-declared parameter list: `void * this, float target_x, float target_y, float target_z, float target_w`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `double`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_008553ec`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CSPtrSet__First` `0x00406d20` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__Next` `0x00406d30` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__ComputeMaxBallisticTravelDistance` `0x005099a0` ×1 site(s) (STATIC_DIRECT).
- Callee `TargetSet__GetEntryByIndex` `0x00509e40` ×1 site(s) (STATIC_DIRECT).
- Caller `CBattleEngine__CalcUnitOverCrossHair` `0x0040acc0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave553 signature/comment hardening: RET 0x10 and CBattleEngine__CalcUnitOverCrossHair callsite vector copies prove four explicit vector dwords after ECX. When an active ballistic profile is available the body forwards the target vector to CUnit__ComputeMaxBallisticTravelDistance; otherwise it selects a target/profile entry from DAT_008553ec by range bucket and returns one of several projectile metric fields or speed/range products. Static retail-binary evidence only; exact profile metric meaning, concrete BattleEngine/target-profile layouts, runtime targeting behavior, BEA launch, patching, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `f8d8e2ced655781ef2db093ddd661cc16e2632575c20e46306f587ced74e97eb`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 4 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 24; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00509c80.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `f8d8e2ced655781ef2db093ddd661cc16e2632575c20e46306f587ced74e97eb`.
- Digest derivation: closure SHA-256 hashes canonical range text `00509c80:00509e36;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
