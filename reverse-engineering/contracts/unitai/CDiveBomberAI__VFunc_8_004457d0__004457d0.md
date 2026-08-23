# CDiveBomberAI__VFunc_8_004457d0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CDiveBomberAI__VFunc_8_004457d0` at `0x004457d0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004457d0`

## Identity
- Body `[0x004457d0,0x004458f6]`, 295 bytes, 110 closure instructions. Raw pristine-body SHA-256 `5d0d9bde07320bf385080dcc3e143757a2f9932a99ee8e9460065ae1ad714b1d`; closure range SHA-256 `c2f512a8261c8359caaa0a6d6b00bb09d7e47c7a62040dd54bdac6f2e66b8a86`; packet range-plus-bytes SHA-256 `2fac3be93d9935aa471878bc0bf3ea17e173b31c9c75889cca873706cfe382c0`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CDiveBomberAI__VFunc_8_004457d0` comes from the current closure/register row. Packet label matches canonical tracked name `CDiveBomberAI__VFunc_8_004457d0`.
- Packet name source `USER_DEFINED` and signature source `ANALYSIS` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `undefined __thiscall CDiveBomberAI__VFunc_8_004457d0(void * this, void * param_1)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
undefined __thiscall CDiveBomberAI__VFunc_8_004457d0(void * this, void * param_1)
```
- Packet-declared parameter list: `void * this, void * param_1`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `undefined`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `DAT_008a9d9c`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGenericActiveReader__SetReader` `0x00401000` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 site(s) (STATIC_DIRECT).
- Callee `Random__NextLCGAbs` `0x004de8d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__CanFireAtTarget_BallisticArcB` `0x004fb5a0` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Class recovered from the binary's own MSVC RTTI: type descriptor -> complete object locator -> vtable, with the owning class resolved through the RTTIClassHierarchyDescriptor base-class array so an inherited method is attributed to the base that introduces it rather than to every derived class. Owner=CDiveBomberAI, vtable 0x005db1ac slot 8; slot 8 of CDiveBomberAI's PRIMARY (sub-object offset 0) vtable is this address. Ownership evidence: this address occurs in exactly one class vtable in the whole image, so no base class emits it. Function entry created 2026-07-27 from an RTTI vtable-slot target; the previous name was Ghidra's default FUN_004457d0, so no behavioural hypothesis was displaced. The name asserts CLASS MEMBERSHIP AND VTABLE SLOT ONLY - no method name is claimed, and the RTTI_CONFIRMED grade this name earns is TAUTOLOGICAL because the prefix was generated from the same RTTI the grader reads. Behaviour remains unproven. Wave: naming-wave-2026-07-27.”
- The displayed decompile is non-empty and SHA-256 `39c301b49b69d9b92c7f73901b534c84e6fa5673f00aa8b004eab4374741b356`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 4 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4`; question `corpus-combat-only`; value: combat-exclusive; 227 covered bytes; evidence `name=CDiveBomberAI__VFunc_8_004457d0`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 2; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004457d0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `39c301b49b69d9b92c7f73901b534c84e6fa5673f00aa8b004eab4374741b356`.
- Digest derivation: closure SHA-256 hashes canonical range text `004457d0:004458f6;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
