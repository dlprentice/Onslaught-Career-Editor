# CFrontEnd__DrawBox

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__DrawBox` at `0x00466e70`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00466e70`

## Identity
- Body `[0x00466e70,0x00467009]`, 410 bytes, 141 closure instructions. Raw pristine-body SHA-256 `e1fc225168fb68921f21284c71828cc8ed9704ba42ac4aef454a79617d3ac938`; closure range SHA-256 `a04bc6ffab28821c231af95bb3207eb2ca7dd3fff734205984cc7c44980f38e2`; packet range-plus-bytes SHA-256 `92c7ab658099c570159746702d631f32c0cbca80cbab1f9328283306f3c9f686`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__DrawBox` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__DrawBox`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFrontEnd__DrawBox(void * this, float tlx, float tly, float brx, float bry, uint argb, float width, float depth)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFrontEnd__DrawBox(void * this, float tlx, float tly, float brx, float bry, uint argb, float width, float depth)
```
- Packet-declared parameter list: `void * this, float tlx, float tly, float brx, float bry, uint argb, float width, float depth`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0089d7a8`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `CDXSurf__RenderSurface` `0x005563d0` ×4 site(s) (STATIC_DIRECT).
- Caller `CFrontEnd__RenderAndProcessModalPanel` `0x0044d6f0` ×1 site(s) (instruction-flow).
- Caller `FUN_004595b0` `0x004595b0` ×1 site(s) (instruction-flow).
- Caller `CFEPDirectory__RenderSaveFileList` `0x0051ae70` ×3 site(s) (instruction-flow).
- Caller `CFEPVirtualKeyboard__DrawPanel` `0x00521260` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `737-743` defines `CFrontEnd::DrawBox` as `void	CFrontEnd::DrawBox(float tlx, float tly, float brx, float bry, DWORD col, float width, float depth)`; exact extracted source-body SHA-256 `427fcd169e60f9ea17b4257a086c1f5bd979a77f288158c717eb693e27e3539d`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=0, switch=0, for=0, while=0; named call tokens `DrawLine`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave467 correction: Frontend box outline helper matching source CFrontEnd::DrawBox stack cleanup and parameter order for top-left/bottom-right bounds, ARGB color, width, and depth; retail body inlines four line-sprite draws. Static retail-binary/source-bridge evidence only; exact texture ids, render-state side effects, runtime visual behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `d645d1c252fabea6a49c6a35529685360cb26f6062450da80ddce3f30bea9955`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 4 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 16; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00466e70.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `d645d1c252fabea6a49c6a35529685360cb26f6062450da80ddce3f30bea9955`.
- Digest derivation: closure SHA-256 hashes canonical range text `00466e70:00467009;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::DrawBox` line 737 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__DrawBox.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
