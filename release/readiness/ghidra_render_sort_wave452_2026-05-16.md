# Ghidra Render / Sort Wave452 Evidence

Date: 2026-05-16

## Scope

Wave452 saved Ghidra signature/comment/tag corrections for `8` render/sort targets:

`0x004b5250`, `0x004b52a0`, `0x004b52c0`, `0x004b5330`, `0x004b5ad0`, `0x004b5e80`, `0x004b6260`, and `0x004b6350`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave452-render-sort-current/`
- Apply script: `tools/ApplyRenderSortWave452.java`
- Probe: `tools/ghidra_render_sort_wave452_probe.py`
- Test alias: `npm run test:ghidra-render-sort-wave452`
- Dry summary: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Apply summary: `updated=8 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `8` metadata rows, `8` tag rows, `27` xref rows, `8` decompile exports, and focused x87/return/callsite instruction evidence.
- Hardened four clean signatures: `CDXEngine__NormalizeCycleScalar`, `Math__AbsDoubleFromSignedFloat`, `CDXEngine__PackVec3AndDepthToSortKey`, and `CMeshRenderer__RenderMesh`.
- Left four recursive render/animation wrappers signature-deferred by design: `CMeshPart__EvaluateAnimatedTransformCore`, `CMeshPart__RenderAnimatedRecursive`, `CSphere__RenderPartsWithOrientation`, and `CSphere__RenderAnimatedRecursive`.
- Queue after refresh: `6057` functions, `1973` commented, `4084` commentless, `1733` undefined signatures, `1677` `param_N` signatures.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-131157_post_wave452_render_sort_verified` (`19` files, `156633991` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime rendering/sorting, particle effect behavior, HUD overlay render behavior, concrete CMeshPart/CSphere/CMeshRenderer layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
