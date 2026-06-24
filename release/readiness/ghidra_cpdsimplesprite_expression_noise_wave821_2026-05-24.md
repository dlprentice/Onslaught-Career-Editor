# Ghidra CPDSimpleSprite Expression/Noise Wave821 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `cpdsimplesprite-expression-noise-wave821`

Wave821 CPDSimpleSprite expression/noise saved comments, tags, and observed ABI signatures for two raw-commentless `CPDSimpleSprite` rows: `0x004c0c70 CPDSimpleSprite__EvalExpressionNode` and `0x004c7db0 CPDSimpleSprite__InitNoiseTableOnce`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004c0c70 CPDSimpleSprite__EvalExpressionNode` | `double __cdecl ... (float base_value, void * post_scale_node, void * pre_scale_node, void * pre_offset_node, void * post_offset_node, int operator_id, int output_mode, float time_scale)` | Recursive x87 ST0 scalar evaluator; self-recursive calls at `0x004c0d2c`, `0x004c0ddf`, `0x004c0f3a`, and `0x004c0fec`; nested `CPDSimpleSprite__EvaluateExpressionRecursive` bridge; observed operator cases include square, exp-style x87 `f2xm1`/`fscale`, sin, cos, reciprocal, ln2-scale, and rand jitter before clamp/wrap-style output handling. |
| `0x004c7db0 CPDSimpleSprite__InitNoiseTableOnce` | `void __cdecl ... (void)` | One-shot initializer gated by `DAT_0082b398`; clears the `0x400`-dword `DAT_0082a358` table; fills a wrapped `32x32` float grid from `_rand` midpoint/diamond-style blends; direct xrefs include `0x004c5d5e`, `0x004c8043`, and orphan block `0x004c900c`. |

Read-back evidence:

- Preserved diagnostic dry compile log: the first dry attempt failed before mutation on a Java API signature mismatch (`no suitable method found for updateFunction`). The script was corrected before any accepted apply.
- Accepted dry: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`.
- Accepted apply: `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 2 metadata rows, 2 tag rows, 18 xref rows, 1802 target instruction rows, 2873 helper instruction rows, 13 helper metadata rows, and 2 decompile rows.
- Queue after Wave821: 6098 total, 5622 commented, 476 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5622/6098 = 92.19%`, strict clean-signature proxy `5622/6098 = 92.19%`.
- Next raw commentless row: `0x004caf30 CParticleManager__ClearParticleOwnerBacklinks`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-173755_post_wave821_cpdsimplesprite_expression_noise_verified`, 19 files, 171510663 bytes, `DiffCount=0`.

What this proves:

- The two target function rows exist in the saved Ghidra project.
- The saved signatures/comments/tags match the Wave821 script read-back.
- The evidence ties the cluster to CPDSimpleSprite expression evaluation, the one-shot noise-table initializer, existing particle descriptor helper context, xrefs, instruction exports, and decompiler output.

What remains unproven:

- Exact expression-node layout.
- Exact operator names.
- Exact procedural-noise source algorithm.
- Runtime particle rendering behavior.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
