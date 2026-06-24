# Ghidra CFastVB Span/Tree Wave655 Readiness

Status: ready for public-safe release notes
Date: 2026-05-20

Wave655 CFastVB span/tree utility hardening saved signatures, comments, and tags for twenty-one adjacent span buffer, copy/fill, assignment, and uint-key red-black-tree helper rows:

- `0x00572f00 CFastVB__InitDwordSpanBuilderState_00572f00`
- `0x00572f20 CFastVB__AppendDwordRangeToSpanBuilder_00572f20`
- `0x00572f50 CFastVB__CopyDwordRange`
- `0x00572f80 CFastVB__GetWordCapacity`
- `0x00572fa0 CFastVB__InsertWordAndGrow`
- `0x00573140 CFastVB__CopyWordRange`
- `0x00573170 CFastVB__InsertDwordAndGrow`
- `0x00573310 CFastVB__CountDwordsFromPointerSpan`
- `0x00573330 CFastVB__GetTreeRootNode_00573330`
- `0x00573340 CFastVB__InsertNodeIntoRBTreeWithHint_00573340`
- `0x00573560 CFastVB__EraseNodeRangeFromRBTree_00573560`
- `0x00573630 RBTree__FindLowerBoundByUIntKey`
- `0x005736a0 MemCopyU16Elements`
- `0x005736d0 CFastVB__InsertDwordSpanFilled`
- `0x00573d00 RBTree__InitUIntKeyTreeWithSharedSentinel`
- `0x00573ff0 CFastVB__FillDwordSpanWithValue_00573ff0`
- `0x00574020 CFastVB__RBTreeRotateLeft_00574020`
- `0x005741d0 CFastVB__CopyWordRange_Strict`
- `0x00574200 CFastVB__CopyDwordRange_Strict`
- `0x00574230 CFastVB__AssignDwordIfDestNotNull`
- `0x00574250 CFastVB__AssignWordIfDestNotNull`

The pass made no renames, no function-boundary changes, and no executable-byte changes. Evidence is static retail Ghidra decompile, instruction, xref, saved metadata, saved comments, and saved tags. The rows bridge CFastVB span/vector helpers and shared-sentinel uint-key red-black-tree helpers; exact STL/vector/tree owner identity and concrete node/span layouts remain unproven.

## Evidence

- Script: `tools/ApplyCFastVBSpanTreeWave655.java`
- Probe: `tools/ghidra_cfastvb_span_tree_wave655_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave655-cfastvb-span-tree`
- Dry/apply/final-dry: `updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=21 missing=0 bad=0`, then `updated=21 skipped=0 renamed=0 would_rename=0 signature_updated=21 missing=0 bad=0`, then `updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `21` metadata rows, `21` tag rows, `117` xref rows, `1869` instruction rows, and `21` clean decompile rows
- Queue after Wave655: `6093` total, `3572` commented, `2521` commentless, `1217` exact-undefined signatures, `736` `param_N` signatures
- Comment-backed proxy: `3572/6093 = 58.62%`
- Strict clean-signature proxy: `3522/6093 = 57.80%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-202319_post_wave655_cfastvb_span_tree_verified`, `19` files, `163154823` bytes, `DiffCount=0`
- Next queue head: `0x00574270 CDXTexture__FindFormatDescriptorById`

## Boundaries

Wave655 proves saved static metadata for the observed CFastVB span/vector utility and shared-sentinel uint-key tree helpers only. Exact CFastVB/span/vector/tree/layout identity, exact owner/template identity, concrete node/span layouts, runtime strip quality, runtime texture/CFastVB behavior, concrete D3D output, BEA patching, and rebuild parity remain unproven.
