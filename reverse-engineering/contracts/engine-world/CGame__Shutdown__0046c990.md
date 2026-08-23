# CGame__Shutdown

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CGame__Shutdown` at `0x0046c990`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/game.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0046c990`

## Identity
- Body `[0x0046c990,0x0046ca6b]`, 220 bytes, 56 closure instructions. Raw pristine-body SHA-256 `a2e3b4e7b380794d87ae4602c347d3ef2fe5be229549a3e634ee56abb6d02858`; closure range SHA-256 `67654a071c14c4e09240941febc9352c7c0b287cbb439b42852207ec398ac4ab`; packet range-plus-bytes SHA-256 `6a7e013db616591309a5b1bd67ddc7676e55681cd67959c8932be6dc3f70fa47`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CGame__Shutdown` comes from the current closure/register row. Packet label matches canonical tracked name `CGame__Shutdown`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CGame__Shutdown(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CGame__Shutdown(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00662dcc`, `DAT_00663498`, `DAT_00679fa8`, `DAT_006fadc8`, `DAT_0082b400`, `DAT_00855bb0`, `DAT_00889a48`, `DAT_0089c9a0`, `DAT_008aa4e8`, `DAT_009c4004`, `DAT_009c8010`, `s_Exiting_Level____0062bf0c`, `s_Freeing_Up_Level_Resources____0062bf20`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CConsole__ClearCommandAndVariableLists` `0x0042af20` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__Status` `0x0042b500` ×1 site(s) (STATIC_DIRECT).
- Callee `CConsole__StatusDone` `0x0042b800` ×1 site(s) (STATIC_DIRECT).
- Callee `CGame__RunOutroFMV` `0x0046d9f0` ×1 site(s) (STATIC_DIRECT).
- Callee `CGameInterface__Shutdown` `0x00472a50` ×1 site(s) (STATIC_DIRECT).
- Callee `CHud__ShutDown` `0x00481b00` ×1 site(s) (STATIC_DIRECT).
- Callee `CHeightField__ShutdownAndDestroyMixerMap` `0x00490f40` ×1 site(s) (STATIC_DIRECT).
- Callee `CMemoryHeap__SetMerge` `0x004a1ea0` ×2 site(s) (STATIC_DIRECT).
- Callee `CMesh__FreeUnusedAndReportLeaks` `0x004a5430` ×1 site(s) (STATIC_DIRECT).
- Callee `CMusic__Stop` `0x004bb490` ×1 site(s) (STATIC_DIRECT).
- Callee `CParticleManager__DestroyParticleSetList` `0x004cbff0` ×1 site(s) (STATIC_DIRECT).
- Callee `CSPtrSet__ClearAnyDynamicCreatedNodes` `0x004e5990` ×1 site(s) (STATIC_DIRECT).
- Callee `CStaticShadows__ClearAllShadowEntries` `0x004ebd10` ×1 site(s) (STATIC_DIRECT).
- Callee `CTexture__FreeLevelResources` `0x004f2b40` ×1 site(s) (STATIC_DIRECT).
- Callee `CWaypoint__CleanupEndLevelVBufTextures` `0x00501360` ×1 site(s) (STATIC_DIRECT).
- Callee `CEngine__SetRenderStateCached` `0x00513a50` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__Shutdown` `0x0053d3e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXImposter__ShutdownAll` `0x00542990` ×1 site(s) (STATIC_DIRECT).
- Callee `MEM_MANAGER__Cleanup` `0x00549270` ×1 site(s) (STATIC_DIRECT).
- Callee `DXParticleTexture__DestroyAll` `0x0054fee0` ×1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/game.cpp` lines `414-526` defines `CGame::Shutdown` as `void CGame::Shutdown()`; exact extracted source-body SHA-256 `4abb5b6ed5ca7422f41ab6caabef221bd2666eb4dd739a925ed54b37dac8a66d`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=2, switch=0, for=1, while=0; named call tokens `AddMessage`, `CIMPOSTER::ShutdownAll`, `CMESH::FreeLevelResources`, `CTEXTURE::FreeLevelResources`, `CVBufTexture::FreeLevelResources`, `Cleanup`, `ClearCommandsAndVariables`, `D3D_SetTexture`, `FindLargestFree`, `GenericSPtrSet::ClearAnyDynamicCreatedNodes`, `GetDefaultHeap`, `OutputBlocks`, `OutputMap`, `OutputStats`, `Reboot`, `RunOutroFMV`, `SAFE_RELEASE`, `SetLoading`, `SetLoadingFraction`, `SetMerge`, `ShutDown`, `Status`, `StatusDone`, `Stop` (+1 more tokens).
- Source-to-retail status: tracked `SOURCE_EXACT` class supplies named identity plus tracked source-body-agreement evidence. The packet/pristine checks below independently pin the retail target; this factory does not silently widen the tracked exactness beyond that evidence row.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave1003 CGame shutdown boundary recovery: recovered a missing Ghidra function object for source-aligned CGame::Shutdown at 0x0046c990. Static evidence: DATA vtable refs 0x005dbbbc and 0x005e50a4 point at this entry; the body stops music when CLIPARAMS.mMusic is non-zero, calls CHud__ShutDown, GAMEINTERFACE shutdown/reset paths, particle/static-shadow/imposter/engine/map/mesh/texture cleanup, memory-manager merge/cleanup, outro FMV handling, and console status/command cleanup before terminal 0x0046ca6b RET. Source parity: references/Onslaught/game.cpp:CGame::Shutdown. Static retail Ghidra evidence only; exact source-body identity, concrete CGame/HUD/engine layouts, runtime shutdown behavior, BEA patching, and rebuild parity remain separate proof.”
- The displayed decompile is non-empty and SHA-256 `b08dbdade08855e40b993b8e7c26062ada5067b09bb70926a980305e5b097fde`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 0 caller record(s), 20 callee record(s), and 2 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 7 immutable manifest SHA-256 `d2ac6ace069c4ff409cd9aaec49022fb08589f5637367a823baa4b65053cc9ef`, row 14; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x0046c990.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `b08dbdade08855e40b993b8e7c26062ada5067b09bb70926a980305e5b097fde`.
- Digest derivation: closure SHA-256 hashes canonical range text `0046c990:0046ca6b;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0062bf0c` length 17 SHA-256 `9194523bd203bad1805b448755a0727ca227b8a667fc6e046493aa519d68298f` value “Exiting Level...”.
- Packet string ref `0x0062bf20` length 30 SHA-256 `0d40425ab54adb084fab10326d48b92c78d1d5b0cfcf70bdf869a2fd7798cd7b` value “Freeing Up Level Resources...”.
- Source crosswalk: `references/Onslaught/game.cpp` `CGame::Shutdown` line 414 (`SOURCE_EXACT`), evidence `reverse-engineering/binary-analysis/functions/game.cpp/CGame__Shutdown.md`, `reverse-engineering/binary-analysis/cgame-level-lifecycle-semantics-2026-08-11.tsv`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
