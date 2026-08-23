# CFastVB__EmitTriangleStripIndexBuffer

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CFastVB__EmitTriangleStripIndexBuffer` at `0x005710d0` in the call-connected triangle adjacency, strip selection, merge/order, and index-buffer support pipeline; exact identity, structured connectivity, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — exact-base current name/register identity, new read-only READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no selected source-crosswalk owner) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x005710d0`

## Identity
- Body `[0x005710d0,0x005715a1]`, 1234 bytes, 433 closure instructions. Raw pristine-body SHA-256 `97211dfbc1abc81ca1e41433cdc2d49019ffdc2c5a73ba235b3559d20c5f09e4`; closure range SHA-256 `5ae3e6a6c9fe595e76871653633df1701d902c0157efddecc2fda2acb1cc2972`; packet range-plus-bytes SHA-256 `15d3a1439d5b3a8cfe26363dba5d96f65f5b6aa9f0d721c8d31792d04cb204a6`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CFastVB__EmitTriangleStripIndexBuffer`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `d25311d371da56d1fd8f42f7f456f622bcebc0702f2b8f8a7fdbf0306fce00f5` and decompile SHA-256 `21315bf64caa801d6e069fed04629d9f1c4003e009a7c9a8e265562a4ff4eb20` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_DARK` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet field records `__stdcall` for `void __stdcall CFastVB__EmitTriangleStripIndexBuffer(void * strip_batch_span, void * out_index_span, int emit_continuity_flag, void * out_separator_count)`. Reconciled bounded ABI: `void __thiscall CFastVB__EmitTriangleStripIndexBuffer(void * this, void * strip_batch_span, void * out_index_span, int emit_continuity_flag, void * out_separator_count)`. Packet comment reconciles the sole callsite's live ECX receiver with RET 0x10; this is dead in the body but remains part of the observed call shape. The packet field is preserved as metadata, not asserted as true where refuted.

## Prototype and parameter semantics
```c
void __thiscall CFastVB__EmitTriangleStripIndexBuffer(void * this, void * strip_batch_span, void * out_index_span, int emit_continuity_flag, void * out_separator_count)
```
- The effective prototype is bounded by the packet's own analyst comment and instruction/callsite facts. Packet field `void __stdcall CFastVB__EmitTriangleStripIndexBuffer(void * strip_batch_span, void * out_index_span, int emit_continuity_flag, void * out_separator_count)` remains preserved above; stronger types, ownership, nullability, and any hidden-register meaning beyond the reconciliation note remain not_determinable.

## Return value meaning
The effective bounded signature declares `void`; no scalar return contract is claimed. Completion, side effects, and failure reporting remain bounded by the displayed body and called/indirect targets.

## Globals read/written
- not_determinable — the displayed decompile names no `DAT_*`/`_DAT_*`/`PTR_*`/`s_*` symbol; this does not prove the body has no absolute data access.

## Callees relied on / callers
- Callee `SharedVFunc__NoOpRet8_00405db0` `0x00405db0` x1 site(s) (STATIC_DIRECT).
- Callee `OID_T3_00426fd0` `0x00426fd0` x1 site(s) (STATIC_DIRECT).
- Callee `OID_T3_00449d40` `0x00449d40` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__AreTriangleVertexSetsEquivalent` `0x0056fe70` x2 site(s) (STATIC_DIRECT).
- Callee `CFastVB__GetSharedVerticesBetweenTriangles` `0x0056fec0` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__IsEven` `0x00571060` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__IsDirectedEdgeInTriangle` `0x00571080` x2 site(s) (STATIC_DIRECT).
- Callee `CFastVB__HasDuplicateTriangleIndices32` `0x00571870` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CopyDwordRange` `0x00572f50` x3 site(s) (STATIC_DIRECT).
- Callee `CFastVB__CountDwordsFromPointerSpan` `0x00573310` x1 site(s) (STATIC_DIRECT).
- Callee `CFastVB__InsertDwordSpanFilled` `0x005736d0` x8 site(s) (STATIC_DIRECT).
- Callee `CFastVB__FillDwordSpanWithValue_00573ff0` `0x00573ff0` x2 site(s) (STATIC_DIRECT).
- Callee `CFastVB__AssignDwordIfDestNotNull` `0x00574230` x1 site(s) (STATIC_DIRECT).
- Caller `CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer` `0x0056eb90` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Packet-first boundary: the exact-base canonical 1,783-row crosswalk and all five landed source-wave receipts were joined before packet interpretation; none owns this VA. The retail packet/pristine body is therefore the first behavior envelope, and no source equivalence is implied.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “CFastVB strip index-buffer emitter: sole callsite CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer does four stack pushes then `LEA ECX,[ESP+…]` / CALL (thiscall callsite shape). Entry stores ECX then immediately reloads ECX from the first stack arg — receiver is dead/unused for body work; body walks strip batches, orients triangles, appends dword indices, inserts 0xffffffff separators when continuity disabled, updates separator count. Terminator `RET 0x10` proves four stack dwords after the (dead) this. Declared `__stdcall` without ECX receiver is false vs callsite. Shape is `void __thiscall (void * this, void * strip_batch_span, void * out_index_span, int emit_continuity_flag, void * out_separator_count)` with unused this (names provisional). Static retail mesh/strip evidence only; exact output container layout, runtime D3D index UX, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `21315bf64caa801d6e069fed04629d9f1c4003e009a7c9a8e265562a4ff4eb20`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 13 callee record(s), and 0 string-ref record(s). Manifest subfamily: `strip_index_buffer_support`.

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, rollback semantics, and invalid topology/codec input handling are not_determinable as a class from packet metadata. The decompile and quoted comment above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_21b26aac`, immutable cohort-11 manifest SHA-256 `6fe1674a2b44993effb685faa156ba35b0003b4dcfc2ec96f8b950b54511db94`, row 18; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact frozen selection base `732548904881841b00e9d49e9a0f7df20fda6ae9`, reuse disposition `NEW_MEASUREMENT`, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `d25311d371da56d1fd8f42f7f456f622bcebc0702f2b8f8a7fdbf0306fce00f5`, and packet decompile SHA-256 `21315bf64caa801d6e069fed04629d9f1c4003e009a7c9a8e265562a4ff4eb20`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `005710d0:005715a1;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
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
