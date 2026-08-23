# CFastVB__MergeAndOrderStripBatches

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__MergeAndOrderStripBatches` at `0x005718c0` in the call-connected triangle adjacency, strip selection, merge/order, and index-buffer support pipeline; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x005718c0`

## Identity
- Body `[0x005718c0,0x005721eb]`, 2348 bytes, 740 closure instructions. Raw pristine-body SHA-256 `cb086a58f13d6be99e7dcaf5cb2eb5ebf8e70316b3b664182cfa07d0808f51a5`; closure range SHA-256 `8a0cc13960a75fde1abd988ba395cb6ddb07831ae138528a5e7df5f44f6f1b32`; packet range-plus-bytes SHA-256 `d358d89537969217f9d6e6821de9cd4b60549f2c94da91a4d199b9ecb695914b`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__MergeAndOrderStripBatches`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `c0009ea5ca5d084c76657da8d4a17f4e2a61ed1ed0aaeaa74b7f4dbcb9fa6430` and decompile SHA-256 `727c76911fca0e773d7521df53612b5b52dbded2fb23036ed8434786bcf1d31d` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFastVB__MergeAndOrderStripBatches(void * this, void * candidate_batch_span, void * ordered_batch_span, void * edge_buckets, void * output_batch_span)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFastVB__MergeAndOrderStripBatches(void * this, void * candidate_batch_span, void * ordered_batch_span, void * edge_buckets, void * output_batch_span)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, nullability, and unlisted register-carried values remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `SharedVFunc__NoOpRet8_00405db0` `0x00405db0` x1 site(s) (STATIC_DIRECT).
- Callee `OID_T3_00426fd0` `0x00426fd0` x5 site(s) (STATIC_DIRECT).
- Callee `OID_T3_00449d40` `0x00449d40` x4 site(s) (STATIC_DIRECT).
- Callee `CFastVB__AreTriangleVertexSetsEquivalent` `0x0056fe70` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__GetSharedVerticesBetweenTriangles` `0x0056fec0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__MergeAndOrderStripBatches_Impl_00570dd0` `0x00570dd0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__IsDirectedEdgeInTriangle` `0x00571080` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__HasDuplicateTriangleIndices32` `0x00571870` x4 site(s) (STATIC_DIRECT).
- Callee `CFastVB__SeedVertexCacheFromTriangleRefs` `0x005721f0` x2 site(s) (STATIC_DIRECT).
- Callee `CFastVB__ComputeAverageVertexOverlapScore_005723c0` `0x005723c0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CountResolvedOppositeEdges` `0x00572500` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InitDwordSpanBuilderState_00572f00` `0x00572f00` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InsertDwordAndGrow` `0x00573170` x5 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InsertDwordSpanFilled` `0x005736d0` x6 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CopyDwordRange_Strict` `0x00574200` x1 site(s) (STATIC_DIRECT).
- Caller `CFastVB__BuildStripBatchesFromIndexBuffer` `0x005715b0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “CFastVB public strip-batch merge/order helper: ECX receiver (reads this+0x10/+0x14); splits oversized batches, filters duplicate 32-bit triangle rows, delegates to MergeAndOrderStripBatches_Impl_00570dd0, scores order via edge-resolution/vertex-cache helpers. Terminator `RET 0x10` proves four stack dwords after this (candidate_batch_span, ordered_batch_span, edge_buckets, output_batch_span). Declared trailing `void * edi_context` is false — unaff_EDI only, forwarded into callees that themselves carried phantom context formals. Shape is `void __thiscall (void * this, void * candidate_batch_span, void * ordered_batch_span, void * edge_buckets, void * output_batch_span)` (names provisional). Static retail stripify evidence only; exact layouts, runtime strip quality, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `727c76911fca0e773d7521df53612b5b52dbded2fb23036ed8434786bcf1d31d`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 15 callee record(s), and 0 string-ref record(s). Manifest subfamily: `strip_index_buffer_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 20; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `c0009ea5ca5d084c76657da8d4a17f4e2a61ed1ed0aaeaa74b7f4dbcb9fa6430`, and packet decompile SHA-256 `727c76911fca0e773d7521df53612b5b52dbded2fb23036ed8434786bcf1d31d`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `005718c0:005721eb;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet stringRefs array: empty.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, all source-authority joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/container record.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, topology/codec policy, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
