# CGame__DeclareLevelLost

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CGame__DeclareLevelLost` at `0x0046f430`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/game.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046f430`

## Identity
- Body `[0x0046f430,0x0046f541]`, 274 bytes, 89 closure instructions. Raw pristine-body SHA-256 `8c37724fd57e6c80748d449c92d3c20e8212cf539461f0d60b01c52f8bfddfa8`; closure range SHA-256 `dba925ee1efc7143ee9a565977e36f4c2c60b5c75228fb170c5dc72c1464e9fc`; packet range-plus-bytes SHA-256 `2ec705e0573645d3af64393d112af0491269290cc0a91fcf42e3e0c9dde58a2b`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CGame__DeclareLevelLost` comes from the current closure/register row. Packet label matches canonical tracked name `CGame__DeclareLevelLost`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CGame__DeclareLevelLost(void * this, int message, int player_died)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CGame__DeclareLevelLost(void * this, int message, int player_died)
```
- Packet-declared parameter list: `void * this, int message, int player_died`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0066f580`, `s_Level_lost_message_____s__0062c190`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CController__SetVibration` `0x0042e750` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__Printf` `0x00441740` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_TimeFromNow` `0x0044b2d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CEventManager__AddEvent_AtTime` `0x0044b370` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__Pause` `0x0046fb00` ×1 site(s) (STATIC_DIRECT).
- Callee `CText__GetStringById` `0x004f2580` ×1 site(s) (STATIC_DIRECT).
- Callee `FromWCHAR` `0x004f7d30` ×1 site(s) (STATIC_DIRECT).
- Caller `con_lose` `0x0046c200` ×1 site(s) (instruction-flow).
- Caller `CGame__DeclarePlayerDead` `0x0046f550` ×1 site(s) (instruction-flow).
- Caller `CGame__ReceiveButtonAction` `0x0046f7e0` ×1 site(s) (instruction-flow).
- Caller `CGame__RespawnPlayer` `0x00470120` ×2 site(s) (instruction-flow).
- Caller `IScript__LevelLost` `0x005381a0` ×1 site(s) (instruction-flow).
- Caller `IScript__LevelLostString` `0x005381c0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `2466-2500` defines `CGame::DeclareLevelLost` as `void CGame::DeclareLevelLost(int message, BOOL player_died)`; exact extracted source-body SHA-256 `79146d21795cba7070202f1394f9d2ec1451d825e1fc33e985b0d76910b7c118`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=4, switch=0, for=1, while=0; named call tokens `AddEvent`, `AddMessage`, `FromWCHAR`, `GetString`, `Pause`, `SetVibration`, `strcpy`.
- Source-to-retail status: tracked `SOURCE_EXACT` class supplies named identity plus tracked source-body-agreement evidence. The packet/pristine checks below independently pin the retail target; this factory does not silently widen the tracked exactness beyond that evidence row.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-aligned with CGame::DeclareLevelLost(int message, BOOL player_died). Stores loss reason message, transitions game state to level-lost, disables controller vibration, and either pauses immediately (non-death) or schedules delayed pause/fade-out events for player-death flow.”
- The displayed decompile is non-empty and SHA-256 `2c1d6e31d76e6f0908dd308055d4626bad69024541f67a67bae34de93e05fbc7`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 6 caller record(s), 7 callee record(s), and 1 string-ref record(s).

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
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 22; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0046f430.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `2c1d6e31d76e6f0908dd308055d4626bad69024541f67a67bae34de93e05fbc7`.
- Digest derivation: closure SHA-256 hashes canonical range text `0046f430:0046f541;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062c190` length 26 SHA-256 `4de53ce2e6a5fced0a479463e08f6b781b8af0ca1c538b7db51d7bb848667d80` value “Level lost message = '%s'”.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::DeclareLevelLost` line 2466 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/functions/game.cpp/CGame__DeclareLevelLost.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
