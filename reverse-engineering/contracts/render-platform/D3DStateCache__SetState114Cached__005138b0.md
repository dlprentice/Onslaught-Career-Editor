# D3DStateCache__SetState114Cached

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `D3DStateCache__SetState114Cached` at `0x005138b0` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x005138b0`

## Identity
- Body `[0x005138b0,0x0051392f]`, 128 bytes, 41 closure instructions. Raw pristine-body SHA-256 `c5c5f22a4de73779e433d5a0952ba4a9d0ab4d8693d71b7aab22f6b04f3a6c5e`; closure range SHA-256 `54b1ede19a0d645cdec2258d742a2ba7d2caeca617b6813dd8bf531e8a7f19ed`; packet range-plus-bytes SHA-256 `1ba55f17ea98ba4994347ca987eb88d95e3aa6f19336703c49e3a88398bd1e5e`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `D3DStateCache__SetState114Cached`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `ca105b74a2acbe3c2444aab72d9752a3d78071163175931709fa13b0f8c688fd` and decompile SHA-256 `b5e2344d59404707e81cb4c4d8e4c6a01a77ce089f20c2a8b1ecf3b56dbabb9e` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__stdcall` for `void __stdcall D3DStateCache__SetState114Cached(int state_slot, int state_id, uint value)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __stdcall D3DStateCache__SetState114Cached(int state_slot, int state_id, uint value)
```
- Packet-declared parameter list: `int state_slot, int state_id, uint value`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and its called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_008557f0`, `DAT_00888a50`, `DAT_00888a78`, `DAT_00888ac0`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callees: none in the packet structured array.
- Caller `D3DStateCache__UseDefaultRenderState` `0x004eb1e0` x28 site(s) (instruction-flow).
- Caller `D3DStateCache__SetMipFilterByGlobalToggle` `0x00551420` x2 site(s) (instruction-flow).
- Caller `D3DStateCache__SetMipFilterLinear` `0x00551460` x1 site(s) (instruction-flow).
- Caller `D3DStateCache__SetMipFilterNone` `0x00551480` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first row: neither the current canonical crosswalk nor the five landed expansion receipts owns this VA. The retail packet/pristine body is therefore the first behavior envelope.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave849 static read-back/signature/comment hardening: policy-gated state helper for DAT_00888a50 vtable slot 0x114. It suppresses state_id 6 value 3 when DAT_00888a78 lacks flag 0x20000, always suppresses state_id 8, clamps state_id 10 through DAT_00888ac0 unless the same cap flag allows the caller value, writes DAT_008557f0[state_id + state_slot*0x1e], and calls slot 0x114. Source ltshell.h has SetTextureStageState/ForceTS wrappers for this class of operation. Static retail/source evidence only; exact D3D texture-stage enum names, capability-bit identity, runtime D3D behavior, BEA patching, and rebuild parity remain deferred.”
- The non-empty packet decompile is bound by SHA-256 `b5e2344d59404707e81cb4c4d8e4c6a01a77ce089f20c2a8b1ecf3b56dbabb9e`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 4 caller record(s), 0 callee record(s), and 0 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 25; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `ca105b74a2acbe3c2444aab72d9752a3d78071163175931709fa13b0f8c688fd`, and packet decompile SHA-256 `b5e2344d59404707e81cb4c4d8e4c6a01a77ce089f20c2a8b1ecf3b56dbabb9e`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `005138b0:0051392f;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
