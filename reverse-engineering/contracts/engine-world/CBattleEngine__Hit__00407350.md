# CBattleEngine__Hit

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__Hit` at `0x00407350`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00407350`

## Identity
- Body `[0x00407350,0x004074cb]`, 380 bytes, 114 closure instructions. Raw pristine-body SHA-256 `8034efee2c37c5e02579dc82d4405b758cedc96d62b27909f5c66a6cea43ae8a`; closure range SHA-256 `28151a2f8b9850159b4c2f1e843f4c34e44d6258d9a79f1c4abe7a296301b210`; packet range-plus-bytes SHA-256 `b6cab23b3c123d9bb41c92495edc512b0b543ec6ea6b63f951f67e89bd2da05d`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__Hit` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__Hit`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C2_BOUNDED_RUNTIME` / closure class `PREEXISTING_GEN19_C1_OR_C2` / packet confidence `BOUNDED_CONTRACT`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CBattleEngine__Hit(void * this, void * otherThing, void * report)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__Hit(void * this, void * otherThing, void * report)
```
- Packet-declared parameter list: `void * this, void * otherThing, void * report`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CGeneralVolume__SpawnPickupAndDispatch` `0x0040dfb0` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__CreateHitRefEvaluateImpulseAndDispatchHit` `0x004fcc30` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/BattleEngine.cpp` lines `1014-1061` defines `CBattleEngine::Hit` as `void		CBattleEngine::Hit(CThing* other_thing, CCollisionReport* report)`; exact extracted source-body SHA-256 `c0416276a593e56319d365490d6878726a9fe5f29577c57274541afa24f52a7e`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=6, switch=0, for=0, while=0; named call tokens `AddMessage`, `AddShutdownEvent`, `DeclareOnObject`, `Explode`, `GetTime`, `GetVelocity`, `IsA`, `IsDying`, `MoveTo`, `Size`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Retail/source identity and bounded runtime control: 0x00407350 matches CBattleEngine::Hit (BattleEngine.h:105; BattleEngine.cpp:1014-1061). The 380-byte retail body and RET 0x8 prove two 4-byte explicit arguments. Source prototype: void Hit(CThing *other_thing, CCollisionReport *report); Ghidra keeps object types opaque. One gap-free Generation 12 invocation observed zero writes to exactly seven watched Battle Engine fields. This does not prove zero writes to other memory, other branches, or other invocations, and source architecture does not substitute for released-runtime causality. Rebuild state is NOT_READY. Gen12 READY 9d2b903d451c; proof ffb2e0b8692d.”
- The displayed decompile is non-empty and SHA-256 `eca4bc0fccbf5aeb6ae4b057a4a911142aa014dc5bc85aa7267c60be2e5e6698`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-round-impact`; value: corroborated in 3/10 coverage sessions; evidence `level-opening-3m-v1-level100, level-opening-3m-v1-level231, level-opening-3m-v1-level232`.
- Session `batch-2`; question `contract-round-impact`; value: corroborated in 4/10 coverage sessions; evidence `level-opening-3m-v1-level321, level-opening-3m-v1-level322, level-opening-3m-v1-level411, level-opening-3m-v1-level412`.
- Session `batch-3`; question `contract-round-impact`; value: corroborated in 1/10 coverage sessions; evidence `level-opening-3m-v1-level523`.
- Session `batch-4`; question `contract-round-impact`; value: corroborated in 1/10 coverage sessions; evidence `level-opening-3m-v1-level524`.
- Session `batch-5`; question `contract-round-impact`; value: corroborated in 2/10 coverage sessions; evidence `level-opening-3m-v1-level854, level-opening-3m-v1-level855`.
- Session `batch-6`; question `contract-round-impact`; value: corroborated in 1/11 coverage sessions; evidence `level-opening-3m-v1-level862`.
- Session `batch-7`; question `contract-round-impact`; value: corroborated in 1/7 coverage sessions; evidence `level521-native-20260802-0018-take2`.
- Session `batch-8`; question `contract-round-impact`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-round-impact`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 3 BEA.exe coverage bitmaps`.
- Session `batch-10`; question `contract-round-impact`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 5; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00407350.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `eca4bc0fccbf5aeb6ae4b057a4a911142aa014dc5bc85aa7267c60be2e5e6698`.
- Digest derivation: closure SHA-256 hashes canonical range text `00407350:004074cb;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `OPEN_AFTER_SURVIVED` and confidence `BOUNDED_CONTRACT`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::Hit` line 1014 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/BattleEngine.cpp/CBattleEngine__Hit.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
