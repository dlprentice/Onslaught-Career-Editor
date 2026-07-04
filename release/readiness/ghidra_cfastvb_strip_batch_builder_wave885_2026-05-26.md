# Ghidra CFastVB Strip-Batch Builder Wave885 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `cfastvb-strip-batch-builder-wave885`

Wave885 CFastVB strip-batch builder saved the previously raw commentless row `0x005715b0 CFastVB__BuildStripBatchesFromIndexBuffer` after serialized headless dry/apply/read-back/final dry with the `cfastvb-strip-batch-builder-wave885` and `wave885-readback-verified` tags. The pass made no renames, no function-boundary changes, no executable-byte changes, and did not launch BEA.

This row is important renderer infrastructure with low local evidence density, not low-importance filler. It sits in the CFastVB strip pipeline between Wave650-Wave653 evidence: the only xref is `0x0056ecaa` from `CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer`, and the body calls `CFastVB__BuildTriangleAdjacency`, `CFastVB__GenerateStripCandidatesFromAdjacency`, and `CFastVB__MergeAndOrderStripBatches` before cleanup of candidate, edge-bucket, overflow, and local span buffers.

Saved boundary:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005715b0 CFastVB__BuildStripBatchesFromIndexBuffer` | Existing signature display preserved as `int CFastVB__BuildStripBatchesFromIndexBuffer(void)` plus new comment/tags | Static instruction/decompile evidence shows an ECX receiver context, six stack inputs, and `RET 0x18`, but Ghidra still reports locked/hidden parameter storage. Wave885 records the ABI evidence in the comment instead of forcing an unsafe prototype. |

Read-back evidence:

- `ApplyCFastVBStripBatchBuilderWave885.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCFastVBStripBatchBuilderWave885.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCFastVBStripBatchBuilderWave885.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 239 instruction rows, 1 decompile row, 7 context metadata rows, and 7 context decompile rows.
- Corrected export logs are clean of `LockException`, `Input file not found`, and `Script not found`. The preserved `badpath-*` logs document the initial rejected export invocation that used stripped backslash paths and the wrong xref script name before the corrected rerun.
- Queue after Wave885: 6113 total, 5968 commented, 145 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5968/6113 = 97.63%`, strict clean-signature proxy `5968/6113 = 97.63%`.
- Next raw commentless row: `0x00573d80 CTexture__InsertNodeIntoTree`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-015531_post_wave885_cfastvb_strip_batch_builder_verified`, 19 files, 172821383 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved name and signature display are still `CFastVB__BuildStripBatchesFromIndexBuffer` and `int CFastVB__BuildStripBatchesFromIndexBuffer(void)`.
- The saved comment and tags include `cfastvb-strip-batch-builder-wave885` and `wave885-readback-verified`.
- The observed static body is tied to the CDXMeshVB strip-batch caller, triangle-adjacency construction, strip-candidate generation, batch merge/order, and cleanup paths.

What remains unproven:

- Exact CFastVB container, triangle, edge, candidate, and batch layouts.
- Exact locked ABI and safe source-level prototype.
- Runtime strip quality.
- Concrete D3D index-buffer behavior.
- BEA patching behavior.
- Rebuild parity.
