# CFrontEnd__SetLanguage

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__SetLanguage` at `0x00466ab0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00466ab0`

## Identity
- Body `[0x00466ab0,0x00466ad6]`, 39 bytes, 12 closure instructions. Raw pristine-body SHA-256 `35bb38bf7ae806ca9a8875378eac85ec21c0360c4a5d28167070941bf8a1eec6`; closure range SHA-256 `09f4a57f05559426ef47c628d66811c57a7a2b45d6e1173b02ba9c383b008570`; packet range-plus-bytes SHA-256 `61f4882811db2d42793b2807f9e3e823302377f6fb937263148fb17f2cc7d838`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__SetLanguage` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__SetLanguage`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFrontEnd__SetLanguage(void * this, int language_index)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFrontEnd__SetLanguage(void * this, int language_index)
```
- Packet-declared parameter list: `void * this, int language_index`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `CText__CopyFrom` `0x004f2660` ×1 site(s) (STATIC_DIRECT).
- Callee `CFEPOptions__Cleanup` `0x0051f8e0` ×1 site(s) (STATIC_DIRECT).
- Caller `OptionsTail_Read` `0x00420d70` ×1 site(s) (instruction-flow).
- Caller `CFEPMain__ButtonPressed` `0x00462250` ×2 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `557-560` defines `CFrontEnd::SetLanguage` as `void	CFrontEnd::SetLanguage(SINT l)`; exact extracted source-body SHA-256 `ee57a867f8b929d9df131c14a861abe95057e01ea7fbfd9e9c711ab61d5d769f`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=0, switch=0, for=0, while=0; named call tokens `Copy`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Signature/source-parity hardening: CFrontEnd::SetLanguage takes one stack language_index, cleans up frontend options, and copies the selected text set into g_Text via CText__CopyFrom before returning with RET 0x4. Static source/decompile evidence only; runtime localization behavior remains unproven.”
- The displayed decompile is non-empty and SHA-256 `766ca5c8e83b8891bb0cc5aaa8b20710912b9ca0318e0cfc03bfc2c922de07b3`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 2 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 12; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00466ab0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `766ca5c8e83b8891bb0cc5aaa8b20710912b9ca0318e0cfc03bfc2c922de07b3`.
- Digest derivation: closure SHA-256 hashes canonical range text `00466ab0:00466ad6;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::SetLanguage` line 557 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__SetLanguage.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
