# CInfantryUnit__VFunc50_HandleDeathPickupAndEffects

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CInfantryUnit__VFunc50_HandleDeathPickupAndEffects` at `0x00489b40`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00489b40`

## Identity
- Body `[0x00489b40,0x00489dde]`, 671 bytes, 196 closure instructions. Raw pristine-body SHA-256 `8836f4fe16824ebe3b7f8434afc7dce02f4ed82565723b97c0592489a0ca60d0`; closure range SHA-256 `70b087e7e083aaecd457324fc67ab8e3313bac58607259d57003422d2cb12464`; packet range-plus-bytes SHA-256 `8a9e4d968778c9daaae70706cb583bb3dc92d134c19434c630221121974a65b0`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CInfantryUnit__VFunc50_HandleDeathPickupAndEffects` comes from the current closure/register row. Packet label matches canonical tracked name `CInfantryUnit__VFunc50_HandleDeathPickupAndEffects`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `int __fastcall CInfantryUnit__VFunc50_HandleDeathPickupAndEffects(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __fastcall CInfantryUnit__VFunc50_HandleDeathPickupAndEffects(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`, `DAT_0067a6b8`, `DAT_0067a6bc`, `DAT_0067a6c0`, `DAT_0067a6c4`, `DAT_008553f8`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `ElapsedTime__BelowThreshold_D0` `0x00401fa0` ×1 site(s) (STATIC_DIRECT).
- Callee `CCollisionSeekingRound__SetCollisionMask` `0x00426480` ×1 site(s) (STATIC_DIRECT).
- Callee `CGroundUnit__MarkDestroyedAndResetState` `0x0047ce80` ×1 site(s) (STATIC_DIRECT).
- Callee `CGroundUnit__ClearLinkedThingFlagsAndResetCounter` `0x0047cea0` ×1 site(s) (STATIC_DIRECT).
- Callee `CInitThing__ctor` `0x0048dcf0` ×1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__CreateEffect` `0x004cb3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CWorldPhysicsManager__CreateExplosion` `0x0050ff10` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave1076 boundary recovery: CInfantryUnit primary vtable 0x005e2730 slot 49 (slot address 0x005e27f4) DATA-xrefs to this previously missing function. Fresh pre-state listed the entry as INSTRUCTION_NO_FUNCTION with missing metadata and missing decompile; the recovered body ends at 0x00489dde RET and does not absorb the next adjacent entry/function at 0x00489de0. Body calls CGroundUnit__MarkDestroyedAndResetState, sets the collision-seeking round mask to -1, creates a pickup via CWorldPhysicsManager__CreatePickup, builds a stack CInitThing-like payload, checks height/linked state, creates a particle effect through CParticleManager__CreateEffect, clears linked flags through CGroundUnit__ClearLinkedThingFlagsAndResetCounter, and returns 1 on the normal completed path. Static retail Ghidra metadata/xref/instruction/vtable evidence only; exact source virtual name, concrete CInfantryUnit/CUnitAI/layout semantics, runtime infantry behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.”
- The displayed decompile is non-empty and SHA-256 `c26b9ada5eb888598947e2b4e06169da121edf474ae279ffa32701cc301eb2d8`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 7 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take2`; question `corpus-combat-only`; value: combat-exclusive; 553 covered bytes; evidence `name=CInfantryUnit__VFunc50_HandleDeathPickupAndEffects`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 6 immutable manifest SHA-256 `9f24ea299ab115b57de8eda78fd01e374647c888e41ce248a0624ee78fadd13e`, row 8; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00489b40.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `c26b9ada5eb888598947e2b4e06169da121edf474ae279ffa32701cc301eb2d8`.
- Digest derivation: closure SHA-256 hashes canonical range text `00489b40:00489dde;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
