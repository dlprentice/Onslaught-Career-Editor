# imageloader.cpp Functions

> Source File: imageloader.cpp | Binary: BEA.exe
> Debug Path: 0x0062d3cc (`C:\dev\ONSLAUGHT2\imageloader.cpp`)
> RTTI: 0x0062d3b8 (`.?AVCImageLoader@@`)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

CImageLoader is a retail image-loader base class with a vtable at `0x005dbedc`. The available Stuart source snapshot does not include the `imageloader.cpp` body, so this page is based on Steam retail Ghidra read-back, debug strings, RTTI, vtable pointers, decompile evidence, and callsite review rather than exact source-body identity.

Wave414 re-audited the ImageLoader vtable and neighboring direct-lock helper. It hardened eight existing CImageLoader targets, created three missing CImageLoader getter boundaries, created two shared vtable getter boundaries, and corrected stale `0x004885e0` ownership from a CVBufTexture helper label to `CIBuffer__LockDirect`.

## Class Layout

Observed member access patterns support this partial layout:

| Offset | Observed role | Notes |
| --- | --- | --- |
| `0x00` | vtable | Constructor installs `0x005dbedc`. |
| `0x04` | field returned by shared vfunc | Zeroed by constructor; exposed through shared slot `0x0052f540`. Exact semantics remain unproven. |
| `0x08` | image width | Returned by `CImageLoader__GetWidth`. |
| `0x0c` | image height | Returned by `CImageLoader__GetHeight`. |
| `0x10` | width buffer pointer | Freed by `CImageLoader__FreeWidthBuffer`; loaded with `0x80`-byte allocation. |
| `0x14` | height buffer pointer / shared field context | Freed by `CImageLoader__FreeHeightBuffer`; returned by shared slot `0x004de070` in multiple vtables. |
| `0x18` | filename storage | `CImageLoader__GetFilenamePtr` returns `this+0x18`; constructor copies the filename here. |

Concrete C++ type declarations, allocator ownership, field names, and runtime image-loading behavior remain unproven.

## Virtual Table

Observed ImageLoader vtable slots at `0x005dbedc`:

| Slot | Slot address | Target | Function |
| ---: | --- | --- | --- |
| `0` | `0x005dbedc` | `0x004886a0` | `CImageLoader__ScalarDeletingDestructor` |
| `1` | `0x005dbee0` | `0x0055df1f` | `CRT__Purecall_0055df1f` |
| `2` | `0x005dbee4` | `0x00488670` | `CImageLoader__GetFilenamePtr` |
| `3` | `0x005dbee8` | `0x0052f540` | `SharedVFunc__ReturnField04_0052f540` |
| `4` | `0x005dbeec` | `0x00488680` | `CImageLoader__GetWidth` |
| `5` | `0x005dbef0` | `0x00488690` | `CImageLoader__GetHeight` |
| `6` | `0x005dbef4` | `0x00453a60` | `CMenuItem__IsEnabled` |
| `7` | `0x005dbef8` | `0x004de070` | `SharedVFunc__ReturnField14_004de070` |
| `8` | `0x005dbefc` | `0x00405930` | `SharedVFunc__ReturnZero_00405930` |
| `9` | `0x005dbf00` | `0x00488740` | `CImageLoader__FreeWidthBuffer` |
| `10` | `0x005dbf04` | `0x00488760` | `CImageLoader__FreeHeightBuffer` |
| `11` | `0x005dbf08` | `0x00488780` | `CImageLoader__LoadWidthBuffer` |
| `12` | `0x005dbf0c` | `0x004887c0` | `CImageLoader__LoadHeightBuffer` |

Rows after slot `12` in the wider pointer read-back are adjacent data or neighboring tables, not ImageLoader slots under the current evidence.

## Functions

Documented CImageLoader-related targets: `11` total.

