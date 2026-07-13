# DXMemBuffer.cpp Function Mappings

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004cf050` → `CMenuItem__Destructor_Thunk` (was `CMenuItem__Destructor`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1198 measured anchor: unique-address accounting now governs active current-risk progress. Wave1198 (`wave1198-cdxmembuffer-current-risk-review`) accounts for `6 CDXMemBuffer resource-buffer score15-16 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The rows are `CDXMemBuffer__ctor`, `CDXMemBuffer__InitFromFile`, `CDXMemBuffer__Skip`, `CDXMemBuffer__Read`, `CDXMemBuffer__Close`, and `CDXMemBuffer__dtor_base_Thunk`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=92 missing=0 bad=0`, then final dry updated=0 skipped=6. It made no rename, no signature change, no function-boundary change, and no executable-byte change. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; corrected active current-risk progress is `860/1179 = 72.94%`; the legacy additive counter is deprecated (`891/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 319; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `709 xref rows`, `919 instruction rows`, and `6 decompile rows`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-214911_post_wave1198_cdxmembuffer_current_risk_review_verified`. Active measurement files: `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, and `reverse-engineering/binary-analysis/mapped-systems.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Exact source-body identity, concrete CDXMemBuffer/file/CRC/path-munge layouts, runtime IO behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

> Binary-to-source function mappings for DXMemBuffer.cpp
> Last updated: 2026-05-24

## Overview

`CDXMemBuffer` is the PC buffered file I/O implementation used through the source `CMEMBUFFER` abstraction. It supports buffered reads and writes, optional compressed/CRC side data paths, and OID-backed allocation.

Wave 319 corrects several stale labels in this family:

- `0x00547d70` and `0x00547d90` are `CDXMemBuffer` constructor/destructor-base bodies, not `CChunker` methods.
- `0x00547ec0` is `CDXMemBuffer__InitFromFile`, the source-parity read-buffer initializer previously labeled `DXMemBuffer__OpenRead`.
- The read/skip/close helpers now carry `CDXMemBuffer__*` names and member-style signatures.

Wave606 completes the adjacent static read/write/EOF tranche:

- `0x00547d40`, `0x00547dc0`, `0x005482c0`, `0x00548820`, `0x00548a70`, and `0x00548d30` now carry `CDXMemBuffer__*` owner labels.
- The pass preserves conservative behavior labels for retail (`SetBufferSize`, `OpenWrite`, `ReadLine`, `WriteBytes`, `IsEOF`) instead of forcing every Stuart-source method name onto bodies where the retail implementation differs or the usage label is clearer.
- Read-back evidence verifies the buffer-size global setter, write-open path, file-size query, text line read, byte write/flush path, and EOF flag query.

Wave806 adds the raw-head close thunk:

- `0x0048ddf0 CDXMemBuffer__Close_Thunk` is a single-instruction thunk to `0x00548c00 CDXMemBuffer__Close`.
- The observed xref is `CParticleSet__LoadParticleSetFile`.
- The pass used `raw-commentless-head-wave806` and `wave806-readback-verified`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260524-102416_post_wave806_raw_commentless_head_verified`.

Wave823 adds the ParticleSet cleanup destructor thunk:

- `0x004cdb90 CDXMemBuffer__dtor_base_Thunk` is a single-instruction jump thunk to `0x00547d90 CDXMemBuffer__dtor_base`.
- The observed xref is `0x005d4230 Unwind@005d4230` in the ParticleSet.cpp cleanup continuation, where the stack-local buffer at `EBP-0x140` is destroyed.
- The pass used `particle-archive-buffer-cleanup-wave823` and `wave823-readback-verified`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260524-183746_post_wave823_particle_archive_buffer_cleanup_verified`.

Wave1028 static re-audit (`cdx-render-resource-lifecycle-review-wave1028`) re-read `0x00547d70 CDXMemBuffer__ctor` with context `0x00548570 CDXMemBuffer__Read` and no mutation. Fresh exports keep the constructor owner-corrected away from stale CChunker wording and tied to resource/chunk/file-buffer callers while preserving the exact-layout and runtime I/O proof boundary. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-021726_post_wave1028_cdx_render_resource_lifecycle_review_verified`.

