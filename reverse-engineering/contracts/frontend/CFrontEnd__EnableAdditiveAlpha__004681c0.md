# CFrontEnd__EnableAdditiveAlpha

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__EnableAdditiveAlpha` at `0x004681c0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004681c0`

## Identity
- Body `[0x004681c0,0x004681dc]`, 29 bytes, 9 closure instructions. Raw pristine-body SHA-256 `24bd8cb6b01e3a9e685df2434e04f436f26ade0d938da095cf0199bde0edeb93`; closure range SHA-256 `57b5c9e2d9b2c74a85ab8f32aac234aaee5ebfaed87d7f348d7dc74786d90a37`; packet range-plus-bytes SHA-256 `d1574466379bad07e0a99dd3ccd29e62e2f6258f8e69cfc176984e14ccfd2c7e`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__EnableAdditiveAlpha` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__EnableAdditiveAlpha`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFrontEnd__EnableAdditiveAlpha(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFrontEnd__EnableAdditiveAlpha(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `RenderState_Set` `0x00513bc0` ×2 site(s) (STATIC_DIRECT).
- Caller `CFrontEnd__RenderOverlayEffects` `0x00452df0` ×1 site(s) (instruction-flow).
- Caller `CFEPMultiplayerStart__SubObj8848__Render` `0x00459ee0` ×1 site(s) (instruction-flow).
- Caller `CFEPLevelSelect__Render` `0x00460b40` ×1 site(s) (instruction-flow).
- Caller `CFEPMain__Render` `0x00462d40` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `1231-1235` defines `CFrontEnd::EnableAdditiveAlpha` as `void	CFrontEnd::EnableAdditiveAlpha()`; exact extracted source-body SHA-256 `6cde1a8fec36a58464150526a5b3773101ed415b31fbd1ff76ce54e358c77978`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=0, switch=0, for=0, while=0; named call tokens `SRS`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave467 correction: Frontend blend-state helper matching source CFrontEnd::EnableAdditiveAlpha, setting source and destination blend to additive/one-style values in retail render state. Static retail-binary/source-bridge evidence only; exact render-state enum names, runtime blending behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `0ee17ce914af830c302f02a62ef800c15e5b48f091aeeec67db9852f4e69de22`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 4 caller record(s), 1 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 23; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x004681c0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `0ee17ce914af830c302f02a62ef800c15e5b48f091aeeec67db9852f4e69de22`.
- Digest derivation: closure SHA-256 hashes canonical range text `004681c0:004681dc;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::EnableAdditiveAlpha` line 1231 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__EnableAdditiveAlpha.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
