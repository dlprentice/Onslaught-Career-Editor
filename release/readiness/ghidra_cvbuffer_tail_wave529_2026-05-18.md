# Ghidra CVBuffer Tail Wave529 Readiness

Status: ready for public-safe release notes
Date: 2026-05-18
Scope: saved static Ghidra metadata for CVBuffer lifecycle, create, lock/unlock, release, stream-source, and one recovered default-pool vtable-slot boundary.

## Scope

Wave529 hardened sixteen adjacent CVBuffer helpers using static retail Ghidra evidence only. The pass corrected three stale ctor/dtor names and created one missing function boundary at `0x00500250`, where the CVBuffer vtable slot 2 and a derived DXPatch-style vtable slot both point.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004fff00` | `void * __thiscall CVBuffer__ctor_base(void * this)` | Installs the CVBuffer vtable, clears the D3D vertex-buffer pointer, initializes the base path, and clears backing storage/dirty state. |
| `0x004fff60` | `void * __thiscall CVBuffer__scalar_deleting_dtor(void * this, byte flags)` | Vtable slot 0 destructor wrapper; calls `CVBuffer__dtor_base` and frees `this` when `flags & 1` is set. |
| `0x004fff80` | `void __thiscall CVBuffer__dtor_base(void * this)` | Releases D3D vertex-buffer state, frees backing storage, and runs base teardown. |
| `0x00500020` | `int __thiscall CVBuffer__CreateInternal(void * this, int total_bytes, int usage_flags, int fvf_format, int pool_mode)` | `RET 0x10` proves four stack arguments; dispatches managed/default-pool vtable slots and returns HRESULT. |
| `0x00500080` | `bool __thiscall CVBuffer__CreateDynamic(void * this, int vertex_count, int vertex_stride, int fvf_format)` | `RET 0x0c`; stores dynamic/default-pool fields and returns `HRESULT >= 0`. |
| `0x005000c0` | `bool __thiscall CVBuffer__Create(void * this, int vertex_count, int vertex_stride, int fvf_format)` | `RET 0x0c`; stores managed-buffer fields, allocates backing storage, and dispatches restore/create slot 1. |
| `0x00500120` | `int __thiscall CVBuffer__Restore(void * this)` | Vtable slot 1 recreates managed buffers and copies backing storage into the D3D buffer when present. |
| `0x005001b0` | `int __thiscall CVBuffer__Lock(void * this, void * * out_data)` | `RET 0x4`; returns backing storage and marks dirty or forwards to D3D Lock with `0x800`. |
| `0x005001e0` | `int __thiscall CVBuffer__Unlock(void * this)` | Unlocks clean buffers or syncs dirty backing storage before unlocking. |
| `0x00500250` | `int __thiscall CVBuffer__CreateDefaultPoolVertexBuffer(void * this)` | Recovered function boundary; vtable slots `0x005dfb94` and `0x005e511c` both resolve here after apply. |
| `0x00500280` | `int __thiscall CVBuffer__Release(void * this)` | Vtable slot 3 releases mode 0 D3D buffers and clears state. |
| `0x005002b0` | `int __thiscall CVBuffer__ReleaseManaged(void * this)` | Vtable slot 4 releases mode 1 D3D buffers and clears state. |
| `0x005002e0` | `int __thiscall CVBuffer__EnsureLock(void * this, void * * out_data)` | `RET 0x4`; chooses D3D Lock flag `0x2800` or `0x800`, and callers test the returned HRESULT. |
| `0x00500320` | `void __thiscall CVBuffer__SetStreamSource(void * this, int stream_index)` | `RET 0x4`; updates FVF/active globals and calls Direct3D `SetStreamSource`. |
| `0x00500360` | `void __thiscall CVBuffer__SetStreamSourceSimple(void * this, int stream_index)` | `RET 0x4`; calls Direct3D `SetStreamSource` without global FVF/active writes. |
| `0x00500390` | `int __thiscall CVBuffer__LockRange(void * this, int offset_bytes, int size_bytes, void * * out_data, int lock_flags)` | `RET 0x10`; forwards range locks or returns `0x80004005` when no D3D buffer exists. |

## Evidence

- Mutation script: `tools/ApplyCVBufferTailWave529.java`
- Probe script: `tools/ghidra_cvbuffer_tail_wave529_probe.py`
- Evidence root: `subagents/ghidra-static-reaudit/wave529-cvbuffer-tail-004fff00/`
- Dry summary: `updated=0 skipped=16 renamed=0 would_rename=3 created=0 would_create=1 missing=0 bad=0`
- Apply summary: `updated=16 skipped=0 renamed=3 would_rename=0 created=1 would_create=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=16 renamed=0 would_rename=0 created=0 would_create=0 missing=0 bad=0`
- Read-back rows: `16` metadata rows, `16` tag rows, `90 target xref rows`, `6736` instruction rows, `16` target decompile exports, `18` context decompile exports, and `20` vtable-slot rows.
- Focused probe: `py -3 tools\ghidra_cvbuffer_tail_wave529_probe.py --check`
- NPM probe: `npm run test:ghidra-cvbuffer-tail-wave529`
- Queue probe: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check`

## Queue Impact

Fresh queue after Wave529:

- Function objects: 6083
- Functions with comments: 2552
- Commentless functions: 3531
- Exact `undefined` signatures: 1578
- Signatures still using `param_N` names: 1326
- Comment-backed telemetry: `2552/6083 = 41.95%`
- Strict clean-signature telemetry: `2498/6083 = 41.07%`

These are queue telemetry only, not certification and not a milestone.

## Backup

Verified backup:

- Path: `[maintainer-local-ghidra-backup-root]\BEA_20260518-033500_post_wave529_cvbuffer_tail_verified`
- Files: 19
- Bytes: 159026055
- MissingCount: 0
- ExtraCount: 0
- HashDiffCount: 0

## Boundaries

This is static retail Ghidra evidence only. Runtime rendering behavior, runtime device-loss behavior, exact CVBuffer/CDXPatch-derived layouts, local-variable recovery, exact Direct3D pool names, BEA patching, and rebuild parity remain unproven.
