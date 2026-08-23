# CGame__PostLoadProcess

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CGame__PostLoadProcess` at `0x0046d040`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/game.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046d040`

## Identity
- Body `[0x0046d040,0x0046d264]`, 549 bytes, 139 closure instructions. Raw pristine-body SHA-256 `0903b78f65a5e2807e9bee27ad83555063cc2dd62cbe49419193dae0d2ed1895`; closure range SHA-256 `e6c4416c08deae428f43f4ae0899d847e5a359b2517c108c86049c1baf1d80e8`; packet range-plus-bytes SHA-256 `89cceaa5b058d3ee9c5ad1cf15767cbc59f86042934b6cc14a1a2db57bf93740`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CGame__PostLoadProcess` comes from the current closure/register row. Packet label matches canonical tracked name `CGame__PostLoadProcess`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `int __fastcall CGame__PostLoadProcess(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __fastcall CGame__PostLoadProcess(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- Decompile symbol references: `DAT_00662f34`, `DAT_00662f36`, `DAT_00662f4c`, `DAT_00663498`, `DAT_0066f580`, `DAT_006fadc8`, `DAT_00704200`, `DAT_00855100`, `DAT_00855108`, `DAT_008aa4e8`, `s_No_start_position_for_player___c_0062c008`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `Atmospherics__Init` `0x00404a00` ×1 site(s) (STATIC_DIRECT).
- Callee `Atmospherics__ResetAndUpdate` `0x00404b90` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__SetLoadingFraction` `0x0042cf70` ×5 site(s) (STATIC_DIRECT).
- Callee `CController__StartRecording` `0x0042d8a0` ×1 site(s) (STATIC_DIRECT).
- Callee `CController__StartPlayback` `0x0042d8c0` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__Printf` `0x00441740` ×1 site(s) (STATIC_DIRECT).
- Callee `CHud__PostLoadProcess` `0x00481af0` ×1 site(s) (STATIC_DIRECT).
- Callee `CInitThing__ctor` `0x0048dcf0` ×1 site(s) (STATIC_DIRECT).
- Callee `CHeightField__BuildCellMinMaxHeightTable` `0x00490e30` ×1 site(s) (STATIC_DIRECT).
- Callee `CMapWho__Sort` `0x004926e0` ×1 site(s) (STATIC_DIRECT).
- Callee `OID__CreateObject` `0x004bf090` ×1 site(s) (STATIC_DIRECT).
- Callee `CPlayer__Init` `0x004d28a0` ×1 site(s) (STATIC_DIRECT).
- Callee `CPlayer__AssignBattleEngine` `0x004d3080` ×2 site(s) (STATIC_DIRECT).
- Caller `CGame__RestartLoopRunLevel` `0x0046dc30` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `764-850` defines `CGame::PostLoadProcess` as `BOOL CGame::PostLoadProcess()`; exact extracted source-body SHA-256 `ae5adcb2d063ff5af1be58e7d061de2e7dfe654452dc4e05ae12dbcd91d148f5`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=6, switch=0, for=2, while=0; named call tokens `AddMessage`, `AssignBattleEngine`, `CAtmospherics::InitialiseAll`, `CAtmospherics::SetupAll`, `CThingCamera`, `FVector`, `First`, `GetBattleEngine`, `GetNumber`, `GetPlayerNumber`, `GetPlayerObject`, `GetStartNB`, `Init`, `InitDamageSystem`, `InitQuickCollisionMap`, `Next`, `PlayFullscreen`, `SetCurrentCamera`, `SetLoadingFraction`, `SortEntries`, `SpawnThing`, `StartPlayback`, `StartRecording`, `new`.
- Source-to-retail status: tracked `SOURCE_EXACT` class supplies named identity plus tracked source-body-agreement evidence. The packet/pristine checks below independently pin the retail target; this factory does not silently widen the tracked exactness beyond that evidence row.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Source-aligned mapping to CGame::PostLoadProcess(). Runs post-load world setup: validates post-load state, initializes/resets atmospherics, resolves per-player start positions, sorts map-who state, and returns TRUE/FALSE for post-load readiness.”
- The displayed decompile is non-empty and SHA-256 `fdf98ec28111ca43d32c0c7e2c12667e8fb2e754aeabd44ceb69550b7883dcee`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 13 callee record(s), and 1 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 17; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x0046d040.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `fdf98ec28111ca43d32c0c7e2c12667e8fb2e754aeabd44ceb69550b7883dcee`.
- Digest derivation: closure SHA-256 hashes canonical range text `0046d040:0046d264;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062c008` length 54 SHA-256 `77b891cf5fd6fe2331f0bf89e306f5f0eb4978ec4787e670e361bba8784edf2d` value “No start position for player - creating a default one”.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::PostLoadProcess` line 764 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/functions/game.cpp/CGame__PostLoadProcess.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
