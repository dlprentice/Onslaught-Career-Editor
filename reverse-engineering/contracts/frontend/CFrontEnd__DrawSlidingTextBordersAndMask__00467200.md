# CFrontEnd__DrawSlidingTextBordersAndMask

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__DrawSlidingTextBordersAndMask` at `0x00467200`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00467200`

## Identity
- Body `[0x00467200,0x00467964]`, 1893 bytes, 532 closure instructions. Raw pristine-body SHA-256 `b6b40ef59f3db173b01ce26a3e27fe0fbb1fa3a5a115cbd7344e2c008f4f7f40`; closure range SHA-256 `db97e82ea01d3c10ca72b866c845c3d58068565f794e9734faddde1b743dc629`; packet range-plus-bytes SHA-256 `2e8f02b4f8c52ad4d7873c154cd2c52d598d09dd6aa889f5281140c759d617e3`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__DrawSlidingTextBordersAndMask` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__DrawSlidingTextBordersAndMask`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFrontEnd__DrawSlidingTextBordersAndMask(void * this, float transition, int dest_page)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFrontEnd__DrawSlidingTextBordersAndMask(void * this, float transition, int dest_page)
```
- Packet-declared parameter list: `void * this, float transition, int dest_page`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0089d834`, `DAT_0089d8dc`, `DAT_0089d8e0`, `DAT_0089d8e4`, `DAT_009c65c0`, `_DAT_008a9570`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `FEPShared__RenderSelectionBrackets` `0x00452fd0` ×1 site(s) (STATIC_DIRECT).
- Callee `FrontEnd__HasStandardSlidingTextBordersAndMaskPage` `0x004679a0` ×1 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetState114Raw` `0x00513930` ×4 site(s) (STATIC_DIRECT).
- Callee `RenderState_Set` `0x00513bc0` ×4 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__ApplyPendingRenderState` `0x00550d50` ×2 site(s) (STATIC_DIRECT).
- Callee `CDXSurf__RenderSurface` `0x005563d0` ×6 site(s) (STATIC_DIRECT).
- Caller `CFEPDevSelect__VFunc_5_00458ee0` `0x00458ee0` ×1 site(s) (instruction-flow).
- Caller `CFEPGoodies__Render` `0x0045e0d0` ×1 site(s) (instruction-flow).
- Caller `CFEPLevelSelect__Render` `0x00460b40` ×1 site(s) (instruction-flow).
- Caller `CFEPLoadGame__Render` `0x00461d90` ×1 site(s) (instruction-flow).
- Caller `CFEPSaveGame__Render` `0x00464a80` ×1 site(s) (instruction-flow).
- Caller `CFEPDirectory__RenderSaveFileList` `0x0051ae70` ×1 site(s) (instruction-flow).
- Caller `CFEPLanguageTest__Render` `0x0051c280` ×1 site(s) (instruction-flow).
- Caller `CFEPMultiplayer__VFunc_5_0051d160` `0x0051d160` ×1 site(s) (instruction-flow).
- Caller `CFEPOptions__Update` `0x0051f700` ×1 site(s) (instruction-flow).
- Caller `CFEPScreenPos__Render` `0x0051fb90` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `807-1020` defines `CFrontEnd::DrawSlidingTextBordersAndMask` as `void CFrontEnd::DrawSlidingTextBordersAndMask(float transition, EFrontEndPage dest)`; exact extracted source-body SHA-256 `a78d9046226f2a64c23c414959d64c9175d250ee4bd828356d8373765b381bd1`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=25, switch=0, for=0, while=0; named call tokens `Apply`, `BlendAlpha`, `BlendAlpha2`, `CSPRITERENDERER::DrawColouredSprite`, `CosResize`, `FO`, `GetCommonPage`, `GetCurrentPage`, `GetShadowOffsetX`, `GetShadowOffsetY`, `GetTexture`, `GetTransitionFrom`, `GetTransitionTo`, `MakeAlpha`, `Range`, `RangeTransition`, `RenderSmallForsetiText`, `Rotate2D`, `SRS`, `STS`, `SetFogEnabled`, `check_draw_twice`, `edge`, `got_standard_SlidingTextBordersAndMask`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Signature/source-parity hardening: CFrontEnd::DrawSlidingTextBordersAndMask takes transition and dest_page, uses the source static got_standard_SlidingTextBordersAndMask page predicate, and calls FEPShared__RenderSelectionBrackets while shaping page-transition masks. Static source/decompile evidence only; runtime frontend rendering remains unproven.”
- The displayed decompile is non-empty and SHA-256 `0e0a1162ff89c5f610d6393aa755819939e8df3c82e8b470ee9b9f5af3084d40`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 10 caller record(s), 6 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 19; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00467200.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `0e0a1162ff89c5f610d6393aa755819939e8df3c82e8b470ee9b9f5af3084d40`.
- Digest derivation: closure SHA-256 hashes canonical range text `00467200:00467964;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::DrawSlidingTextBordersAndMask` line 807 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__DrawSlidingTextBordersAndMask.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
