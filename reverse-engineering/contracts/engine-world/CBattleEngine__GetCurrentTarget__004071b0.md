# CBattleEngine__GetCurrentTarget

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__GetCurrentTarget` at `0x004071b0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004071b0`

## Identity
- Body `[0x004071b0,0x00407305]`, 342 bytes, 121 closure instructions. Raw pristine-body SHA-256 `311eadaf6a6ab665fec93b03a0d9181ab7dbef6df718d4f296d7e29b0d1879d4`; closure range SHA-256 `7edebef118a01681a0c11cbeeff11d3ca588d8c08f793e3dd42c263642bb6481`; packet range-plus-bytes SHA-256 `407618c4629b53a90f3180edb21f482285c154a9055850c602b70a88b798e2ea`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__GetCurrentTarget` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__GetCurrentTarget`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CBattleEngine__GetCurrentTarget(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void * __thiscall CBattleEngine__GetCurrentTarget(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void *`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00672fd0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/BattleEngine.cpp` lines `913-977` defines `CBattleEngine::GetCurrentTarget` as `CUnit* CBattleEngine::GetCurrentTarget()`; exact extracted source-body SHA-256 `15ca8971132fac816cd471f30e7dff91aa80d0c4dcbbcb3115bc4e7eb1ef26df`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=9, switch=0, for=3, while=0; named call tokens `First`, `GetTime`, `Next`, `ToRead`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Retail/source identity: 0x004071B0 matches virtual CBattleEngine::GetCurrentTarget (BattleEngine.cpp:913-977): it increments mCurrentTarget, handles mRecentLocks, scans mLocks for a finished target, then round-robins mFiredLocks; retail offsets and branch order match. This is vtable slot 81. Level 521 raw boundary rows observed 17 calls and immediately paired entries from 0x00507395 on receiver 0x079B9750. Return-value association is withheld pending the call-context gap repair; source/body identity, pointer-or-null return shape, exact null reasons, pointee type, and global behavior retain their stated evidence boundaries.”
- The displayed decompile is non-empty and SHA-256 `e673033d4e62f24085e5484d4e34573764a913ea64636b4bb29deba0a479f1fc`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `level521-native-20260802-0018-take4, level521-native-20260802-0018-take2, level521-native-20260802-0018-take1`; question `corpus-combat-only`; value: combat-exclusive; 339 covered bytes; evidence `name=CBattleEngine__GetCurrentTarget`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 4; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004071b0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `e673033d4e62f24085e5484d4e34573764a913ea64636b4bb29deba0a479f1fc`.
- Digest derivation: closure SHA-256 hashes canonical range text `004071b0:00407305;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::GetCurrentTarget` line 913 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__GetCurrentTarget.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
