# Ghidra CDXSnow Boundary Wave615

Status: ready
Date: 2026-05-20

## Scope

Wave615 corrected the stale CDXSnow function boundary at the current high-signal queue head:

- `0x00555020 CAtmosphericsProfile__ResetAndInitSnowResources`
- `0x0055515e` is no longer a function entry; it is contained inside the corrected `0x00555020` body.

The saved Ghidra evidence shows vtable `0x005e5974` slot `+0x0c` / address `0x005e5980` points to `0x00555020`, while `Atmospherics__ResetAndUpdate` dispatches that slot over the atmospheric list. The old `0x0055515e CDXSnow__Init` row had no xrefs and started after the real SEH prologue/resource setup.

## What Changed

- Deleted the stale split function entry at `0x0055515e CDXSnow__Init`.
- Created the corrected function at `0x00555020`.
- Saved signature `void __thiscall CAtmosphericsProfile__ResetAndInitSnowResources(void * this)`.
- Set the corrected body to `0x00555020-0x00555403`, ending before `0x00555410 CAtmosphericsProfile__ReleaseResources`.
- Added bounded comments/tags for the vtable slot, old split address, CVBufTexture snow allocation at `this+0x8`, `cg_snow_*` console-variable registration, snow quad/index population, and resource cleanup/reinit flow.

## Evidence

- Apply script: `tools/ApplyCDXSnowBoundaryWave615.java`
- Focused probe: `tools/ghidra_cdxsnow_boundary_wave615_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave615-cdxsnow-init-0055515e/`
- Initial clean dry: `updated=0 skipped=1 created=0 would_create=1 deleted=0 would_delete=1 body_set=0 would_set_body=1 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=1 skipped=0 created=1 would_create=0 deleted=1 would_delete=0 body_set=1 would_set_body=0 renamed=0 would_rename=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=1 created=0 would_create=0 deleted=0 would_delete=0 body_set=0 would_set_body=0 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `4` context metadata rows plus the expected stale-address miss, `4` context tag rows plus the expected stale-address miss, `5` xref rows, `339` instruction rows, `4` decompile rows plus the expected stale-address miss, and `8` vtable rows.
- Verified backup: `G:\GhidraBackups\BEA_20260520-011651_post_wave615_cdxsnow_boundary_verified`
  - `sourceFileCount=19`
  - `destFileCount=19`
  - `sourceBytes=161614727`
  - `destBytes=161614727`
  - `DiffCount=0`

## Queue Delta

Post-Wave615 queue telemetry:

- Total functions: `6093`
- Commented functions: `3160`
- Commentless functions: `2933`
- Exact-undefined signatures: `1271`
- `param_N` signatures: `1056`
- Comment-backed proxy: `3160/6093 = 51.86%`
- Strict clean-signature proxy: `3115/6093 = 51.12%`
- Next queue head: `0x005563d0 CDXSurf__RenderSurface`

Delta from Wave614:

- `+1` commented row
- `-1` commentless row
- `-1` exact-undefined signature
- `0` `param_N` signatures
- `+1` strict clean row

## Limits

This is static retail Ghidra boundary/signature/comment/tag evidence only. Runtime snow/weather behavior remains unproven. Exact source method identity, concrete `CAtmosphericsProfile` / `CDXSnow` / `CVBufTexture` / shader layouts, runtime rendering behavior, BEA patching, and rebuild parity remain deferred.
