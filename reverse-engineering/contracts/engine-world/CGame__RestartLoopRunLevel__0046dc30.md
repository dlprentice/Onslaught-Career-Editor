# CGame__RestartLoopRunLevel

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CGame__RestartLoopRunLevel` at `0x0046dc30`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/game.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046dc30`

## Identity
- Body `[0x0046dc30,0x0046e22a]`, 1531 bytes, 408 closure instructions. Raw pristine-body SHA-256 `dee636c3cc58ab1e673357436d2447b17aa379f79afa4a09bcc23905fa4e45f6`; closure range SHA-256 `0d2fa4692bb0360a743cec142fcbd12612b92b95abc7f61d5223a17499a06f4e`; packet range-plus-bytes SHA-256 `829179bce91d1228dc2ee852265a9da7d8025eec7b531634e81d041e7140a1d0`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CGame__RestartLoopRunLevel` comes from the current closure/register row. Packet label matches canonical tracked name `CGame__RestartLoopRunLevel`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CGame__RestartLoopRunLevel(void * this, int aLevel)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CGame__RestartLoopRunLevel(void * this, int aLevel)
```
- Packet-declared parameter list: `void * this, int aLevel`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_0062493c`, `DAT_0062ba44`, `DAT_00662dcc`, `DAT_00662dd4`, `DAT_00663050`, `DAT_00663498`, `DAT_0066e8c0`, `DAT_00672fd0`, `DAT_00679ec4`, `DAT_0083d448`, `DAT_0083d454`, `DAT_008550d0`, `DAT_00889a48`, `DAT_00896988`, `DAT_0089c9a0`, `DAT_008a9ac0`, `DAT_009c3df0`, `DAT_009c8010`, `s_Dump_the_game_time_records_0062c114`, `s_Post_Load__d_0062c130`, `s_autoexec_con_0062c0f4`, `s_dumptimerecords_0062c104`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `Atmospherics__Shutdown` `0x00404c10` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__ExecScript` `0x0042ad30` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__RegisterCommand` `0x0042af80` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoading` `0x0042bbc0` ×2 site(s) (STATIC_DIRECT).
- Callee `CConsole__RenderLoadingScreen` `0x0042c810` ×2 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoadingRange` `0x0042cf40` ×4 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoadingFraction` `0x0042cf70` ×7 site(s) (STATIC_DIRECT).
- Callee `CController__SetNonInteractiveSection` `0x0042d7d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CController__InactivityMeansQuitGame` `0x0042d810` ×1 site(s) (STATIC_DIRECT).
- Callee `CController__GetToControl` `0x0042e4b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CController__SetToControl` `0x0042e610` ×1 site(s) (STATIC_DIRECT).
- Callee `CEngine__InitDamageSystem` `0x0044a130` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__PlaySound` `0x00468770` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__ShutdownRestartLoop` `0x0046ca70` ×2 site(s) (STATIC_DIRECT).
- Callee `CGame__LoadLevel` `0x0046cdf0` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__PostLoadProcess` `0x0046d040` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__FillOutEndLevelData` `0x0046d470` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__RunIntroFMV` `0x0046d890` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__Update` `0x0046e910` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__MainLoop` `0x0046eee0` ×1 site(s) (STATIC_DIRECT).
- Callee `CMemoryManager__DumpMemory` `0x004a2a80` ×1 site(s) (STATIC_DIRECT).
- Callee `CMonitor__Shutdown` `0x004bac40` ×1 site(s) (STATIC_DIRECT).
- Callee `CMusic__PlaySelection` `0x004bb8c0` ×1 site(s) (STATIC_DIRECT).
- Callee `CEngine__SetOptionValueAndNotifyTarget` `0x004d3020` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__KillAllSamples` `0x004e12b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSoundManager__UpdateStatus` `0x004e1b20` ×1 site(s) (STATIC_DIRECT).
- Callee `CStaticShadows__Reattach` `0x004ebc00` ×1 site(s) (STATIC_DIRECT).
- Callee `CUnit__PlayRespawnVoiceCueIfAvailable` `0x004f99b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CEngine__TrimVbIbPoolCapacitiesPow2` `0x005015c0` ×1 site(s) (STATIC_DIRECT).
- Callee `PLATFORM__Process` `0x00515880` ×1 site(s) (STATIC_DIRECT).
- Callee `PLATFORM__GetSysTimeFloat` `0x005159e0` ×4 site(s) (STATIC_DIRECT).
- Callee `lookup_FMV` `0x00523120` ×2 site(s) (STATIC_DIRECT).
- Callee `MEM_MANAGER__Cleanup` `0x00549270` ×1 site(s) (STATIC_DIRECT).
- Callee `sprintf` `0x0055de9b` ×1 site(s) (STATIC_DIRECT).
- Caller `CGame__RunLevel` `0x0046e240` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `1260-1569` defines `CGame::RestartLoopRunLevel` as `EQuitType	CGame::RestartLoopRunLevel(SINT aLevel)`; exact extracted source-body SHA-256 `f4833dee39b2041093f247a71b4f5367e6ebaff4f831b9fd8bad0b88cbf6b694`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=18, switch=2, for=3, while=3; named call tokens `BuildLevelSpecifics`, `CAtmospherics::ShutdownAll`, `CCONTROLLER::InactivityMeansQuitGame`, `CController::SetNonInteractiveSection`, `CVBufTexture::ClearOut`, `CalcRenderFrameFraction`, `Cleanup`, `DumpMemory`, `Exec`, `FOR_ALL_ITEMS_IN`, `FillOutEndLevelData`, `Flush`, `GetIntroFMV`, `GetLandscape`, `GetMapTex`, `GetSysTimeFloat`, `GetTime`, `GetTimeoutTime`, `GetToControl`, `GetUnitNB`, `HandleStreams`, `HasTimeoutExpired`, `Init`, `KillAllSamples` (+28 more tokens).
- Source-to-retail status: tracked `SOURCE_EXACT` class supplies named identity plus tracked source-body-agreement evidence. The packet/pristine checks below independently pin the retail target; this factory does not silently widen the tracked exactness beyond that evidence row.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-aligned mapping to CGame::RestartLoopRunLevel(SINT). Executes one restart-loop pass: load level/post-load, optional intro FMV, build level specifics, pre-run setup, per-frame loop while mQuit==QT_NONE via CGame__MainLoop, then cleanup/quit result propagation.”
- The displayed decompile is non-empty and SHA-256 `b62afdcc7f1f4875c6d414450cde4b8848ff6cfbe1da8fbc60490b6ade77a2f2`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 34 callee record(s), and 4 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless the value itself states a stronger measured fact:
- Session `batch-1`; question `contract-level-flow`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level100, level-opening-3m-v1-level110, level-opening-3m-v1-level200, level-opening-3m-v1-level201 …`.
- Session `batch-2`; question `contract-level-flow`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level300, level-opening-3m-v1-level311, level-opening-3m-v1-level312, level-opening-3m-v1-level321 …`.
- Session `batch-3`; question `contract-level-flow`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level421, level-opening-3m-v1-level422, level-opening-3m-v1-level431, level-opening-3m-v1-level432 …`.
- Session `batch-4`; question `contract-level-flow`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level524, level-opening-3m-v1-level600, level-opening-3m-v1-level611, level-opening-3m-v1-level612 …`.
- Session `batch-5`; question `contract-level-flow`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level732, level-opening-3m-v1-level741, level-opening-3m-v1-level742, level-opening-3m-v1-level800 …`.
- Session `batch-6`; question `contract-level-flow`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level856, level-opening-3m-v1-level857, level-opening-3m-v1-level858, level-opening-3m-v1-level859 …`.
- Session `batch-7`; question `contract-level-flow`; value: CORROBORATED live in every coverage session of batch; evidence `level-opening-3m-v1-level901, level-opening-3m-v1-level902, level-opening-3m-v1-level903, level-opening-3m-v1-level904 …`.
- Session `batch-8`; question `contract-level-flow`; value: corroborated in 1/4 coverage sessions; evidence `level521-native-20260802-0018-take4`.
- Session `batch-9`; question `contract-level-flow`; value: CORROBORATED live in every coverage session of batch; evidence `q-pilot-cov-l700-20260731, q-pilot-cov-l742-20260731, q-pilot-cov-l742-rep2-20260731`.
- Session `batch-10`; question `contract-level-flow`; value: no coverage collector output for this batch's sessions; evidence `batch carries no BEA.exe coverage bitmap (query/infra captures)`.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 19; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0046dc30.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `b62afdcc7f1f4875c6d414450cde4b8848ff6cfbe1da8fbc60490b6ade77a2f2`.
- Digest derivation: closure SHA-256 hashes canonical range text `0046dc30:0046e22a;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062c0f4` length 13 SHA-256 `d71996037c7732993f0f38e2c0213c04153b1ac0ff04e12bdb793f5bc7697675` value “autoexec.con”.
- Packet string ref `0x0062c104` length 16 SHA-256 `6d4c1a5c78fcda32b7589aae14bd8b6eab45017ef65620533a957b23fd53cbaa` value “dumptimerecords”.
- Packet string ref `0x0062c114` length 27 SHA-256 `f69569dfbe4575464d4d8cfb4622c6f43fbb3ca924e1b3d552943d4e0d8c1be4` value “Dump the game time records”.
- Packet string ref `0x0062c130` length 13 SHA-256 `9d19c8dd47747fc28acb00b577fc88960064042a5bd9d5287f10ce7173958947` value “Post Load %d”.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::RestartLoopRunLevel` line 1260 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/functions/game.cpp/CGame__RestartLoopRunLevel.md`, `reverse-engineering/binary-analysis/cgame-level-lifecycle-semantics-2026-08-11.tsv`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
