# CFastVB__BuildTriangleAdjacency

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__BuildTriangleAdjacency` at `0x0056f620` in the call-connected triangle adjacency, strip selection, merge/order, and index-buffer support pipeline; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0056f620`

## Identity
- Body `[0x0056f620,0x0056fcdf]`, 1728 bytes, 602 closure instructions. Raw pristine-body SHA-256 `5edd7dc4478aaf6809e96b4f9403009750049c1ef49bba71a0fc07d6e3c6ff1d`; closure range SHA-256 `0387c9e54f2c02d988a305a75f346b60760db17914e506797516245863d6e0e6`; packet range-plus-bytes SHA-256 `cdc45e2aaa0f15dc7759955dd285843f211d487a96654f2c8c7d2eb2006c086b`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__BuildTriangleAdjacency`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `08ef67f285d9ba606104915e0bc83ece9ceb1c447c7c74cb5fd185d7bb32ea53` and decompile SHA-256 `d662df9001ab9cc54855edd70e377ad32ac8b7e75ddc69f1aacbc9b7f669019f` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `void __thiscall CFastVB__BuildTriangleAdjacency(void * this, void * triangle_record_span, void * edge_buckets, int max_vertex_index)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
void __thiscall CFastVB__BuildTriangleAdjacency(void * this, void * triangle_record_span, void * edge_buckets, int max_vertex_index)
```
- Packet-declared parameter labels are analyst intent. Concrete layouts, units, ownership, aliasing, valid ranges, nullability, and unlisted register-carried values remain not_determinable unless directly bounded by the quoted packet comment.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called/indirect targets.

## Globals read/written
- Decompile symbol references: `s_BuildStripifyInfo__`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `SharedVFunc__NoOpRet8_00405db0` `0x00405db0` x3 site(s) (STATIC_DIRECT).
- Callee `OID_T3_00426fd0` `0x00426fd0` x7 site(s) (STATIC_DIRECT).
- Callee `OID_T3_00449d40` `0x00449d40` x4 site(s) (STATIC_DIRECT).
- Callee `CRT__PrintfStdoutLocked` `0x0055e183` x3 site(s) (STATIC_DIRECT).
- Callee `CFastVB__FindEdgeRecord` `0x0056f540` x3 site(s) (STATIC_DIRECT).
- Callee `CFastVB__ContainsTriangleTriplet` `0x0056f5c0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__HasDuplicateTriangleIndices16` `0x00571890` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__AppendDwordRangeToSpanBuilder_00572f20` `0x00572f20` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CopyDwordRange` `0x00572f50` x9 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CountDwordsFromPointerSpan` `0x00573310` x8 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InsertDwordSpanFilled` `0x005736d0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__FillDwordSpanWithValue_00573ff0` `0x00573ff0` x4 site(s) (STATIC_DIRECT).
- Caller `CFastVB__BuildStripBatchesFromIndexBuffer` `0x005715b0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “CFastVB triangle adjacency builder (stripify prep): ECX receiver treats this as 16-bit index span; sizes triangle/edge-bucket spans, creates 0x18-byte triangle and 0x1c-byte edge records, links opposites via CFastVB__FindEdgeRecord, emits diagnostics. Terminator `RET 0xc` proves three stack dwords after this. Sole callsite BuildStripBatchesFromIndexBuffer pushes triangle span, edge buckets, max_vertex_index + `MOV ECX,ESI` — no fifth arg. Declared `uint mode_flags` is false. Shape is `void __thiscall (void * this, void * triangle_record_span, void * edge_buckets, int max_vertex_index)` (names provisional). Static retail mesh/strip evidence only; exact record layout, runtime render UX, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `d662df9001ab9cc54855edd70e377ad32ac8b7e75ddc69f1aacbc9b7f669019f`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 12 callee record(s), and 1 string-ref record(s). Manifest subfamily: `strip_index_buffer_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 10; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `08ef67f285d9ba606104915e0bc83ece9ceb1c447c7c74cb5fd185d7bb32ea53`, and packet decompile SHA-256 `d662df9001ab9cc54855edd70e377ad32ac8b7e75ddc69f1aacbc9b7f669019f`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0056f620:0056fcdf;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x00656e68` length 71 SHA-256 `69142288dc9cf07b13733ba270a33900cea10dae8fd9abc20139ec7e5c1a3801` value `BuildStripifyInfo: > 2 triangles on an edge... uncertain consequences\n`.
- Source-first authorities joined before packets: `reverse-engineering/source-crosswalk/crosswalk.tsv`, `reverse-engineering/source-crosswalk/expansion/w1-save-session-input-frontend/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w2-thing-battleengine-camera/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w3-audio-music/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w4-memory-container-archive/RECEIPT.json`, `reverse-engineering/source-crosswalk/expansion/w5-engine-render-platform-shell/RECEIPT.json`.
- Selected source crosswalk rows: none for this VA; this is an explicit packet-first row, not an assertion that no source analog exists.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, reconciled signature text, structured edge inventory, comments, strings, all source-authority joins, and TTD presence/absence are pinned. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global/container record.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, topology/codec policy, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
