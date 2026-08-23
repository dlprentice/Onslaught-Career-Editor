# CGame__RunLevel

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CGame__RunLevel` at `0x0046e240`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/game.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046e240`

## Identity
- Body `[0x0046e240,0x0046e45b]`, 540 bytes, 151 closure instructions. Raw pristine-body SHA-256 `6bcb72c3a1d6e800ca77fea8e8a5f501b593905162b22adf21dd5c91f5bc9f7c`; closure range SHA-256 `23f692509c23de212613e4fcac31f782516e43f8f7af087617336039df2a0758`; packet range-plus-bytes SHA-256 `b3d6277fee2b5827e80c1825459c44fbc437a891d37d4f839406d686d9a0707c`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CGame__RunLevel` comes from the current closure/register row. Packet label matches canonical tracked name `CGame__RunLevel`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CGame__RunLevel(void * this, int aLevel)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CGame__RunLevel(void * this, int aLevel)
```
- Packet-declared parameter list: `void * this, int aLevel`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00662dcc`, `DAT_00662f40`, `DAT_00663498`, `DAT_0066e8c0`, `DAT_00679fa8`, `DAT_0083d448`, `DAT_0083d454`, `DAT_00889a48`, `DAT_00896988`, `DAT_0089c9a0`, `DAT_008aa4e8`, `_DAT_008552fc`, `_DAT_00855300`, `_DAT_00855304`, `_DAT_00855308`, `s_game_resources_0062c140`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CConsole__SetLoading` `0x0042bbc0` ×1 site(s) (STATIC_DIRECT).
- Callee `FatalError__ExitWithLocalizedPrefix_A` `0x0042c750` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoadingRange` `0x0042cf40` ×3 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoadingFraction` `0x0042cf70` ×3 site(s) (STATIC_DIRECT).
- Callee `FatalError_LocalizedStringId` `0x0042d080` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__Init` `0x0046c360` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__InitRestartLoop` `0x0046c430` ×2 site(s) (STATIC_DIRECT).
- Callee `CGame__ShutdownRestartLoop` `0x0046ca70` ×3 site(s) (STATIC_DIRECT).
- Callee `CGame__LoadResources` `0x0046cd30` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__RestartLoopRunLevel` `0x0046dc30` ×1 site(s) (STATIC_DIRECT).
- Callee `CGameInterface__InitResources` `0x00472a10` ×1 site(s) (STATIC_DIRECT).
- Callee `CHud__LoadTextures` `0x00481650` ×1 site(s) (STATIC_DIRECT).
- Callee `CMessageBox__LoadPortraitTextures` `0x004b7320` ×1 site(s) (STATIC_DIRECT).
- Callee `CMessageLog__LoadTextures` `0x004b8e70` ×1 site(s) (STATIC_DIRECT).
- Callee `CMusic__Stop` `0x004bb490` ×2 site(s) (STATIC_DIRECT).
- Callee `CPauseMenu__LoadPauseTextures` `0x004d0510` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__ReloadLanguageSampleBank` `0x004e2c50` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__InitResources` `0x0053d6d0` ×1 site(s) (STATIC_DIRECT).
- Caller `CLTShell__RunStressTestLevelLoop` `0x004f0200` ×1 site(s) (instruction-flow).
- Caller `CLTShell__RunFrontEndAndGameLoop` `0x004f0330` ×2 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `1573-1699` defines `CGame::RunLevel` as `EQuitType	CGame::RunLevel(SINT aLevel)`; exact extracted source-body SHA-256 `faa72c9d7ed86cc09886bb231c148742f6fc3a0ab25e2e099cf9ba0f02ff237c`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=14, switch=0, for=0, while=1; named call tokens `Init`, `InitOneOffResources`, `InitRestartLoop`, `InitRestartResources`, `LoadAllSounds`, `LoadResources`, `LoadXAPFile`, `LoadedCurrentLanguage`, `RenderDiscFailureTextAndHang`, `ResetLoadedState`, `RestartLoopRunLevel`, `SetLoading`, `SetLoadingRange`, `Shutdown`, `ShutdownRestartLoop`, `Stop`.
- Source-to-retail status: tracked `SOURCE_EXACT` class supplies named identity plus tracked source-body-agreement evidence. The packet/pristine checks below independently pin the retail target; this factory does not silently widen the tracked exactness beyond that evidence row.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-aligned mapping to CGame::RunLevel(SINT). Top-level level driver: init/startup checks, InitRestartLoop + LoadResources + one-off setup/HUD texture load, restart-loop orchestration via CGame__RestartLoopRunLevel, and final shutdown/quit-code return.”
- The displayed decompile is non-empty and SHA-256 `e7c1896a5165664aacbded60d87e289b7a7c2b34de9172b651182ab7ebf17066`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 2 caller record(s), 18 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 20; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x0046e240.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `e7c1896a5165664aacbded60d87e289b7a7c2b34de9172b651182ab7ebf17066`.
- Digest derivation: closure SHA-256 hashes canonical range text `0046e240:0046e45b;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062c140` length 15 SHA-256 `b3d173b3893a3c1cf3794ecfb3a0aa0e8b460ac7b00517b43da3d21c380b8ab4` value “game resources”.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::RunLevel` line 1573 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/functions/game.cpp/CGame__RunLevel.md`, `reverse-engineering/binary-analysis/cgame-level-lifecycle-semantics-2026-08-11.tsv`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
