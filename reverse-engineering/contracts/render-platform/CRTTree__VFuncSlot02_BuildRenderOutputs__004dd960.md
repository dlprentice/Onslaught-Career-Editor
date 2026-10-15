# CRTTree__VFuncSlot02_BuildRenderOutputs

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CRTTree__VFuncSlot02_BuildRenderOutputs` at `0x004dd960` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004dd960`

## Identity
- Body `[0x004dd960,0x004ddfc6]`, 1639 bytes, 359 closure instructions. Raw pristine-body SHA-256 `76ce1a38f90205588092d9e3af60b5108e257d11e8246351bbfd8b9b2f626efb`; closure range SHA-256 `cdfc0d3e6bf11f0f15856dc15303d330209d2cf7e3ce10037e86e609ecd72717`; packet range-plus-bytes SHA-256 `37a01534e866726bc3be33da6342e2ee0db29fabab298fca2235c41456a30ab9`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CRTTree__VFuncSlot02_BuildRenderOutputs`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `a76105a5cf3e9f14e6749264334c32e7818719763b08d7050e4392a755357934` and decompile SHA-256 `400a861dcb73d318672b1f79d27b9cc79d527b48d66af439e8d49f7ca4087abd` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CRTTree__VFuncSlot02_BuildRenderOutputs(void * this, void * renderContext)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CRTTree__VFuncSlot02_BuildRenderOutputs(void * this, void * renderContext)
```
- Packet-declared parameter list: `void * this, void * renderContext`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_006fbe44`, `DAT_006fbe48`, `DAT_006fbe54`, `DAT_0083cd58`, `DAT_0089c9a0`, `DAT_0089c9a4`, `DAT_0089ce4c`, `DAT_009c`, `DAT_009c65c0`, `DAT_009c661c`, `DAT_009c68a0`, `DAT_009c68a1`, `DAT_009c68a8`, `DAT_009c68b6`, `DAT_009c68fc`, `DAT_009c68fd`, `DAT_009c6904`, `DAT_009c6905`, `DAT_009c690c`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `Vec3__AssignXYZ` `0x0044a5f0` x6 site(s) (STATIC_DIRECT).
- Callee `CFrontEndPage__Process_NoOp` `0x00452b60` x2 site(s) (STATIC_DIRECT).
- Callee `MathMatrix3x4__AssignFromEightScalars` `0x004901e0` x2 site(s) (STATIC_DIRECT).
- Callee `CSphere__RenderAnimatedRecursive` `0x004b6260` x1 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__SetWorldMatrixElements` `0x00550ca0` x1 site(s) (STATIC_DIRECT).
- Callers: none in the packet structured array.
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave497 CRTTree vtable 0x005deb9c slot 2. On near/falling-tree + DAT_0083cd58==0 gate: pulls this+0x08 transform, stages world matrices via CDXEngine__SetWorldMatrixElements and MathMatrix3x4__AssignFromEightScalars, packs color into DAT_009c* render globals, calls CFrontEndPage__Process_NoOp and CSphere__RenderAnimatedRecursive, then restores staged matrices. renderContext stack arg is ABI-present but unused in body. Static retail-binary only; exact virtual name, record layout, and rebuild parity unproven.”
- The non-empty packet decompile is bound by SHA-256 `400a861dcb73d318672b1f79d27b9cc79d527b48d66af439e8d49f7ca4087abd`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 0 caller record(s), 5 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 19; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `a76105a5cf3e9f14e6749264334c32e7818719763b08d7050e4392a755357934`, and packet decompile SHA-256 `400a861dcb73d318672b1f79d27b9cc79d527b48d66af439e8d49f7ca4087abd`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `004dd960:004ddfc6;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
