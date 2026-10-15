# CFrontEnd__IsMouseInputReady

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__IsMouseInputReady` at `0x0044dea0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no current source-crosswalk row) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0044dea0`

## Identity
- Body `[0x0044dea0,0x0044debc]`, 29 bytes, 10 closure instructions. Raw pristine-body SHA-256 `85e0f467ce4c1eb884a2527982d87779a378aecf8801e67218f7624e9d3af945`; closure range SHA-256 `446b5a23c1ddee50d3fa7520e557605b463209ddacccdc35da6ee4d67f54953b`; packet range-plus-bytes SHA-256 `78b0f769b3df66bbfb5b31b802052e3ac57d820cc5d222b2fdc7400e0f7ea8d2`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__IsMouseInputReady` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__IsMouseInputReady`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__fastcall` for `bool __fastcall CFrontEnd__IsMouseInputReady(void * frontend)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
bool __fastcall CFrontEnd__IsMouseInputReady(void * frontend)
```
- Packet-declared parameter list: `void * frontend`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `bool`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented here.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `FEPShared__RenderContextHelpPrompt` `0x00453140` ×1 site(s) (instruction-flow).
- Caller `CFEPDebriefing__Render` `0x00456dd0` ×1 site(s) (instruction-flow).
- Caller `CFEPLevelSelect__UpdateMouseEdgeSlide` `0x0045d730` ×1 site(s) (instruction-flow).
- Caller `CFEPGoodies__Process` `0x0045d7e0` ×1 site(s) (instruction-flow).
- Caller `CFrontEnd__ReceiveButtonAction` `0x004669a0` ×1 site(s) (instruction-flow).
- Caller `CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture` `0x00469390` ×1 site(s) (instruction-flow).
- Caller `CFrontEnd__GetCursorStateInRect` `0x004693d0` ×1 site(s) (instruction-flow).
- Caller `CFrontEnd__GetClickStateInRect` `0x00469400` ×1 site(s) (instruction-flow).
- Caller `CFEPDirectory__GetCursorStateInRectAndConsumeIfMouseReady` `0x00469430` ×1 site(s) (instruction-flow).
- Caller `CMenuItemDropdown_T3_004a3c30` `0x004a3c30` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: the current source crosswalk has no pinned Stuart owner for this VA.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Signature hardening: mouse input ready predicate returns true when the frontend modal/input gate at +0x1f8c is active and modal/input type at +0x1f98 is nonzero. Exact field names, runtime frontend behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `e32dbeab4de8c586da41bcd2609a482cd6b36831c7348e5521fdbb1807590d23`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 10 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 5; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x0044dea0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `e32dbeab4de8c586da41bcd2609a482cd6b36831c7348e5521fdbb1807590d23`.
- Digest derivation: closure SHA-256 hashes canonical range text `0044dea0:0044debc;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
