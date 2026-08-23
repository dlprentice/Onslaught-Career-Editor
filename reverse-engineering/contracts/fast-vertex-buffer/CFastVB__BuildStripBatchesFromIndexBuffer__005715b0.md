# CFastVB__BuildStripBatchesFromIndexBuffer

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__BuildStripBatchesFromIndexBuffer` at `0x005715b0` in the call-connected triangle adjacency, strip selection, merge/order, and index-buffer support pipeline; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x005715b0`

## Identity
- Body `[0x005715b0,0x0057186b]`, 700 bytes, 239 closure instructions. Raw pristine-body SHA-256 `b3674e71fe2de2b92f90d0fce4ba630768c52cb7c5c9315440ed8a947c35babc`; closure range SHA-256 `3ce05169c0a252db4c352ce2d431bbc09908461ff5c321cba68f702d2fba50cc`; packet range-plus-bytes SHA-256 `0389188771d660df6cdeeccbab1fecc397c48a4dd8342c1a687ee995141316dc`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__BuildStripBatchesFromIndexBuffer`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `5bfc214c5a9c17ca1349207bcc0824fec8afdb4f38a78336d916e0b2d5c37091` and decompile SHA-256 `b2981d0ccf28cb6f6d1f668c87a305468a2ecc225b12f9a5b4767185d4183b44` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `HIGH_STATIC`. Proposed promotion: false.

## Calling convention
Packet field records `unknown` for `int CFastVB__BuildStripBatchesFromIndexBuffer(void)`. Reconciled bounded ABI: `int __thiscall CFastVB__BuildStripBatchesFromIndexBuffer(void * this, void * source_index_span, int seed_or_cache_param, int owner_field_param, int max_vertex_index, void * ordered_batch_span, void * output_batch_span)`. Packet comment, MOV ESI,ECX, the sole LEA-ECX callsite, six pushes, and RET 0x18 refute the packet field's unknown zero-argument declaration. The packet field is preserved as metadata, not asserted as true where refuted.

## Prototype and parameter semantics
```c
int __thiscall CFastVB__BuildStripBatchesFromIndexBuffer(void * this, void * source_index_span, int seed_or_cache_param, int owner_field_param, int max_vertex_index, void * ordered_batch_span, void * output_batch_span)
```
- The effective prototype is bounded by the packet's own analyst comment and instruction/callsite facts. Packet field `int CFastVB__BuildStripBatchesFromIndexBuffer(void)` remains preserved above; stronger types, ownership, nullability, and any hidden-register meaning beyond the reconciliation note remain not_determinable.

## Return value meaning
The effective bounded signature declares `int`. The analyst comment quoted in Behavior summary is bounded evidence for its interpretation; exact domain, sentinels, status meaning, and caller expectations remain not_determinable unless explicitly stated there.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `SharedVFunc__NoOpRet8_00405db0` `0x00405db0` x3 site(s) (STATIC_DIRECT).
- Callee `OID_T3_00426fd0` `0x00426fd0` x1 site(s) (STATIC_DIRECT).
- Callee `OID_T3_00449d40` `0x00449d40` x5 site(s) (STATIC_DIRECT).
- Callee `CFastVB__ReleaseBufferAndResetTriplet_0056f260` `0x0056f260` x2 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CountWordElements` `0x0056f280` x6 site(s) (STATIC_DIRECT).
- Callee `CFastVB__BuildTriangleAdjacency` `0x0056f620` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__MergeAndOrderStripBatches` `0x005718c0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__GenerateStripCandidatesFromAdjacency` `0x005725e0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__GetWordCapacity` `0x00572f80` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CopyWordRange` `0x00573140` x2 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CopyWordRange_Strict` `0x005741d0` x2 site(s) (STATIC_DIRECT).
- Caller `CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer` `0x0056eb90` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “CFastVB strip-batch pipeline entry (sole CALL from CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer): ECX receiver (`MOV ESI,ECX`) owns the 16-bit index-word span object (writes this+0x10/+0x14/+0x18/+0x1c); copies/grows source words, builds adjacency (CFastVB__BuildTriangleAdjacency), generates candidates (GenerateStripCandidatesFromAdjacency), merges/orders (MergeAndOrderStripBatches), releases temps. Terminator `RET 0x18` proves six stack dwords after this. Sole callsite: `LEA ECX,[ESP+…]` then six pushes / CALL. Decompile recovers `in_ECX` + `in_stack_00000004`…`in_stack_00000018` under locked storage WARNING — do not treat Ghidra `in_stack_*` labels as alternate EBP formals. Declared `int ...(void)` is false. Shape is `int __thiscall (void * this, void * source_index_span, int seed_or_cache_param, int owner_field_param, int max_vertex_index, void * ordered_batch_span, void * output_batch_span)` (names provisional from stack uses; do not invent typed mesh formals). Static retail stripify evidence only; exact container layouts, runtime strip quality, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `b2981d0ccf28cb6f6d1f668c87a305468a2ecc225b12f9a5b4767185d4183b44`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 11 callee record(s), and 0 string-ref record(s). Manifest subfamily: `strip_index_buffer_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 19; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `5bfc214c5a9c17ca1349207bcc0824fec8afdb4f38a78336d916e0b2d5c37091`, and packet decompile SHA-256 `b2981d0ccf28cb6f6d1f668c87a305468a2ecc225b12f9a5b4767185d4183b44`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `005715b0:0057186b;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `DARK` and confidence `HIGH_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
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
