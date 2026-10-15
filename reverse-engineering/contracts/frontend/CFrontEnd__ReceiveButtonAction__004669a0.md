# CFrontEnd__ReceiveButtonAction

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__ReceiveButtonAction` at `0x004669a0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004669a0`

## Identity
- Body `[0x004669a0,0x00466aa7]`, 264 bytes, 93 closure instructions. Raw pristine-body SHA-256 `97d63512c57dba2c901df2a86ffe0d4c0a8b860ee373b829a881974208e553db`; closure range SHA-256 `fbd4740a709f9cd4892e69e5ddd1fb393595db9f49254043bcfe0c4b02c43846`; packet range-plus-bytes SHA-256 `b6850b59c65319e5b8432b562b04f8ec4238a609655b0844556f85fa4feb7ac3`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__ReceiveButtonAction` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__ReceiveButtonAction`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFrontEnd__ReceiveButtonAction(void * this, void * from_controller, int button, float action_value)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFrontEnd__ReceiveButtonAction(void * this, void * from_controller, int button, float action_value)
```
- Packet-declared parameter list: `void * this, void * from_controller, int button, float action_value`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00675688`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CFrontEnd__HandleModalPanelButton` `0x0044dd60` ×1 site(s) (STATIC_DIRECT).
- Callee `CFrontEnd__IsMouseInputReady` `0x0044dea0` ×1 site(s) (STATIC_DIRECT).
- Caller `Input__DispatchClickInRect` `0x00523bc0` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `477-554` defines `CFrontEnd::ReceiveButtonAction` as `void	CFrontEnd::ReceiveButtonAction(CController* from_controller, int button, float val)`; exact extracted source-body SHA-256 `d199880e120af70df6a5ed8d304f98ac9f7cbfeeac4cea5b39ea749030c99ccd`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=11, switch=0, for=0, while=0; named call tokens `BeingDisplayed`, `ButtonPressed`, `GetPortFromController`, `Load`, `Log`, `Save`, `SetPage`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Name/signature/source-parity correction: CFrontEnd::ReceiveButtonAction-style vtable slot dispatches frontend button input from a controller pointer, captures player-0 on BUTTON_FRONTEND_MENU_SELECT 0x2c, routes BUTTON_FRONTEND_CHEAT 0x2d, and returns with RET 0x0c. Static source/decompile/vtable evidence only; runtime input behavior remains unproven.”
- The displayed decompile is non-empty and SHA-256 `139d602ed144cbf184c736860ba3987b90c5bdc3b92cad499c50148ccc602770`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 11; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x004669a0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `139d602ed144cbf184c736860ba3987b90c5bdc3b92cad499c50148ccc602770`.
- Digest derivation: closure SHA-256 hashes canonical range text `004669a0:00466aa7;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::ReceiveButtonAction` line 477 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__ReceiveButtonAction.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
