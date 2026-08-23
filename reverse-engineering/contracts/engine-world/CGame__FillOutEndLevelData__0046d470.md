# CGame__FillOutEndLevelData

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CGame__FillOutEndLevelData` at `0x0046d470`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/game.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046d470`

## Identity
- Body `[0x0046d470,0x0046d807]`, 920 bytes, 258 closure instructions. Raw pristine-body SHA-256 `2cd8ee2693c5b5064e085d8893eadee34039eeadfa5e00d12fe7f4b6a54f8fd2`; closure range SHA-256 `856ebfefaeb323622f4a2a597bf491973288059b33d09b4057196f27cef0c241`; packet range-plus-bytes SHA-256 `771382930a8ea6da23c44494bb154852abb535095f3a223eee15ecc9843c8616`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CGame__FillOutEndLevelData` comes from the current closure/register row. Packet label matches canonical tracked name `CGame__FillOutEndLevelData`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CGame__FillOutEndLevelData(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CGame__FillOutEndLevelData(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0062c040`, `DAT_0066f580`, `DAT_006728f8`, `DAT_00672d78`, `DAT_00672dc8`, `DAT_00672e18`, `DAT_00672e1c`, `DAT_00672e20`, `DAT_00672e24`, `DAT_00672e34`, `DAT_00672e44`, `DAT_00672fd0`, `DAT_00855150`, `DAT_0085515c`, `_DAT_00672e28`, `_DAT_00672e2c`, `_DAT_00672e38`, `_DAT_00672e3c`, `_DAT_00672e40`, `s_FATAL_ERROR__two_many_base_thing_0062c048`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CConsole__Printf` `0x00441740` ×1 site(s) (STATIC_DIRECT).
- Callee `CEndLevelData__IsAllSecondaryObjectivesComplete` `0x004496e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__At` `0x004e5c90` ×1 site(s) (STATIC_DIRECT).
- Caller `CGame__RestartLoopRunLevel` `0x0046dc30` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `910-1043` defines `CGame::FillOutEndLevelData` as `void	CGame::FillOutEndLevelData()`; exact extracted source-body SHA-256 `4eb93eb544d0b51d4f520e8b0efb3a52000ab184b8f80bb107350b7e0f78c2fb`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=19, switch=0, for=2, while=0; named call tokens `AddMessage`, `At`, `GetBaseWorldThingNB`, `GetNumEnemyThingKilled`, `GetNumSecondaryObjectives`, `GetPlayer`, `GetTime`, `IsAllSecondaryObjectivesComplete`, `IsDying`, `SetAll`, `Size`, `ToRead`, `_GetClassName`, `saved`, `strcpy`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-aligned mapping to CGame::FillOutEndLevelData(). Captures end-of-level snapshot data (objectives, timers, score/lives context, level kill counts, progression/grade fields, and related career-facing summary values).”
- The displayed decompile is non-empty and SHA-256 `15910d7bcacc79dd78b16668f31d9afbdf2cd98ae0c21880a55f72aaaa94ded3`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 3 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-2`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-3`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-4`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-5`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 10 BEA.exe coverage bitmaps`.
- Session `batch-6`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 11 BEA.exe coverage bitmaps`.
- Session `batch-7`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 7 BEA.exe coverage bitmaps`.
- Session `batch-8`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 4 BEA.exe coverage bitmaps`.
- Session `batch-9`; question `contract-level-flow`; value: NOT EXECUTED anywhere in batch (bounded: these captures only); evidence `absent from all 3 BEA.exe coverage bitmaps`.
- Session `batch-10`; question `contract-level-flow`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 18; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0046d470.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `15910d7bcacc79dd78b16668f31d9afbdf2cd98ae0c21880a55f72aaaa94ded3`.
- Digest derivation: closure SHA-256 hashes canonical range text `0046d470:0046d807;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062c048` length 80 SHA-256 `099f444468c9162ad9d05c652b82f205161b07fde74245012da08af2698e8b63` value “FATAL ERROR: two many base things trying to be saved (size = %d) max size = %d ”.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::FillOutEndLevelData` line 910 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/game.cpp/CGame__FillOutEndLevelData.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
