# Ghidra GeneralVolume Axis Correction - 2026-05-09

Status: PASS

Scope: public-safe summary of a saved Ghidra name/comment correction. Raw decompile exports, instruction windows, and mutation logs remain under ignored `subagents/` paths.

## What Changed

- `0x00413660` was corrected from `CGeneralVolume_Unk_00409e60__Wrapper_00413660` to `CGeneralVolume__ApplyYawInputByWeaponClass`.
- `0x004136e0` was corrected from stale `CMonitor__ApplyYawInputByWeaponClass` to `CGeneralVolume__ApplyPitchInputByWeaponClass`.
- Proof-boundary comments were saved for both corrected functions.

## Evidence Summary

- Rename-map preflight accepted `2` rows.
- Direct headless rename dry/apply saw the expected old names and saved both corrected names.
- Headless comment dry/apply saved the proof-boundary comments.
- Metadata, decompile, xref, and raw-callsite instruction read-back verified the saved state.
- `tools\ghidra_general_volume_axis_correction_probe.py --check` returned PASS.
- The refreshed queue reports `5865` total functions, `371` commented functions, `5494` commentless functions, `2` uncertain-owner names, `0` address-suffixed helper names, and `3` address-suffixed wrapper names.

## Interpretation

- Raw mode-2 dispatch calls both targets through the same GeneralVolume group at `actor+0x578`.
- `0x00413660` is the config-scaled yaw-axis helper called from raw callsite `0x004d337b`.
- `0x004136e0` is the fixed-rate pitch-axis helper called from raw callsite `0x004d3390`.
- This consumes `0x00413660` from the name-confidence deferral queue and corrects an adjacent stale Monitor owner/axis label.

## Not Proven

- This does not harden signatures, parameter names, local names, tags, structures, or type information.
- This does not prove exact source identity or runtime behavior.
- This does not launch, patch, or mutate `BEA.exe` or the installed game.
- The remaining name-confidence deferral queue is still `0x00402dd0`, `0x0040dda0`, and `0x00418090`.
