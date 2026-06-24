# Ghidra RenderQueue Depth-Gate Correction - 2026-05-14

Status: public-safe static Ghidra evidence note

Wave407 corrected the saved Ghidra metadata for `0x00477b70` from the caller-owned `CVBufTexture__QueueRenderIfDepthInRange` label to `CRenderQueue__InsertIfDepthBelowIndexedLimit`. This is a serialized static Ghidra correction/read-back wave only.

| Address | Previous saved label | Saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x00477b70` | `CVBufTexture__QueueRenderIfDepthInRange` | `void __thiscall CRenderQueue__InsertIfDepthBelowIndexedLimit(void * this, void * item, float depth)` | The only direct caller is `CVBufTexture__RenderDynamicUnitPass` at callsite `0x00477250`. The callsite sets `ECX to global render queue &DAT_009c7550`, pushes the item and computed depth, then calls the helper. Instruction read-back records `RET 0x8`, `DAT_0089d680`, the indexed depth-limit access, and the tail call into `CRenderQueue__InsertSortedByDepth`. |

## Correction Boundary

The previous owner label was useful as caller context but overstated the target's receiver. The current read-back supports a render-queue helper shape because the caller passes the global render queue in `ECX`, while the target uses that receiver to gate the insert and then calls the already named sorted insert helper.

## Validation

- `ApplyRenderQueueDepthGateWave407.java` dry run passed with `updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0`.
- `ApplyRenderQueueDepthGateWave407.java` apply run passed with `updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0` and `REPORT: Save succeeded`.
- Read-back verified `1` metadata row, `1` tag row, `1` xref row, `25` target instruction rows, `17` callsite instruction rows, and the post-rename decompile text.
- Refreshed queue telemetry reports `6028` functions, `1560` commented functions, `4468` commentless functions, `1909` undefined signatures, and `1856` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1560/6028 = 25.88%`, strict clean-signature `1498/6028 = 24.85%`.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260514_073711_post_wave407_renderqueue_depth_gate_verified` with `19` files, `154798983` bytes, and `HashDiffCount=0`.

## Claim Boundary

This note does not prove exact CRenderQueue layout, does not prove DAT_0089d680 semantics, does not prove runtime LOD/render behavior, does not prove rebuild parity, and does not involve launching or patching `BEA.exe`.