| Address | Saved name | Saved signature | Purpose |
| --- | --- | --- | --- |
| `0x00488620` | `CImageLoader__Constructor` | `void * __thiscall CImageLoader__Constructor(void * this, char * filename)` | Zero fields `+0x04` through `+0x14`, install vtable, copy filename to `+0x18`. |
| `0x00488670` | `CImageLoader__GetFilenamePtr` | `char * __thiscall CImageLoader__GetFilenamePtr(void * this)` | Getter returning `this+0x18`. |
| `0x00488680` | `CImageLoader__GetWidth` | `int __thiscall CImageLoader__GetWidth(void * this)` | Getter returning width from `+0x08`. |
| `0x00488690` | `CImageLoader__GetHeight` | `int __thiscall CImageLoader__GetHeight(void * this)` | Getter returning height from `+0x0c`. |
| `0x004886a0` | `CImageLoader__ScalarDeletingDestructor` | `void * __thiscall CImageLoader__ScalarDeletingDestructor(void * this, byte flags)` | Destructor wrapper with optional object free when `flags & 1`. |
| `0x00488700` | `CImageLoader__Destructor` | `void __thiscall CImageLoader__Destructor(void * this)` | Restore base vtable and free both buffers. |
| `0x00488740` | `CImageLoader__FreeWidthBuffer` | `void __thiscall CImageLoader__FreeWidthBuffer(void * this)` | Free and clear buffer pointer at `+0x10`. |
| `0x00488760` | `CImageLoader__FreeHeightBuffer` | `void __thiscall CImageLoader__FreeHeightBuffer(void * this)` | Free and clear buffer pointer at `+0x14`. |
| `0x00488780` | `CImageLoader__LoadWidthBuffer` | `bool __thiscall CImageLoader__LoadWidthBuffer(void * this, void * alloc_context)` | Free existing width buffer, allocate `0x80` bytes, store at `+0x10`, return allocation success. |
| `0x004887c0` | `CImageLoader__LoadHeightBuffer` | `bool __thiscall CImageLoader__LoadHeightBuffer(void * this, void * alloc_context)` | Free existing height buffer, allocate `0x80` bytes, store at `+0x14`, return allocation success. |
| `0x004f2c60` | `CTGALoader__CTGALoader` | See `tgaloader.cpp` | Derived TGA loader constructor calls the ImageLoader base constructor. |

Shared vtable helpers used by this table:

| Address | Saved name | Evidence |
| --- | --- | --- |
| `0x0052f540` | `SharedVFunc__ReturnField04_0052f540` | Compact getter returns field `+0x04`; DATA xrefs include ImageLoader and other vtables. |
| `0x004de070` | `SharedVFunc__ReturnField14_004de070` | Compact getter returns field `+0x14`; DATA xrefs include ImageLoader, CTGALoader, CRTMesh, and other vtables. |

## Buffer Helpers

Both load helpers follow the same static pattern:

1. Call the corresponding free vtable slot (`+0x24` for width, `+0x28` for height).
2. Allocate `0x80` bytes through the global allocator using the `imageloader.cpp` debug path.
3. Store the result at `+0x10` or `+0x14`.
4. Return whether allocation succeeded.

The preserved allocation line tokens are `0x2b` for width-buffer load and `0x32` for height-buffer load.

## Inheritance Context

```
CImageLoader (base)
    |
    +-- CTGALoader (TGA format support)
```

CTGALoader vtable entries reuse `CImageLoader__GetFilenamePtr`, `CImageLoader__GetWidth`, `CImageLoader__GetHeight`, `SharedVFunc__ReturnField04_0052f540`, and `SharedVFunc__ReturnField14_004de070`.

## Wave414 Validation

- Headless mutation script: `tools/ApplyCImageLoaderWave414.java`.
- Focused proof guard: `tools/ghidra_cimageloader_wave414_probe.py`.
- Focused tests: `tools/ghidra_cimageloader_wave414_probe_test.py`.
- Package script: `test:ghidra-cimageloader-wave414`.
- Dry run: `updated=0 skipped=8 created=0 would_create=5 renamed=0 would_rename=1 missing=0 bad=0`.
- Apply run: `updated=13 skipped=0 created=5 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`.
- Read-back verified `13` metadata rows, `13` tag rows, ImageLoader vtable rows, xrefs, `13` decompile exports, and instruction evidence for the compact getter boundaries.
- Refreshed queue telemetry reports `6035` total functions, `1602` commented functions, `4433` commentless functions, `1893` undefined signatures, and `1838` `param_N` signatures.

## Claim Boundary

This page records saved static Ghidra name/signature/comment/tag correction and public-safe retail binary evidence. It does not prove runtime image loading, runtime rendering behavior, exact source-body identity, complete CImageLoader/CTGALoader/CRTMesh layouts, local-variable or structure recovery, BEA launch behavior, game patching, or rebuild parity.
