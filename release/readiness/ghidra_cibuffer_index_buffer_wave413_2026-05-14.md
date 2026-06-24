# Ghidra CIBuffer Index Buffer Correction - 2026-05-14

Status: public-safe static Ghidra evidence note

This note records a serialized saved-Ghidra metadata correction for the CIBuffer index-buffer lifecycle/create/lock/release cluster in the Steam retail `BEA.exe` project. The pass used read-only metadata, tag, xref, vtable, decompile, instruction, and callsite review before a headless dry/apply mutation, then verified the saved project with read-back exports and focused probes.

## Corrected Targets

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00488210` | `void * __thiscall CIBuffer__Constructor(void * this)` | Sets the CIBuffer vtable, clears the D3D index-buffer pointer, initializes the base render/device-object path, and clears shadow-copy/dirty fields. |
| `0x00488270` | `void * __thiscall CIBuffer__ScalarDeletingDestructor(void * this, byte flags)` | Calls the base CIBuffer destructor and conditionally frees the object when `flags & 1` is set. |
| `0x00488290` | `void __thiscall CIBuffer__Destructor(void * this)` | Restores the CIBuffer vtable, runs base cleanup, releases the D3D index-buffer pointer when present, clears `+0x08`, and frees shadow-copy storage. |
| `0x00488330` | `int __thiscall CIBuffer__CreateConfigured(void * this, int size_bytes, int usage_flags, int index_format, int buffer_type)` | Corrects the earlier five-argument wording; retail read-back shows `RET 0x10`, stores four stack arguments, and dispatches dynamic/static create through vtable slots. |
| `0x00488380` | `int __thiscall CIBuffer__Create(void * this, int index_count)` | Allocates `index_count * 2` shadow storage from the `ibuffer.cpp` debug path, stores size/usage/format/type fields, then dispatches dynamic create. |
| `0x004883f0` | `int __thiscall CIBuffer__Unlock(void * this)` | Directly unlocks when no shadow upload is pending, or locks with `0x800`, copies shadow bytes, clears the dirty flag, and unlocks. |
| `0x00488460` | `int __thiscall CIBuffer__CreateDynamic(void * this)` | Recovered function boundary for CIBuffer vtable slot `1`; calls the D3D `CreateIndexBuffer` wrapper with dynamic pool token `1`, then uploads shadow bytes when present. |
| `0x004884f0` | `int __thiscall CIBuffer__CreateStatic(void * this)` | Recovered function boundary for CIBuffer vtable slot `2`; calls the D3D `CreateIndexBuffer` wrapper with pool token `0` and static buffer-type gate. |
| `0x00488520` | `int __thiscall CIBuffer__ReleaseStatic(void * this)` | Releases and clears `+0x08` only for static buffer type `0`. |
| `0x00488550` | `int __thiscall CIBuffer__ReleaseDynamic(void * this)` | Releases and clears `+0x08` only for dynamic buffer type `1`. |
| `0x00488580` | `int __thiscall CIBuffer__Lock(void * this, void * * out_data)` | Returns shadow storage and marks it dirty when a shadow copy exists; otherwise locks the D3D index buffer with `0x2800` or `0x800` depending on usage flags. |
| `0x0048e350` | `void __thiscall CIBuffer__Destructor_thunk(void * this)` | Preserves the thiscall receiver and jumps to `CIBuffer__Destructor`. |

## Validation Summary

- Headless dry/apply script: `tools/ApplyCIBufferIndexBufferWave413.java`.
- Focused proof guard: `tools/ghidra_cibuffer_index_buffer_wave413_probe.py`.
- Focused tests: `tools/ghidra_cibuffer_index_buffer_wave413_probe_test.py`.
- Package script: `test:ghidra-cibuffer-index-buffer-wave413`.
- Dry run result: `updated=0 skipped=10 created=0 would_create=2 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply result: `updated=12 skipped=0 created=2 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Both dry and apply logs included `REPORT: Save succeeded`.
- Read-back verified `12` metadata rows, `12` tag rows, `37` xref rows, `12` target decompile exports, `564` target instruction rows, and CIBuffer vtable slots `0` through `4`.
- Focused probes passed through both direct Python and the package-script wrapper.
- Refreshed queue telemetry reports `6030` total functions, `1589` commented functions, `4441` commentless functions, `1900` undefined signatures, and `1839` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1589/6030 = 26.35%`; strict clean-signature `1526/6030 = 25.31%`.
- The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260514_105233_post_wave413_cibuffer_index_buffer_verified` with `19` files, `154831751` bytes, and `HashDiffCount=0`.

## Claim Boundary

This note does not prove runtime rendering behavior, concrete CIBuffer structure recovery beyond observed offsets, exact Stuart source-body identity, local-variable or structure recovery, rebuild parity, BEA launch behavior, or game patching. It records saved static Ghidra name/signature/comment/tag correction plus public-safe vtable/xref/decompile/instruction evidence.
