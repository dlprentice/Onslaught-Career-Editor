# D3DStateCache__UseDefaultRenderState

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `D3DStateCache__UseDefaultRenderState` at `0x004eb1e0` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004eb1e0`

## Identity
- Body `[0x004eb1e0,0x004eb99c]`, 1981 bytes, 569 closure instructions. Raw pristine-body SHA-256 `bcad8f7a002abfae31c1ff466e794600a6716bf4e51fb4d930c4d7a094828dd0`; closure range SHA-256 `a89ef948119cb122303d5ec9c190d72cbe10ccf41a03636d88292a06b97f0df0`; packet range-plus-bytes SHA-256 `4cf8b30510d23917198704633bbeaebfe93cf5bd93ea988a41443aa1fd0e5d20`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `D3DStateCache__UseDefaultRenderState`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `389fad24a522dae42190670a9f69b1cea385c4c2bc084e23ea932c102bcfb204` and decompile SHA-256 `6c4761121efc0500dbff409487ade9c12d78e78d4aa5752bcadb5f47eaa6954b` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet field records `unknown` for `void D3DStateCache__UseDefaultRenderState(void)`. The packet analyst comment explicitly refutes the packet field's bare `(void)` form: `MOV ESI,ECX` and receiver restoration before member calls prove an ECX receiver. The bounded reconciled shape is thiscall (or ABI-equivalent fastcall) with only `this`; no applied-device formal is invented.

## Prototype and parameter semantics
```c
void __thiscall D3DStateCache__UseDefaultRenderState(void * this)
```
- Reconciled bounded ABI from the packet's own analyst comment: `void __thiscall D3DStateCache__UseDefaultRenderState(void * this)`. The packet field's declared `void D3DStateCache__UseDefaultRenderState(void)` remains preserved above as metadata, not asserted as true.

## Return value meaning
The reconciled bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00854e6c`, `DAT_00855bb0`, `DAT_00888b04`, `DAT_0089d680`, `DAT_009c65c0`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CEngine__SetVertexShaderPathEnabled` `0x004eba30` x1 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__ResetSentinelTable` `0x00513600` x1 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetStateRaw` `0x00513870` x35 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetState114Cached` `0x005138b0` x28 site(s) (STATIC_DIRECT).
- Callee `RenderState_SetRaw` `0x00513c20` x43 site(s) (STATIC_DIRECT).
- Callee `CEngine__SetVertexShadersEnabled` `0x00513ca0` x1 site(s) (STATIC_DIRECT).
- Callee `RenderState_SetAlphaRefRaw` `0x00513dd0` x1 site(s) (STATIC_DIRECT).
- Callee `RenderState_Set_23_8C_Compat` `0x00514030` x1 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetMipFilterByGlobalToggle` `0x00551420` x3 site(s) (STATIC_DIRECT).
- Callee `D3DStateCache__SetMipFilterLinear` `0x00551460` x1 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__SetProjectionDepthBiasIndex` `0x005514a0` x1 site(s) (STATIC_DIRECT).
- Caller `CConsole__RenderLoadingScreen` `0x0042c810` x1 site(s) (instruction-flow).
- Caller `CFEPGoodies__Render` `0x0045e0d0` x1 site(s) (instruction-flow).
- Caller `CGame__DrawDebugStuff` `0x00470650` x1 site(s) (instruction-flow).
- Caller `CDXEngine__PreRender` `0x0053e220` x1 site(s) (instruction-flow).
- Caller `CDXEngine__Render` `0x0053e2e0` x1 site(s) (instruction-flow).
- Caller `CDXFMV__VFunc_11_0053f190` `0x0053f190` x1 site(s) (instruction-flow).
- Caller `CDXFrontEnd__RenderStart` `0x00540f70` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “D3DStateCache default render-state reset (sentinel tables, optional vertex-shader disable, baseline SetRenderState sequence, fog/depth clamps, texture-stage defaults). Bare `RET`. Declared `void ...(void)` is false — prologue `MOV ESI,ECX` and later `MOV ECX,ESI` before member CALL prove ECX receiver. Shape is `__thiscall (void * this)` (or __fastcall equivalent; do not invent applied device formals). Static retail evidence only; exact state-table schema, runtime device UX, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `6c4761121efc0500dbff409487ade9c12d78e78d4aa5752bcadb5f47eaa6954b`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 7 caller record(s), 11 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `all level-openings`; question `corpus-open-core`; value: invariant across all 66 openings; 128,568 cumulative covered bytes; evidence `name=D3DStateCache__UseDefaultRenderState`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 6; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `389fad24a522dae42190670a9f69b1cea385c4c2bc084e23ea932c102bcfb204`, and packet decompile SHA-256 `6c4761121efc0500dbff409487ade9c12d78e78d4aa5752bcadb5f47eaa6954b`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004eb1e0:004eb99c;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
