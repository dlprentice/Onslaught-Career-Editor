# Ghidra CTexture RB-Tree Wave654 Readiness

Status: ready for public-safe release notes
Date: 2026-05-20

Wave654 CTexture/RB-tree helper hardening saved signatures, comments, and tags for eight adjacent sentinel-backed tree/list helpers:

- `0x00572e40 CTexture__DestroyNodeTreeAndStorage`
- `0x005738e0 CTexture__EraseNodeFromTree`
- `0x00573cc0 CTexture__DestroySubtreeRecursive`
- `0x00574080 CTexture__WalkNodeListUntilSentinel`
- `0x005740a0 CTexture__RotateTreeLeft`
- `0x00574100 CTexture__InitTreeNodeParentAndKey`
- `0x00574120 CTexture__TreeIteratorNext`
- `0x00574180 CTexture__TreeIteratorPrev`

The pass made no renames, no function-boundary changes, and no executable-byte changes. Evidence is static retail Ghidra decompile, instruction, xref, saved metadata, saved comments, and saved tags. The CTexture owner prefix is retained from existing Ghidra state, but several xrefs are from adjacent CFastVB red-black-tree helpers, so this wave does not prove a concrete CTexture template/class layout.

## Evidence

- Script: `tools/ApplyCTextureTreeWave654.java`
- Probe: `tools/ghidra_ctexture_tree_wave654_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave654-ctexture-tree`
- Dry/apply/final-dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `8` metadata rows, `8` tag rows, `13` xref rows, `392` instruction rows, and `8` clean decompile rows
- Queue after Wave654: `6093` total, `3551` commented, `2542` commentless, `1217` exact-undefined signatures, `757` `param_N` signatures
- Comment-backed proxy: `3551/6093 = 58.28%`
- Strict clean-signature proxy: `3501/6093 = 57.46%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-195520_post_wave654_ctexture_tree_verified`, `19` files, `163089287` bytes, `DiffCount=0`
- Next queue head: `0x00572f00 CFastVB__InitDwordSpanBuilderState_00572f00`

## Boundaries

Wave654 proves saved static metadata for the observed sentinel-backed tree/list helpers only. Exact owner/template identity, concrete node layout, runtime texture behavior, runtime CFastVB tree behavior, BEA patching, and rebuild parity remain unproven.
