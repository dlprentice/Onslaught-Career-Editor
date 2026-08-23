# CFrontEnd__RenderVideoQuadScaledToWindow

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__RenderVideoQuadScaledToWindow` at `0x00452ce0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00452ce0`

## Identity
- Body `[0x00452ce0,0x00452d9b]`, 188 bytes, 49 closure instructions. Raw pristine-body SHA-256 `95f31b479669500a0471b342f7de6a2be9d02c38183cf7334a39fb6d1b15e668`; closure range SHA-256 `f1afff2be3ea4f3ff28576904b6a7cc1951ce5151bf321b8fdac6e52a850a7ed`; packet range-plus-bytes SHA-256 `254fc7e56bc5a1bebad77d57c9bec03ac93e3ba8924d6d182d75dcd3d8e090c0`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__RenderVideoQuadScaledToWindow` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__RenderVideoQuadScaledToWindow`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__stdcall` for `void __stdcall CFrontEnd__RenderVideoQuadScaledToWindow(float scale, int argb, float center_x, float center_y)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __stdcall CFrontEnd__RenderVideoQuadScaledToWindow(float scale, int argb, float center_x, float center_y)
```
- Packet-declared parameter list: `float scale, int argb, float center_x, float center_y`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0089d91c`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `D3DStateCache__SetStateCached` `0x00513820` ×1 site(s) (STATIC_DIRECT).
- Callee `PLATFORM__GetWindowWidth` `0x00515940` ×2 site(s) (STATIC_DIRECT).
- Callee `PLATFORM__GetWindowHeight` `0x00515b00` ×2 site(s) (STATIC_DIRECT).
- Callee `CDXFrontEndVideo__Render` `0x00541790` ×1 site(s) (STATIC_DIRECT).
- Caller `CFEPMultiplayerStart__SubObj8848__RenderPreCommon` `0x00459e50` ×1 site(s) (instruction-flow).
- Caller `CFEPMain__RenderPreCommon` `0x00462b70` ×1 site(s) (instruction-flow).
- Caller `CFrontEnd__RenderPreCommonFade` `0x004679e0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Signature/comment correction: frontend video-quad render helper. It resolves default center coordinates from PLATFORM window dimensions when the sentinel center is passed, sets D3D render state, scales width/height against the window, and calls CDXFrontEndVideo__Render with the ARGB value. Static retail evidence only; exact source method identity, runtime rendering behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `d1849191607aac98729a0da3a80d97d692188ddf66f9645baa788300bc7b75a7`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 3 caller record(s), 4 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 6; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00452ce0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `d1849191607aac98729a0da3a80d97d692188ddf66f9645baa788300bc7b75a7`.
- Digest derivation: closure SHA-256 hashes canonical range text `00452ce0:00452d9b;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
