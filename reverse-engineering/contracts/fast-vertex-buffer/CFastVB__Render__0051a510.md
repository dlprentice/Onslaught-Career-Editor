# CFastVB__Render

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__Render` at `0x0051a510` in the FastVB dynamic-buffer lifecycle, lock/update, and draw runtime; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0051a510`

## Identity
- Body `[0x0051a510,0x0051a692]`, 387 bytes, 115 closure instructions. Raw pristine-body SHA-256 `64780b481fdad9e4ebf00d2950d82fd78df238dbbbda251037ba97aa596d06f6`; closure range SHA-256 `68665b775dfc7201969df703d0445b02ac7c8211f481f8c5e857d49e451e4591`; packet range-plus-bytes SHA-256 `cc5ce4b3c563c34da93121e1a3f550dcd2d3da60e306aee68e898de8f65a6ec3`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__Render`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `7cf776b824e3732c97b58d0d36f0ef554f0eea3d1905e4c6cf46bd6a5f85cdcc` and decompile SHA-256 `b71fcec4c2d52bbacbba8839d304e8bc9161e295a7b0473e71861cfa075bda0f` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFastVB__Render(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFastVB__Render(void * this)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, nullability, and unlisted register-carried values remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called/indirect targets.

## Globals read/written
- Decompile symbol references: `DAT_00855bb0`, `DAT_00888a50`, `DAT_00897a90`, `DAT_009c3df0`, `s_C__dev_ONSLAUGHT2_FastVB_cpp_0063fb24`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CIBuffer__Constructor` `0x00488210` x1 site(s) (STATIC_DIRECT).
- Callee `CIBuffer__Create` `0x00488380` x1 site(s) (STATIC_DIRECT).
- Callee `CIBuffer__Unlock` `0x004883f0` x1 site(s) (STATIC_DIRECT).
- Callee `CIBuffer__Lock` `0x00488580` x1 site(s) (STATIC_DIRECT).
- Callee `CVBuffer__Unlock` `0x005001e0` x1 site(s) (STATIC_DIRECT).
- Callee `CEngine__DrawIndexedPrimitives` `0x00513c70` x1 site(s) (STATIC_DIRECT).
- Callee `D3DBufferRegistry__MoveToFreeList` `0x00513d20` x1 site(s) (STATIC_DIRECT).
- Callee `CEngine__SetVertexShaderHandleRaw` `0x00513ec0` x1 site(s) (STATIC_DIRECT).
- Callee `CDXMemoryManager__Alloc` `0x005490e0` x1 site(s) (STATIC_DIRECT).
- Caller `CDXCompass__Render` `0x00427210` x4 site(s) (instruction-flow).
- Caller `CFastVB__Lock` `0x0051a430` x2 site(s) (instruction-flow).
- Caller `CDXFont__DrawTextScaled` `0x00540010` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave563 signature/comment hardening: source-aligns to FastVB.cpp CFastVB::Render. The retail body returns when this+0x06 is 0xffff, unlocks the vertex buffer, binds stream source stride 0x1c, lazily allocates shared CIBuffer DAT_00897a90 from the FastVB.cpp line-0xc3 debug context, calls CIBuffer__Create with index_count 0x1d4c, fills the [0,1,2,2,3,0] quad-index pattern up to this+0x0c vertices, registers the index buffer, binds it, sets raw vertex shader/FVF handle 0x144, draws indexed primitive type 4 from this+0x06/this+0x08, then resets this+0x06 to 0xffff and this+0x08 to 0. Static retail/source evidence only; exact render-state lifetime, CFastVB/CIBuffer layout, D3D runtime behavior, BEA launch, patching, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `b71fcec4c2d52bbacbba8839d304e8bc9161e295a7b0473e71861cfa075bda0f`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 3 caller record(s), 9 callee record(s), and 1 string-ref record(s). Manifest subfamily: `runtime_lifecycle_lock_update`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 4; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `7cf776b824e3732c97b58d0d36f0ef554f0eea3d1905e4c6cf46bd6a5f85cdcc`, and packet decompile SHA-256 `b71fcec4c2d52bbacbba8839d304e8bc9161e295a7b0473e71861cfa075bda0f`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0051a510:0051a692;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0063fb24` length 29 SHA-256 `21e339b970f1866dd188072ce4950dd7c0db002c8660a86d5e0f9023e2a26ae0` value `C:\\dev\\ONSLAUGHT2\\FastVB.cpp`.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, all source-authority joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/container record.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, topology/codec policy, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
