# CFrontEnd__RenderOverlayEffects

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__RenderOverlayEffects` at `0x00452df0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00452df0`

## Identity
- Body `[0x00452df0,0x00452fc6]`, 471 bytes, 127 closure instructions. Raw pristine-body SHA-256 `780e987a643dfecc183711c03fac662280735d00eea9f26e663e1cf78d524c84`; closure range SHA-256 `c6691a79c4a0f1ec188a3dc1cbd29ea3ec65bdb1d1d5fac86c94e40d9b30a9ae`; packet range-plus-bytes SHA-256 `46361a7ffa12a1e13d5f5334588c789134640b54710eb72c8c25cd58fecf5c2e`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__RenderOverlayEffects` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__RenderOverlayEffects`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__stdcall` for `void __stdcall CFrontEnd__RenderOverlayEffects(float transition)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __stdcall CFrontEnd__RenderOverlayEffects(float transition)
```
- Packet-declared parameter list: `float transition`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0089d758`, `DAT_0089d7fc`, `DAT_0089d890`, `DAT_009c65c0`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CFrontEnd__EnableAdditiveAlpha` `0x004681c0` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__EnableModulateAlpha` `0x004681e0` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__GetShadowOffsetX` `0x00468730` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__GetShadowOffsetY` `0x00468750` ×1 site(s) (STATIC_DIRECT).
- Callee `RenderState_Set` `0x00513bc0` ×2 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__ApplyPendingRenderState` `0x00550d50` ×2 site(s) (STATIC_DIRECT).
- Callee `CDXSurf__RenderSurface` `0x005563d0` ×4 site(s) (STATIC_DIRECT).
- Callee `CRT__FpuIntrinsicDispatch2Thunk` `0x0055e3ea` ×1 site(s) (STATIC_DIRECT).
- Caller `CFEPBEConfig__Render` `0x004505b0` ×1 site(s) (instruction-flow).
- Caller `CFEPBriefing__Render` `0x00451d50` ×1 site(s) (instruction-flow).
- Caller `CFEPDebriefing__Render` `0x00456dd0` ×1 site(s) (instruction-flow).
- Caller `CFEPDevSelect__VFunc_5_00458ee0` `0x00458ee0` ×1 site(s) (instruction-flow).
- Caller `CFEPMultiplayerStart__SubObj8848__Render` `0x00459ee0` ×1 site(s) (instruction-flow).
- Caller `CFEPGoodies__Render` `0x0045e0d0` ×1 site(s) (instruction-flow).
- Caller `CFEPLevelSelect__Render` `0x00460b40` ×1 site(s) (instruction-flow).
- Caller `CFEPLoadGame__Render` `0x00461d90` ×1 site(s) (instruction-flow).
- Caller `CFEPSaveGame__Render` `0x00464a80` ×1 site(s) (instruction-flow).
- Caller `CFEPCredits__Render` `0x0051a8b0` ×1 site(s) (instruction-flow).
- Caller `CFEPDirectory__Render` `0x0051b460` ×2 site(s) (instruction-flow).
- Caller `CFEPLanguageTest__Render` `0x0051c280` ×1 site(s) (instruction-flow).
- Caller `CFEPMultiplayer__VFunc_5_0051d160` `0x0051d160` ×1 site(s) (instruction-flow).
- Caller `CFEPMultiplayerStart__Render` `0x0051e1b0` ×1 site(s) (instruction-flow).
- Caller `CFEPOptions__Update` `0x0051f700` ×1 site(s) (instruction-flow).
- Caller `CFEPScreenPos__Render` `0x0051fb90` ×1 site(s) (instruction-flow).
- Caller `CFEPVirtualKeyboard__Render` `0x00521100` ×2 site(s) (instruction-flow).
- Caller `CFEPWingmen__Render` `0x00522190` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Frontend overlay/effect renderer with float intensity input; draws animated surfaces and updates render-state blend setup. Called by multiple FE render paths (credits, directory, language test, level select).”
- The displayed decompile is non-empty and SHA-256 `8b86a4985d5ea9610e8d775cf6b26d9883d2784fcc293974c06ca297ad799f62`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 18 caller record(s), 8 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 7; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00452df0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `8b86a4985d5ea9610e8d775cf6b26d9883d2784fcc293974c06ca297ad799f62`.
- Digest derivation: closure SHA-256 hashes canonical range text `00452df0:00452fc6;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
