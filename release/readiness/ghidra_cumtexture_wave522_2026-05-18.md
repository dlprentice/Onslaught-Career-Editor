# Ghidra CUMTexture Wave522 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for the CUMTexture texture-resource wrapper

## Summary

Wave522 hardened six saved Ghidra function records around `CUMTexture`, including constructor/destructor lifecycle, mode-based configuration, texture recreation, and texture release. The pass corrected five stale/provisional names and fixed the `CUMTexture__ConfigureByMode` signature to the observed `this + three stack arguments` shape.

Targets:

- `0x004f79d0` - `CUMTexture__ctor_base`
- `0x004f7a20` - `CUMTexture__scalar_deleting_dtor`
- `0x004f7a40` - `CUMTexture__dtor_base`
- `0x004f7ab0` - `CUMTexture__ConfigureByMode`
- `0x004f7b60` - `CUMTexture__RecreateTextureResource`
- `0x004f7bd0` - `CUMTexture__VFunc_03_ReleaseTextureResource`

## Evidence

Read-back artifacts live under `subagents/ghidra-static-reaudit/wave522-cumtexture-004f79d0/`.

Verified exports:

- 6 target metadata rows
- 6 target tag rows
- 15 target xref rows
- 366 instruction rows
- 6 target decompile exports
- 6 context metadata rows
- 6 context decompile exports
- 16 vtable-slot rows

Final apply evidence:

- Dry run: `updated=0 skipped=6 renamed=0 would_rename=5 missing=0 bad=0`
- Apply run: `updated=6 skipped=0 renamed=5 would_rename=0 missing=0 bad=0`
- Save status: `REPORT: Save succeeded`
- Focused probe: `py -3 tools\ghidra_cumtexture_wave522_probe.py`
- NPM probe: `npm run test:ghidra-cumtexture-wave522`

## Queue Impact

Fresh queue after Wave522:

- Function objects: 6082
- Functions with comments: 2477
- Commentless functions: 3605
- Exact `undefined` signatures: 1594
- Signatures still using `param_N` names: 1381
- Comment-backed telemetry: `2477/6082 = 40.73%`
- Strict clean-signature telemetry: `2423/6082 = 39.84%`

These are queue telemetry only, not certification and not a milestone.

## Backup

Verified backup:

- Path: `[maintainer-local-ghidra-backup-root]\BEA_20260517-235521_post_wave522_cumtexture_verified`
- Files: 19
- Bytes: 158731143
- MissingCount: 0
- ExtraCount: 0
- HashDiffCount: 0

## Boundaries

This wave proves saved static retail Ghidra evidence only. The unresolved items `runtime GPU behavior`, runtime texture lifetime behavior, exact source-body identity, complete CUMTexture layout, BEA patching, and rebuild parity remain unproven.
