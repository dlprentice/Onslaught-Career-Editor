# Ghidra Career / Options Signature Correction - 2026-05-10

## Summary

Wave 316 completed a saved Ghidra name/signature/comment correction tranche for `3` Career/options-adjacent targets.

The tranche hardened `0x0041bd00` as `void __fastcall CCareer__Update(void * this)` with a bounded source/decompile parity comment for the end-level Career update path.

It also corrected two stale Career owner labels:

- `0x00420cd0` is now `D3DDeviceProfileTable__GetAdapterRecord`, superseding the older `CCareer__GetSlotRecordPtr` label.
- `0x00420d10` is now `D3DDeviceProfile__PackDeviceIndexKey`, superseding the older `CCareer__PackLevelSummaryBits` label.

Fresh xref/decompile review ties both corrected helpers to `OptionsTail_Write` / `OptionsTail_Read` display-profile context, not to `CCareer` save-slot or level-summary ownership.

## Validation

- Headless correction dry run: `updated=0 skipped=3 renamed=0 missing=0 bad=0`.
- Headless correction apply: `updated=3 skipped=0 renamed=0 missing=0 bad=0`; the two stale labels had already been renamed by the initial serialized apply, and the final apply normalized signatures/comments.
- Metadata read-back: `3/3` targets found.
- Decompile read-back: `3/3` targets dumped.
- Xref read-back: saved target xrefs present for every target.
- Instruction read-back: saved target instruction context present for every target.
- Focused probe: `PASS`, `3` targets, `2` renamed targets, `0` failures.
- Whole-database queue snapshot: `5868` functions, `651` commented functions, `5217` commentless functions, `2045` undefined signatures, and `2334` `param_N` signatures.

## Boundary

This is saved static Ghidra refinement only. It does not prove exact D3D profile table layout, exact Stuart source identity for the two options helpers, runtime display behavior, runtime save behavior, BEA launch behavior, game patching, local-variable names, Ghidra tags, structure types, or rebuild parity.

Raw read-back exports and generated proof JSON remain under ignored `subagents/`.
