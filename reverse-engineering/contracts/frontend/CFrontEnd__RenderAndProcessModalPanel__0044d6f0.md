# CFrontEnd__RenderAndProcessModalPanel

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__RenderAndProcessModalPanel` at `0x0044d6f0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0044d6f0`

## Identity
- Body `[0x0044d6f0,0x0044dd5b]`, 1644 bytes, 491 closure instructions. Raw pristine-body SHA-256 `54dd0228c9f18d3fcaca7d332e067eceb5d2cf4195cc8bc578d8125279e946c8`; closure range SHA-256 `813174225337c2d59b1b47252ce067bb92d3c8de68f1092608290549eee1dbd6`; packet range-plus-bytes SHA-256 `650339e8a05c7141d0104f574e81be268040312d86434d5fa8e242f4400477d8`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__RenderAndProcessModalPanel` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__RenderAndProcessModalPanel`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `void __fastcall CFrontEnd__RenderAndProcessModalPanel(void * frontend)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __fastcall CFrontEnd__RenderAndProcessModalPanel(void * frontend)
```
- Packet-declared parameter list: `void * frontend`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0088a0a8`, `DAT_0089d758`, `DAT_009c68ac`, `DAT_009c690d`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CFrontEnd__HandleModalPanelButton` `0x0044dd60` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXFont__DrawTextScaledWithShadow` `0x004659a0` ×3 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__DrawBox` `0x00466e70` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__DrawPanel` `0x00467010` ×3 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__DrawBarGraph` `0x004670b0` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__PlaySound` `0x00468770` ×1 site(s) (STATIC_DIRECT).
- Callee `FrontEndText__GetLocalizedOrFallbackTextByToken` `0x0046a2a0` ×7 site(s) (STATIC_DIRECT).
- Callee `CPlatform__Font` `0x00515a70` ×6 site(s) (STATIC_DIRECT).
- Callee `Input__GetClickStateInRect` `0x00523cc0` ×2 site(s) (STATIC_DIRECT).
- Callee `Input__GetCursorStateInRectAndConsume` `0x00523d40` ×1 site(s) (STATIC_DIRECT).
- Callee `CDXFont__GetTextExtent` `0x00540680` ×5 site(s) (STATIC_DIRECT).
- Caller `CFEPDevSelect__VFunc_5_00458ee0` `0x00458ee0` ×1 site(s) (instruction-flow).
- Caller `CFrontEnd__Render` `0x00468200` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Signature hardening: frontend modal panel renderer/input helper gates on +0x1f8c, calls DrawPanel-style panel/box/text/bar drawing paths, processes modal type state at +0x1f98, and calls CFrontEnd__HandleModalPanelButton for selection/cancel actions. Exact widget layout, runtime frontend behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `f75482b9e055804b1d1fc9b46aba0668bcfc1d771f40fc07d95d0bbc8b6f179c`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 2 caller record(s), 11 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 3; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x0044d6f0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `f75482b9e055804b1d1fc9b46aba0668bcfc1d771f40fc07d95d0bbc8b6f179c`.
- Digest derivation: closure SHA-256 hashes canonical range text `0044d6f0:0044dd5b;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: no row for this VA in the current tracked crosswalk.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
