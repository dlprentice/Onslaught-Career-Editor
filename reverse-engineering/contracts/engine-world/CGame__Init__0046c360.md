# CGame__Init

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CGame__Init` at `0x0046c360`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/game.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046c360`

## Identity
- Body `[0x0046c360,0x0046c42f]`, 208 bytes, 56 closure instructions. Raw pristine-body SHA-256 `0c4121bf33e06ed038278c6db7fd1b3ed9783399e0d75f146514afdb9bbca7f8`; closure range SHA-256 `5c04b0ef5e98defc4f517f023d162e1ecdba31f7c94459c81ce1d7912eaeba03`; packet range-plus-bytes SHA-256 `618ad9a12e96d0ff3d7e5a4fe9ed3e540dd68826f3cd560585d127441ae3f417`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CGame__Init` comes from the current closure/register row. Packet label matches canonical tracked name `CGame__Init`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `int __fastcall CGame__Init(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __fastcall CGame__Init(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00663498`, `DAT_00679fa8`, `DAT_006fadc8`, `DAT_0089c9a0`, `DAT_008aa4e8`, `DAT_009c7490`, `DAT_009c8010`, `s_Should_level_data_sizes_be_shown_0062bc48`, `s_Should_memory_deltas_be_shown__0062bc80`, `s_cg_showdatasizes_0062bc34`, `s_cg_showmemdeltas_0062bc6c`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CConsole__RegisterBuiltinCommands` `0x00429ef0` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__RegisterVariable` `0x0042b040` ×2 site(s) (STATIC_DIRECT).
- Callee `CGameInterface__ResetMenuState` `0x004729e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CHud__Init` `0x00481450` ×1 site(s) (STATIC_DIRECT).
- Callee `CHeightField__InitAndClearMapLoadFlags` `0x00490f10` ×1 site(s) (STATIC_DIRECT).
- Callee `CStaticShadows__Initialise` `0x004ebbc0` ×1 site(s) (STATIC_DIRECT).
- Callee `CTweakFLOAT__SetNumViewpoints` `0x00528b50` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__Init` `0x0053d5f0` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXImposter__InitGlobals` `0x005428d0` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__InitConsoleVar_UseRenderQueue` `0x005515a0` ×1 site(s) (STATIC_DIRECT).
- Caller `CGame__RunLevel` `0x0046e240` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `246-288` defines `CGame::Init` as `BOOL CGame::Init()`; exact extracted source-body SHA-256 `22a666f7c8cb15236daffa105571ffe7f0a03bcd85ad8b9c65befa783bf9d0e9`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=3, switch=0, for=0, while=0; named call tokens `CAtmospherics::InitialiseAll`, `CIMPOSTER::InitAll`, `InitDefaultCommands`, `Initialise`, `RegisterVariable`, `SetNumViewpoints`.
- Source-to-retail status: tracked `SOURCE_EXACT` class supplies named identity plus tracked source-body-agreement evidence. The packet/pristine checks below independently pin the retail target; this factory does not silently widen the tracked exactness beyond that evidence row.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `662-670` defines `CGame::InitOneOffResources` as `void	CGame::InitOneOffResources()`; exact extracted source-body SHA-256 `f0b28498d19c58eb81a88a4d3a0d8a0ac8732afab32a0c7b581661f2c5793221`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=0, switch=0, for=0, while=0; named call tokens `InitResources`, `SetLoadingFraction`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `674-680` defines `CGame::InitRestartResources` as `void	CGame::InitRestartResources()`; exact extracted source-body SHA-256 `3dede8ffe3dc00cf761c0e02b47e990646bb339ae643b8c47aaed7f632d3907e`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=0, switch=0, for=0, while=0; named call tokens `InitResources`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-aligned mapping to CGame::Init(). Performs core engine startup checks and subsystem initialization (ENGINE.Init, imposters, render queue, static shadows, GAMEINTERFACE/HUD init), registers memory-size debug CVars, and returns TRUE/FALSE for startup success.”
- The displayed decompile is non-empty and SHA-256 `8d887d11a7fe94a95041fe371cbc7d09f34de9e55fa352a03b8559b9354b6328`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 10 callee record(s), and 4 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `6737c4da288324f6bb1e0f6d5e4411a0158a9eda8dd878e05058b839108be98e`, row 13; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x0046c360.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `8d887d11a7fe94a95041fe371cbc7d09f34de9e55fa352a03b8559b9354b6328`.
- Digest derivation: closure SHA-256 hashes canonical range text `0046c360:0046c42f;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062bc34` length 17 SHA-256 `471377812847802524b660e566867a52257e7cf692218f901d50067a68b21743` value “cg_showdatasizes”.
- Packet string ref `0x0062bc48` length 34 SHA-256 `2b88de68c8a4dd7415baf095c33ec26331183dc35d1aad8e793714cbb4efaf7c` value “Should level data sizes be shown?”.
- Packet string ref `0x0062bc6c` length 17 SHA-256 `c831b9a60f9219501ab1987da159bbd09a98e5c3c1c37932ac3b6b846ec77987` value “cg_showmemdeltas”.
- Packet string ref `0x0062bc80` length 31 SHA-256 `ab7c5e02a30662aa072da3fe344ed4b8d93ec78e20599660cfc28919bdfe8564` value “Should memory deltas be shown?”.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::Init` line 246 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/functions/game.cpp/CGame__Init.md`, `reverse-engineering/binary-analysis/cgame-level-lifecycle-semantics-2026-08-11.tsv`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::InitOneOffResources` line 662 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::InitRestartResources` line 674 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
