# CFrontEnd__DrawBar

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__DrawBar` at `0x00467ae0`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00467ae0`

## Identity
- Body `[0x00467ae0,0x00467bcf]`, 240 bytes, 83 closure instructions. Raw pristine-body SHA-256 `272fdb9c79428cc0af2eb3c138947a345c76cb30ed8607bc55e0cb543c4d534b`; closure range SHA-256 `f917ce5b0d9c2bcccb745f62d74e02773c4673c2ec846b99b249a9775c9a97f5`; packet range-plus-bytes SHA-256 `c86b3a4d2e7e7a1a585d1ea072ad6f4a60ee789a242e378ccaa8f13ce56994d5`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__DrawBar` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__DrawBar`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFrontEnd__DrawBar(void * this, float sx, float sy, float depth, int segment_count, uint argb, float scale)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFrontEnd__DrawBar(void * this, float sx, float sy, float depth, int segment_count, uint argb, float scale)
```
- Packet-declared parameter list: `void * this, float sx, float sy, float depth, int segment_count, uint argb, float scale`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0089d7ac`, `DAT_0089d7b0`, `DAT_0089d7b4`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `D3DStateCache__SetState114Raw` `0x00513930` ×4 site(s) (STATIC_DIRECT).
- Callee `CDXSurf__RenderSurface` `0x005563d0` ×1 site(s) (STATIC_DIRECT).
- Caller `CFEPLanguageTest__Render` `0x0051c280` ×1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `1073-1096` defines `CFrontEnd::DrawBar` as `void	CFrontEnd::DrawBar(float sx, float sy, float z, SINT segs, DWORD col, float scale)`; exact extracted source-body SHA-256 `4ac4c20f9dfda8e5bd70d65bc87b702d5b3f3d4557116a90275851c57b066552`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=2, switch=0, for=1, while=0; named call tokens `CSPRITERENDERER::DrawColouredSprite`, `GetTexture`, `STS`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave467 correction: Frontend header/bar strip helper matching source CFrontEnd::DrawBar stack cleanup and parameter order for start position, depth, segment count, ARGB color, and scale; retail body selects left/center/right bar textures while rendering segment_count + 2 sprites. Static retail-binary/source-bridge evidence only; exact texture ids, runtime visual behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `6dadc4e29fc36bac9e8ae5e95bf70f3fa92a24f7bf2883d166664796d65d1232`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 1 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 21; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00467ae0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `6dadc4e29fc36bac9e8ae5e95bf70f3fa92a24f7bf2883d166664796d65d1232`.
- Digest derivation: closure SHA-256 hashes canonical range text `00467ae0:00467bcf;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::DrawBar` line 1073 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__DrawBar.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