Runtime file I/O behavior, exact field names, tags, locals, structure typing, and rebuild parity remain unproven.

**Debug Path:** `[maintainer-local-source-export-root]\DXMemBuffer.cpp` at `0x00650fd0`

## Estimated Class Structure

The layout below is still an estimate from static read-back and source comparison. Do not treat it as a finalized Ghidra structure.

```cpp
class CDXMemBuffer {
    /* 0x00 */ HANDLE  mFileHandle;
    /* 0x04 */ void*   mData;
    /* 0x08 */ void*   mCurrentPos;
    /* 0x0C */ void*   mCRCData;
    /* 0x10 */ int     mCRCIndex;
    /* 0x14 */ int     mFlushCount;
    /* 0x18 */ int     mBufferSize;
    /* 0x1C */ int     mBytesInBuffer;
    /* 0x20 */ int     mIsReadMode;
    /* 0x24 */ int     mIsEOF;
    /* 0x28 */ int     mIsLastChunk;
    /* 0x2C */ char    mFilename[256];
    /* ... */          // additional counters/state still under review
};
```

## Global Variables

| Address | Name | Type | Purpose |
|---------|------|------|---------|
| `0x00650f6c` | `g_DXMemBufferSize` | DWORD | Default buffer size. |
| `0x008c029c` | `g_CompressionBuffer` | byte buffer | Shared compression/decompression buffer context. |
| `0x006318a0` | `g_CompressedExtension` | char* | Extension check context for compressed files. |

## Function Mappings

### Static / Setup

| Address | Current name | Purpose |
|---------|--------------|---------|
| `0x00547d40` | `CDXMemBuffer__SetBufferSize` | Sets the global default buffer size, rounded to a 1 MiB boundary. |

### Instance Methods

| Address | Current name | Current signature | Purpose |
|---------|--------------|-------------------|---------|
| `0x0048ddf0` | `CDXMemBuffer__Close_Thunk` | `bool __fastcall CDXMemBuffer__Close_Thunk(void * this)` | Five-byte close thunk used from particle file-loading cleanup context; jumps to `0x00548c00 CDXMemBuffer__Close`. |
| `0x004cdb90` | `CDXMemBuffer__dtor_base_Thunk` | `void __fastcall CDXMemBuffer__dtor_base_Thunk(void)` | Five-byte destructor-base thunk used from ParticleSet.cpp cleanup; jumps to `0x00547d90 CDXMemBuffer__dtor_base`. |
| `0x00547d70` | `CDXMemBuffer__ctor` | `void * __fastcall CDXMemBuffer__ctor(void * this)` | Constructor/init path that zeros data, CRC pointer, and state fields used by readers. |
| `0x00547d90` | `CDXMemBuffer__dtor_base` | `void __fastcall CDXMemBuffer__dtor_base(void * this)` | Destructor-base cleanup for owned data/CRC buffers. |
| `0x00547dc0` | `CDXMemBuffer__OpenWrite` | `bool __thiscall CDXMemBuffer__OpenWrite(void * this, char * filename, int mem_type)` | Write-buffer open path; allocates the 0x100000 write buffer, opens with `CreateFileA`, and prepares `.crc` sidecar state. |
| `0x00547ec0` | `CDXMemBuffer__InitFromFile` | `bool __thiscall CDXMemBuffer__InitFromFile(void * this, char * filename, int memType, int mungePath, uint startSkip)` | Read-buffer initializer used by `CChunkReader__OpenFile`. |
| `0x005482c0` | `CDXMemBuffer__GetFileSize` | `uint __fastcall CDXMemBuffer__GetFileSize(void * this)` | Gets the underlying file size through Win32 `GetFileSize(this[0], NULL)`. |
| `0x005482d0` | `CDXMemBuffer__Skip` | `int __thiscall CDXMemBuffer__Skip(void * this, int size)` | Skips bytes forward through the active read buffer. |
| `0x00548570` | `CDXMemBuffer__Read` | `int __thiscall CDXMemBuffer__Read(void * this, void * data, int size)` | Reads bytes from the buffered file into caller storage. |
| `0x00548820` | `CDXMemBuffer__ReadLine` | `void __thiscall CDXMemBuffer__ReadLine(void * this, char * output, int max_chars)` | Reads a CR/LF-normalized text line and refills through the compressed read path when needed. |
| `0x00548a70` | `CDXMemBuffer__WriteBytes` | `void __thiscall CDXMemBuffer__WriteBytes(void * this, void * data, uint size)` | Writes bytes from caller storage into the buffered file and flushes through raw or compressed write paths. |
| `0x00548c00` | `CDXMemBuffer__Close` | `bool __fastcall CDXMemBuffer__Close(void * this)` | Closes read mode or flushes write mode, then frees active buffers. |
| `0x00548d30` | `CDXMemBuffer__IsEOF` | `bool __fastcall CDXMemBuffer__IsEOF(void * this)` | Returns the EOF flag at `this+0x24`. |

