# Ghidra CDXPatch Manager Wave613

Status: ready
Date: 2026-05-20

## Scope

Wave613 saved signature/comment/tag hardening for the CDXPatch and CDXPatchManager terrain-patch lifecycle island:

- `0x00550380 CDXPatch__Constructor`
- `0x005503a0 CDXPatch__Destructor_thunk`
- `0x005503b0 CDXPatchManager__ReleasePatches`
- `0x005503d0 CDXPatchManager__ResetPatchSlots`
- `0x00550400 CDXPatchManager__AllocatePatchSlot`
- `0x00550430 CDXPatchManager__Init`
- `0x005506e0 CDXPatchManager__Destroy`
- `0x00550730 CDXPatch__FreeData`
- `0x00550750 CDXPatch__LoadFromFile`

The pass made no renames and did not create or repair function boundaries. The evidence is static retail Ghidra decompile, instruction, xref, callsite, vtable, and post-save tag read-back. Runtime terrain rendering and rebuild parity remain unproven.

## What Changed

- `CDXPatch__Constructor` now records the ECX-only constructor ABI, `CVBuffer__ctor_base` call, and vtable install at `0x005e5114`.
- `CDXPatch__Destructor_thunk` now records the ECX-only thunk path to `CVBuffer__dtor_base`.
- `CDXPatchManager__ReleasePatches` now records the destroy callback shape over 8-byte patch-pool entries and the vtable slot-0 delete dispatch.
- `CDXPatchManager__ResetPatchSlots` now records the ECX patch-pool ABI, `0x50`-byte stride, and free-slot marker write at patch `+0x3c`.
- `CDXPatchManager__AllocatePatchSlot` now records the one-stack-argument `RET 0x4` slot-id ABI, free-slot scan, and null-on-exhaustion return.
- `CDXPatchManager__Init` now records the engine init callsite counts `800`, `300`, and `90`, three `0x50`-byte patch arrays, grid vertex buffer setup for LOD steps `2`, `4`, and `8`, and 48 CLandscapeTexture entries arranged as three 16-texture mip groups.
- `CDXPatchManager__Destroy` now records the engine shutdown callsite, pool-table callback destruction, count-header free, and landscape-texture vector release.
- `CDXPatch__FreeData` now records the unbounded caller at `0x005120cb`, the patch data pointer at `+0x0c`, and the clear-after-free behavior.
- `CDXPatch__LoadFromFile` now records the resource accumulator callsite, `3x16` table reads into `+0x10`, count read into `+0xd0`, `count*2` data allocation, and loaded flag at `+0x08`.

## Evidence

- Apply script: `tools/ApplyCDXPatchManagerWave613.java`
- Focused probe: `tools/ghidra_cdxpatch_manager_wave613_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave613-cdxpatch-manager-00550380-00550750/`
- Initial clean dry: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `9` metadata rows, `9` tag rows, `16` xref rows, `2349` instruction rows, `9` decompile rows, `464` callsite instruction rows, and `10` vtable-slot rows.
- Verified backup: `G:\GhidraBackups\BEA_20260520-001229_post_wave613_cdxpatch_manager_verified`
  - `sourceFileCount=19`
  - `destFileCount=19`
  - `sourceBytes=161614727`
  - `destBytes=161614727`
  - `DiffCount=0`

## Queue Delta

Post-Wave613 queue telemetry:

- Total functions: `6093`
- Commented functions: `3156`
- Commentless functions: `2937`
- Exact-undefined signatures: `1275`
- `param_N` signatures: `1056`
- Comment-backed proxy: `3156/6093 = 51.80%`
- Strict clean-signature proxy: `3111/6093 = 51.06%`
- Next queue head: `0x00552060 CDXShadows__Destructor`

Delta from Wave612:

- `+9` commented rows
- `-9` commentless rows
- `-8` exact-undefined signatures
- `0` `param_N` signatures
- `+9` strict clean rows

## Limits

This is static retail evidence only. Exact CDXPatch, CDXPatchManager, CDXPatch pool, CLandscapeTexture, and serialized patch-data layouts remain partial. CDXPatch vtable slot 0 still points to `0x00550320`, where no Ghidra function exists yet; the nearby unbounded region calls `CDXPatch__Destructor_thunk` at `0x0055035c`, but boundary recovery is deferred. Runtime terrain rendering, runtime LOD behavior, concrete D3D device behavior, BEA patching, and rebuild parity remain unproven.
