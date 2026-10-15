# CDXTrees__Render

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CDXTrees__Render` at `0x0055aa10` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0055aa10`

## Identity
- Body `[0x0055aa10,0x0055ae39]`, 1066 bytes, 316 closure instructions. Raw pristine-body SHA-256 `3109f13423c4816f16f50720e8be4ff9a021d895a4e1c09f14fdf9ba07839be7`; closure range SHA-256 `461517d75c196f516d3eacc26ecd46b492681130f92dd972d3efd00e506f6b0e`; packet range-plus-bytes SHA-256 `b8a29e3519938b099e2ea1a100cab34085b4e90914e200a9f5aea465f2f40ac7`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CDXTrees__Render`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `9d11cbd0296b296a43c7982702b092e14f7863a07098373366b0660ec795874b` and decompile SHA-256 `f555e84e466dceeacf7902f9dd7c48b71d26ade90cff35809fd61e6d747284f8` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CDXTrees__Render(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CDXTrees__Render(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_006fadc8`, `DAT_008554fc`, `DAT_00855bb0`, `DAT_0089c9a4`, `DAT_0089ce4c`, `DAT_008aa850`, `DAT_008aa854`, `DAT_008aa858`, `DAT_008aa85c`, `DAT_008aa860`, `DAT_008aa864`, `DAT_008aa868`, `DAT_008aa86c`, `DAT_008aa8b8`, `DAT_009c65c0`, `DAT_009c68ad`, `DAT_009c6910`, `DAT_009c73f0`, `DAT_009c73f4`, `DAT_009c73f8`, `DAT_009c73fc`, `DAT_009c7400`, `DAT_009c7404`, `DAT_009c7408`, `DAT_009c740c`, `DAT_009c7410`, `DAT_009cc160`, `DAT_009cc190`, `DAT_009cc194`, `DAT_009cc198`, `DAT_009cc19c`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CStaticShadows__SampleShadowHeightBilinear` `0x0047eb80` x1 site(s) (STATIC_DIRECT).
- Callee `CVBufTexture__RenderIndexed` `0x00500fa0` x1 site(s) (STATIC_DIRECT).
- Callee `CVBufTexture__RenderIndexedNoValidate` `0x005010e0` x1 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetStateCached` `0x00513820` x18 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetStateRaw` `0x00513870` x4 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetState114Raw` `0x00513930` x12 site(s) (STATIC_DIRECT).
- Callee `CEngine__SetRenderStateCached` `0x00513a50` x1 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetSlotMode4or5` `0x00513af0` x1 site(s) (STATIC_DIRECT).
- Callee `RenderState_Set` `0x00513bc0` x9 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__SetWorldMatrixElements` `0x00550ca0` x1 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__ApplyPendingRenderState` `0x00550d50` x2 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetMipFilterByGlobalToggle` `0x00551420` x1 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetMipFilterNone` `0x00551480` x1 site(s) (STATIC_DIRECT).
- Callee `CDXTexture__GetAnimatedFrame` `0x00558690` x1 site(s) (STATIC_DIRECT).
- Callee `CDXTrees__BuildTreeGeometry` `0x0055a420` x1 site(s) (STATIC_DIRECT).
- Caller `CDXEngine__Render` `0x0053e2e0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave618 CDXTrees head hardening: CDXEngine__Render callsite 0x0053e7c1 passes the global tree renderer in ECX. Body lazily calls CDXTrees__BuildTreeGeometry when this+0x08 is empty, copies world matrix state, binds the animated tree texture, applies alpha/render-state setup, renders the primary buffer with CVBufTexture__RenderIndexedNoValidate, optionally renders the secondary buffer when the sampled shadow-height delta exceeds the observed threshold, then restores render states. Static retail decompile/xref/instruction evidence only; exact render-state meanings, runtime vegetation/shadow output, BEA patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `f555e84e466dceeacf7902f9dd7c48b71d26ade90cff35809fd61e6d747284f8`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 15 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 24; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `9d11cbd0296b296a43c7982702b092e14f7863a07098373366b0660ec795874b`, and packet decompile SHA-256 `f555e84e466dceeacf7902f9dd7c48b71d26ade90cff35809fd61e6d747284f8`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0055aa10:0055ae39;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source crosswalk: no selected canonical or landed-expansion row for this VA.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