## Superseded Labels

| Address | Superseded label | Current label |
|---------|------------------|---------------|
| `0x00547d70` | `CChunker__CChunker` | `CDXMemBuffer__ctor` |
| `0x00547d90` | `CChunker__Destructor` | `CDXMemBuffer__dtor_base` |
| `0x00547d40` | `DXMemBuffer__SetBufferSize` | `CDXMemBuffer__SetBufferSize` |
| `0x00547dc0` | `DXMemBuffer__OpenWrite` | `CDXMemBuffer__OpenWrite` |
| `0x00547ec0` | `DXMemBuffer__OpenRead` | `CDXMemBuffer__InitFromFile` |
| `0x005482c0` | `DXMemBuffer__GetFileSize` | `CDXMemBuffer__GetFileSize` |
| `0x005482d0` | `DXMemBuffer__Skip` | `CDXMemBuffer__Skip` |
| `0x00548570` | `DXMemBuffer__ReadBytes` | `CDXMemBuffer__Read` |
| `0x00548820` | `DXMemBuffer__ReadLine` | `CDXMemBuffer__ReadLine` |
| `0x00548a70` | `DXMemBuffer__WriteBytes` | `CDXMemBuffer__WriteBytes` |
| `0x00548c00` | `DXMemBuffer__Close` | `CDXMemBuffer__Close` |
| `0x0048ddf0` | `thunk_DXMemBuffer__Close` | `CDXMemBuffer__Close_Thunk` |
| `0x004cdb90` | `CDXMemBuffer__dtor_base` | `CDXMemBuffer__dtor_base_Thunk` |
| `0x00548d30` | `DXMemBuffer__IsEOF` | `CDXMemBuffer__IsEOF` |

## Read Path Summary

`CChunkReader__OpenFile` calls `CDXMemBuffer__InitFromFile` with a filename, memory type, path-munging flag, and start-skip value. The read buffer then supports:

- `CDXMemBuffer__Read` for byte reads across buffer refills.
- `CDXMemBuffer__Skip` for cursor movement.
- `CDXMemBuffer__Close` for read/write close and cleanup.

These are static Ghidra/source-alignment notes. They do not prove runtime archive behavior, compression edge cases, or exact source identity for every adjacent method.

## Write / Line I/O Summary

Wave606 verifies the neighboring write and text-line helpers:

