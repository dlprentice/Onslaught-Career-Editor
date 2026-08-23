# CBattleEngine__StartDieProcess

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CBattleEngine__StartDieProcess` at `0x0040bfd0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040bfd0`

## Identity
- Body `[0x0040bfd0,0x0040c17b]`, 428 bytes, 137 closure instructions. Raw pristine-body SHA-256 `d0fa743cf06a17137c604f4a58d4c9fe21a9722ed94799a9a464c11b0d98d14e`; closure range SHA-256 `201bde2fd5b4763bd55ed37bd9b3664acad1b10cd42a246ee59a4ea33dee87d8`; packet range-plus-bytes SHA-256 `d64aa7da35a7e96e6f7ae4ebdacaf4abd4bb8b27e7f4f89f7238d1fd32c1b38d`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CBattleEngine__StartDieProcess` comes from the current closure/register row. Packet label matches canonical tracked name `CBattleEngine__StartDieProcess`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CBattleEngine__StartDieProcess(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CBattleEngine__StartDieProcess(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_006601e8`, `DAT_006601ec`, `DAT_006601f0`, `DAT_006601f4`, `DAT_00672fd0`, `DAT_0082b400`, `DAT_008a9a98`, `s_Oily_Smoke_Effect_006234c8`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CGeneralVolume__SpawnPickupAndDispatch` `0x0040dfb0` ×1 site(s) (STATIC_DIRECT).
- Callee `CController__SetVibration` `0x0042e750` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__DeclarePlayerDead` `0x0046f550` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__GetController` `0x004705d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__CreateEffect` `0x004cb3d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CParticleSet__FindByNameAndTrackLinkSlot` `0x004cd7a0` ×1 site(s) (STATIC_DIRECT).
- Callee `IScript__CallEventId3_OrReset` `0x005337e0` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/BattleEngine.cpp` lines `2617-2650` defines `CBattleEngine::StartDieProcess` as `BOOL CBattleEngine::StartDieProcess()`; exact extracted source-body SHA-256 `d882c153db4650eed34d3334fa88af0f439960368ba058453c8d4b79e72d4327`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=4, switch=0, for=0, while=0; named call tokens `AddParticle`, `DeclarePlayerDead`, `Died`, `Explode`, `GetController`, `GetNumber`, `GetPD`, `IsDying`, `SetPos`, `SetVibration`, `ToRead`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Signature/comment re-audit: source-aligned CBattleEngine::StartDieProcess. Retail body checks the dying flag, stops player vibration, sets the dying bit, notifies CGame__DeclarePlayerDead, tears down mission script state, calls the explode/pickup path, and starts the oily smoke effect. Static identity/read-back only; runtime death behavior is not re-proven.”
- The displayed decompile is non-empty and SHA-256 `f42c19846f706754b4405a22fa0660bd865d7758dfc9768359fef461112e6aff`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 7 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-2`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-3`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-4`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-5`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-6`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 11 BEA.exe coverage bitmaps`.
- Session `batch-7`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 7 BEA.exe coverage bitmaps`.
- Session `batch-8`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 4 BEA.exe coverage bitmaps`.
- Session `batch-9`; question `contract-damage`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 3 BEA.exe coverage bitmaps`.
- Session `batch-10`; question `contract-damage`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 9; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040bfd0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `f42c19846f706754b4405a22fa0660bd865d7758dfc9768359fef461112e6aff`.
- Digest derivation: closure SHA-256 hashes canonical range text `0040bfd0:0040c17b;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x006234c8` length 18 SHA-256 `06ada570323cc6cb85ec517c5bb6a6eec974051f2fa1073b81e6b606642722b2` value “Oily Smoke Effect”.
- Source crosswalk: `references/Onslaught/BattleEngine.cpp` `CBattleEngine::StartDieProcess` line 2617 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`, `reverse-engineering/source-crosswalk/audit/remediation-wave1.tsv`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
