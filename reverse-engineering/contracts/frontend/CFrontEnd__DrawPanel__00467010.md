# CFrontEnd__DrawPanel

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static contract for `CFrontEnd__DrawPanel` at `0x00467010`; packet-described behavior is retained with explicit unknowns and no promotion claim.
Evidence: MEASURED — READY packet/decompile, structured edges, closure identity, and independently recomputed pristine body bytes; runtime and source limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/FrontEnd.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00467010`

## Identity
- Body `[0x00467010,0x004670a4]`, 149 bytes, 47 closure instructions. Raw pristine-body SHA-256 `c3298284d6b8cedd00970bfecd632fab397f8f40febf42b1a5ba49e7fa7592ef`; closure range SHA-256 `5d682ea4d0e0ca5b3f01319d6c38821691e0276f1918ea1e0a69f8ca800ad02a`; packet range-plus-bytes SHA-256 `f9f9609a60f59dd5f9353c68cb58e127aa1eacccef86c923cb9e5a57693a2cda`. All three were independently recomputed over the exact single contiguous inclusive range.
- Canonical name `CFrontEnd__DrawPanel` comes from the current closure/register row. Packet label matches canonical tracked name `CFrontEnd__DrawPanel`.
- Packet name source `USER_DEFINED` and signature source `USER_DEFINED` are counted provenance, not semantic proof.
- Campaign grade `C1_CANDIDATE_PARTIAL` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFrontEnd__DrawPanel(void * this, float tlx, float tly, float brx, float bry, float depth, uint argb)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFrontEnd__DrawPanel(void * this, float tlx, float tly, float brx, float bry, float depth, uint argb)
```
- Packet-declared parameter list: `void * this, float tlx, float tly, float brx, float bry, float depth, uint argb`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Callee/side-effect completion and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_0089d8ec`. Read/write direction for each symbol is not independently instruction-verified in this factory draft.

## Callees relied on / callers
- Callee `D3DStateCache__SetState114Raw` `0x00513930` ×4 site(s) (STATIC_DIRECT).
- Callee `CDXSurf__RenderSurface` `0x005563d0` ×1 site(s) (STATIC_DIRECT).
- Caller `CFrontEnd__RenderAndProcessModalPanel` `0x0044d6f0` ×3 site(s) (instruction-flow).
- Caller `FUN_004595b0` `0x004595b0` ×1 site(s) (instruction-flow).
- Caller `CFEPDirectory__RenderSaveFileList` `0x0051ae70` ×1 site(s) (instruction-flow).
- Caller `CFEPVirtualKeyboard__DrawPanel` `0x00521260` ×2 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first owner/target branch: `references/Onslaught/FrontEnd.cpp` lines `749-759` defines `CFrontEnd::DrawPanel` as `void	CFrontEnd::DrawPanel(float tlx, float tly, float brx, float bry, float z, DWORD col)`; exact extracted source-body SHA-256 `b9c36ec9297a29f83b134d36eab69bf50a1b4c47484b17e89f12559816a4fa50`.
- Source algorithm skeleton (mechanical, not a retail claim): control counts if=0, switch=0, for=0, while=0; named call tokens `CSPRITERENDERER::DrawColouredSprite`, `GetTexture`, `STS`, `SetFogEnabled`.
- Source-to-retail status: `SOURCE_ANALOG` is architecture/name intent only. Every source branch, call, field name, and ordering rule remains a hypothesis until the retail packet/body below independently agrees.
- Source-vs-retail delta/unknown boundary: no unlisted equivalence is assumed; platform conditionals, concrete layouts, omitted/inlined calls, constants, failure paths, and runtime causality remain open unless the packet comment/decompile or cited tracked evidence states the same fact.
- Existing packet analyst comment (quoted as bounded packet evidence, not silently upgraded): “Wave467 correction: Frontend blank-panel helper matching source CFrontEnd::DrawPanel stack cleanup and parameter order for bounds, depth, and ARGB color; retail body clamps texture addressing, renders the blank panel surface, then restores wrapping. Static retail-binary/source-bridge evidence only; exact texture ids, render-state side effects, runtime visual behavior, and rebuild parity remain unproven.”
- The displayed decompile is non-empty and SHA-256 `c4bca9ea952689012ed997500b979a31ccecd2398b91acca75d52ab199f87288`. This factory draft preserves that packet-described control/side-effect intent but does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory for this body: 4 caller record(s), 2 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation failure, indirect-call failure, NaN/overflow behavior, and rollback semantics are not_determinable as a class from the packet metadata. The decompile and quoted comment are the bounded static evidence; any missing branch-level edge contract remains an open question rather than an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer-task authority: task `t_efc238f0`, cohort 8 immutable manifest SHA-256 `83ef22fcc410af7ab26413e27b32248eed601953dc07b220412c513a08f4536b`, row 17; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and proposed promotion false. The task comment/independent-review receipts are the durable manifest authority; no writer-local scratch path is claimed as tracked evidence.
- Packet `D:/packet-runs/wave2-contracts-20260822/packet-0x00467010.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`); packet decompile SHA-256 `c4bca9ea952689012ed997500b979a31ccecd2398b91acca75d52ab199f87288`.
- Digest derivation: closure SHA-256 hashes canonical range text `00467010:004670a4;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `COVERED` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs: empty.
- Source crosswalk: `references/Onslaught/FrontEnd.cpp` `CFrontEnd::DrawPanel` line 749 (`SOURCE_ANALOG`), evidence `reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__DrawPanel.md`. This is source/name architecture evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact identity, contiguous pristine bytes, digest derivations, signature text, and structured edge inventory are reconciled; field-level semantics and runtime causality remain bounded to the packet/decompile and any cited source/TTD rows. A packet/canonical name discrepancy forces confidence 0. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