- `CDXMemBuffer__SetBufferSize` is a static/global helper with one caller-popped `requested_size` argument. Retail stores `DAT_00650f6c = 0x100000` for zero and otherwise rounds up to the next 1 MiB boundary; this differs from the related source `SetNextReadBufferSize` default/rounding behavior.
- `CDXMemBuffer__OpenWrite` is the write-open path. It takes `filename` and `mem_type`, allocates a 0x100000 buffer through `OID__AllocObject` at the retail `DXMemBuffer.cpp` line `0xe3` site, opens the file with `CreateFileA`, and prepares a `.crc` sidecar name.
- `CDXMemBuffer__GetFileSize` wraps `GetFileSize(this[0], NULL)` and returns the Win32 result directly; `CText__Init` uses the returned `EAX` value as an allocation size.
- `CDXMemBuffer__ReadLine` reads text into `output` until newline, EOF, or `max_chars - 1`, normalizes CR/LF, updates `this+0x12c` and `this+0x24`, and uses `DAT_006318a0`, `DAT_008c029c`, and `uncompress` for compressed reads.
- `CDXMemBuffer__WriteBytes` buffers caller data and flushes through raw `WriteFile` or the compressed `compress`/`DAT_008c029c` path.
- `CDXMemBuffer__IsEOF` returns the EOF flag at `this+0x24`; xrefs include `CEffect__LoadSFXFile`, `CConsole__ExecScript`, and `CPCController__ReadControllerState`.

## Wave606 Queue Note

Wave606 added comments/signatures and owner-corrected six rows. Post-Wave606 queue telemetry is `6093` total, `3109` commented, `2984` commentless, `1305` exact-undefined signatures, and `1071` `param_N` signatures. Strict clean-signature proxy is `3064/6093 = 50.29%`. The next queue head is `0x00548ec0 CDXEngine__FreeLandscapeCellList_Debug`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-204906_post_wave606_dxmembuffer_io_verified`.

## Wave806 Close Thunk Note

Wave806 raw commentless head (`raw-commentless-head-wave806`, `wave806-readback-verified`) saved `0x0048ddf0 CDXMemBuffer__Close_Thunk` as `bool __fastcall CDXMemBuffer__Close_Thunk(void * this)`. Static instruction evidence shows a direct jump to `0x00548c00 CDXMemBuffer__Close`, and xref evidence ties the thunk to `CParticleSet__LoadParticleSetFile`. Post-Wave806 queue telemetry is `6098` total, `5581` commented, `517` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5581/6098 = 91.52%`, and next raw head `0x0048f2f0 CDXLandscape__SetUpdateBoundsAndRebuildVB`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-102416_post_wave806_raw_commentless_head_verified`.

This proves saved static Ghidra metadata for the thunk only. Runtime particle file teardown, exact CDXMemBuffer layout, BEA patching, and rebuild parity remain deferred.

## Wave823 Destructor Thunk Note

Wave823 particle archive buffer cleanup (`particle-archive-buffer-cleanup-wave823`, `wave823-readback-verified`) saved `0x004cdb90 CDXMemBuffer__dtor_base_Thunk` as `void __fastcall CDXMemBuffer__dtor_base_Thunk(void)`. Static instruction evidence shows a direct jump to `0x00547d90 CDXMemBuffer__dtor_base`, and xref evidence ties the thunk to `0x005d4230 Unwind@005d4230` for the ParticleSet.cpp stack-local buffer at `EBP-0x140`. The same wave corrected `0x004cd7a0 CParticleSet__FindByNameAndTrackLinkSlot`; queue after Wave823 is `6098` total, `5628` commented, `470` commentless, strict proxy `5628/6098 = 92.29%`, and next raw commentless row `0x004cf050 CMenuItem__Destructor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-183746_post_wave823_particle_archive_buffer_cleanup_verified`.

This proves saved static Ghidra metadata for the thunk only. Runtime stack-local buffer lifetime, runtime particle archive behavior, exact unwind parent/source-body identity, exact CDXMemBuffer layout, BEA patching, and rebuild parity remain deferred.
