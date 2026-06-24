# Ghidra CDXMeshVB Head Wave609

Status: ready
Date: 2026-05-20

## Scope

Wave609 saved signature/comment/tag hardening for the CDXMeshVB lifecycle, build, release, and load head:

- `0x0054bf80 CDXMeshVB__ctor`
- `0x0054bff0 CDXMeshVB__scalar_deleting_dtor`
- `0x0054c010 CDXMeshVB__dtor_base`
- `0x0054c0a0 CDXMeshVB__BuildStaticVB`
- `0x0054c920 CDXMeshVB__BuildSkeletalVB`
- `0x0054d3f0 CDXMeshVB__ReleaseResources`
- `0x0054e160 CDXMeshVB__Load`

The pass made four owner/name corrections and left the renderer pass entry at `0x0054d530 CMeshRenderer__RenderMeshWithLayerPasses` for a separate callsite-focused wave. The current source checkout does not include `DXMeshVB.cpp` or `DXMeshVB.h`, so the evidence is retail Ghidra decompile, instruction, xref, vtable, and post-save tag read-back.

## What Changed

- `CDXMeshVB__ctor` now has the saved signature `void * __thiscall CDXMeshVB__ctor(void * this)` and records vtable `0x005e50fc`, the cleared fields at `+0x108/+0x10c/+0x110/+0x120/+0x124`, and the 64 group-pointer slots at `+0x8`.
- `CDXMeshVB__scalar_deleting_dtor` now has the saved signature `void * __thiscall CDXMeshVB__scalar_deleting_dtor(void * this, byte flags)` and records vtable slot `0`, `RET 0x4`, the base destructor call, and conditional free when `flags&1`.
- `CDXMeshVB__dtor_base` now has the saved signature `void __thiscall CDXMeshVB__dtor_base(void * this)` and records the `CDXMeshVB__ReleaseResources` call, name free at `+0x124`, and base device-object teardown.
- `CDXMeshVB__BuildStaticVB` now has the saved signature `int __thiscall CDXMeshVB__BuildStaticVB(void * this)` and records 0x24-byte static vertices, FVF `0x152`, group/index buffer construction, and stride/FVF/primitive fields `+0x114/+0x118/+0x11c` as `0x24/0x152/4`.
- `CDXMeshVB__BuildSkeletalVB` now has the saved signature `int __thiscall CDXMeshVB__BuildSkeletalVB(void * this)` and records the `Building skeletal VB` status path, 0x30-byte skeletal vertices, the `DAT_00854e6c` hardware gate, and stride/FVF/primitive fields `+0x114/+0x118/+0x11c` as `0x30/0/4`.
- `CDXMeshVB__ReleaseResources` now has the saved signature `int __thiscall CDXMeshVB__ReleaseResources(void * this)` and records vtable slot `4`, shared first-group VB release, per-group index/group cleanup, group-count reset at `+0x108`, and vertex-shader reference cleanup at `+0x110`.
- `CDXMeshVB__Load` now has the saved signature `void __thiscall CDXMeshVB__Load(void * this, void * reader, int use_hardware_shader)` and records `RET 0x8`, the `CMeshPart__LoadFromStream` xref, 0x128-byte serialized header read, group record reads, and the `DAT_00854e6c && use_hardware_shader` gate.

## Evidence

- Apply script: `tools/ApplyCDXMeshVBHeadWave609.java`
- Focused probe: `tools/ghidra_cdxmeshvb_head_wave609_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave609-cdxmeshvb-head-0054bf80/`
- Dry/apply/final dry:
  - dry: `updated=0 skipped=7 renamed=0 would_rename=4 missing=0 bad=0`
  - apply: `updated=7 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`
  - final dry: `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `7` metadata rows, `7` tag rows, `9` xref rows, `791` instruction rows, `7` decompile rows, and `16` vtable-slot rows.
- Vtable read-back verified slot `0` as `CDXMeshVB__scalar_deleting_dtor` and slot `4` as `CDXMeshVB__ReleaseResources`.
- Verified backup: `G:\GhidraBackups\BEA_20260519-221542_post_wave609_cdxmeshvb_head_verified`
  - `sourceFileCount=19`
  - `destFileCount=19`
  - `sourceBytes=161418119`
  - `destBytes=161418119`
  - `DiffCount=0`

## Queue Delta

Post-Wave609 queue telemetry:

- Total functions: `6093`
- Commented functions: `3124`
- Commentless functions: `2969`
- Exact-undefined signatures: `1301`
- `param_N` signatures: `1060`
- Comment-backed proxy: `3124/6093 = 51.27%`
- Strict clean-signature proxy: `3079/6093 = 50.53%`
- Next queue head: `0x0054d530 CMeshRenderer__RenderMeshWithLayerPasses`

Delta from Wave608:

- `+7` commented rows
- `-7` commentless rows
- `-3` exact-undefined signatures
- `-4` `param_N` signatures
- `+7` strict clean rows

## Limits

This is static retail evidence only. Exact source identity, exact CDXMeshVB/mesh/group/bone/serialized layouts, runtime render behavior, runtime asset loading, concrete D3D output, BEA patching, and rebuild parity remain unproven.
