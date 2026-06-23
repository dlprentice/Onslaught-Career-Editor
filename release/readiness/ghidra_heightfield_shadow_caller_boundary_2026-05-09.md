# Ghidra Heightfield Shadow Caller Boundary - 2026-05-09

Status: PASS

Scope: public-safe summary of a saved Ghidra function-boundary recovery, rename, and proof-boundary comment pass. Raw decompile exports, instruction windows, mutation inputs, and generated JSON remain under ignored `subagents/` paths.

## What Changed

- A missing function boundary at `0x00447120` was recovered and saved as `VFuncSlot_1c_00447120`.
- `0x00402dd0` was corrected from `CHeightField_Unk_0047eb80__Wrapper_00402dd0` to `ShadowHeightfield__AnyBoundsCornerAboveSampledHeight`.
- Proof-boundary comments were saved on both functions.
- The saved xref for `0x00402dd0` now resolves from callsite `0x004478a3` inside `VFuncSlot_1c_00447120` instead of `<no_function>`.

## Evidence Summary

- Pre-mutation metadata confirmed `0x00447120` had no function object.
- The only direct reference to `0x00447120` was a DATA reference from table slot `0x005e1ee0`.
- Headless create dry/apply recovered one boundary: dry `would_create=1 failed=0`, apply `created=1 renamed=1 failed=0`.
- Rename-map preflight accepted `2` rows; headless rename dry/apply corrected `0x00402dd0` and skipped already-correct `0x00447120`.
- Headless comment dry/apply saved proof-boundary comments on both functions.
- Metadata, decompile, xref, instruction, pointer-table, and focused probe read-back verified the saved state.
- `py -3 tools\ghidra_heightfield_shadow_caller_boundary_probe_test.py` returned PASS.
- `py -3 tools\ghidra_heightfield_shadow_caller_boundary_probe.py --check` returned PASS.
- `cmd.exe /c npm run test:ghidra-heightfield-shadow-caller-boundary` returned PASS.
- After refreshing the Ghidra quality snapshot, the queue reports `5866` total functions, `372` commented functions, `5494` commentless functions, `0` uncertain-owner names, `0` address-suffixed helper names, and `1` address-suffixed wrapper name.

## Interpretation

- The recovered caller is still named conservatively as a virtual-slot function because table ownership is not proven.
- The renamed helper samples attached-bounds corners against `CStaticShadows__SampleShadowHeightBilinear` and the object's height callback, then returns true when a corner exceeds the sampled/static shadow threshold.
- The remaining name-confidence tail is now the DATA table-owner case at `0x00418090`.

## Not Proven

- This does not prove the exact vtable owner or source method identity for `0x00447120`.
- This does not harden signatures, parameter names, local names, tags, structures, or type information.
- This does not prove runtime shadow behavior.
- This does not launch, patch, or mutate `BEA.exe` or the installed game.
