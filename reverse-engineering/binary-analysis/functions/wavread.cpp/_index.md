# wavread.cpp - WAV File Reader

**Source File:** `[maintainer-local-source-export-root]\wavread.cpp`
**Debug String Address:** `0x0063d1b0`
**Function Address Range:** `0x00505210` - `0x005056b0`

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

WAV file reader implementation for loading PCM-style audio through the Windows Multimedia I/O (`mmio`) API. Wave537 recovered the saved CWaveSoundRead function boundaries from the concrete/base vtables and hardened signatures/comments/tags in Ghidra.

This page is static retail-binary evidence. It does not prove runtime WAV acceptance behavior, runtime DirectSound integration, exact DirectX SDK source-body identity, concrete CWaveSoundRead/base layouts, or rebuild parity.

Wave908 audio/media/cutscene static review (`audio-media-cutscene-static-review-wave908`) keeps the WAV reader inside the static-coherent audio/media/cutscene/camera core. The read-only slice covers `CWaveSoundRead 11` plus `WavRead 2` rows inside the `171` selected-row, `26` family evidence set, with anchors `CWaveSoundRead__Open`, `CWaveSoundRead__Read`, `WavRead__ReadMMIO`, and `WavRead__WaveReadFile`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified`. Runtime WAV decode/acceptance, DirectSound integration, exact SDK source identity, patch behavior, and rebuild parity remain unproven.

## Class: CWaveSoundRead

Observed object fields from the hardened functions:

| Offset | Observed content |
| ---: | --- |
| `+0x00` | vtable pointer |
| `+0x04` | `WAVEFORMATEX*` |
| `+0x08` | `HMMIO` file handle |
| `+0x0C` | data `MMCKINFO` |
| `+0x20` | RIFF `MMCKINFO` |
| `+0x2C` | RIFF data offset used before data-chunk descend |

### Vtables

| Vtable | Slots verified by Wave537 |
| --- | --- |
| `0x005dfc4c` | scalar deleting destructor, `Open`, `Read`, `CloseHandle`, `HasFormat`, `GetSampleRate`, `GetChannelCount` |
| `0x005dfc6c` | base scalar deleting destructor plus purecall slots |

The table-adjacent values after those observed slots are not promoted as function boundaries.

## Functions (13 saved targets)

| Address | Saved state | Notes |
| --- | --- | --- |
| `0x00505210` | `int __cdecl WavRead__ReadMMIO(void * hmmio, void * riff_chunk, void * * wave_format_out)` | Parses RIFF/WAVE/fmt, allocates/copies WAVEFORMATEX, frees on late failure. |
| `0x005053d0` | `int __cdecl WavRead__WaveReadFile(void * hmmio, uint byte_count, byte * out_buffer, void * data_chunk, uint * bytes_read_out)` | Buffered MMIO data reader; clamps against data-chunk remaining bytes and writes actual byte count. |
| `0x005054a0` | `void __fastcall CWaveSoundRead__Constructor(void * this)` | Installs concrete vtable `0x005dfc4c`, clears format pointer. |
| `0x005054b0` | `bool __fastcall CWaveSoundRead__HasFormat(void * this)` | Wave537-created vtable slot 4; returns `this+0x04 != null`. |
| `0x005054c0` | `uint __fastcall CWaveSoundRead__GetSampleRate(void * this)` | Wave537-created vtable slot 5; reads WAVEFORMATEX `nSamplesPerSec` at `+0x04`. |
| `0x005054d0` | `uint __fastcall CWaveSoundRead__GetChannelCount(void * this)` | Wave537-created vtable slot 6; zero-extends WAVEFORMATEX `nChannels` at `+0x02`. |
| `0x005054e0` | `void * __thiscall CWaveSoundRead__ScalarDeletingDestructor(void * this, byte delete_flags)` | Renamed from stale generic destructor; closes resources then optionally frees `this`. |
| `0x00505500` | `void __fastcall CWaveSoundRead__Close(void * this)` | Closes HMMIO handle, frees format pointer, restores base vtable. |
| `0x00505570` | `void __fastcall CWaveSoundRead__BaseConstructor(void * this)` | Installs base vtable `0x005dfc6c`. |
| `0x00505580` | `void * __thiscall CWaveSoundRead__BaseScalarDeletingDestructor(void * this, byte delete_flags)` | Wave537-created base-vtable slot 0 scalar deleting destructor. |
| `0x005055b0` | `int __thiscall CWaveSoundRead__Open(void * this, char * filename)` | Opens with `mmioOpenA`, calls `ReadMMIO`, seeks to RIFF data offset, descends into data chunk. |
| `0x00505680` | `int __thiscall CWaveSoundRead__Read(void * this, uint byte_count, byte * out_buffer, uint * bytes_read_out)` | Wave537-created vtable slot 2 wrapper into `WavRead__WaveReadFile`. |
| `0x005056b0` | `int __fastcall CWaveSoundRead__CloseHandle(void * this)` | Wave537-created vtable slot 3 helper; calls `mmioClose(this+0x08, 0)` and returns `0`. |

## RIFF Chunk IDs

| Chunk | Value |
| --- | ---: |
| `RIFF` | `0x46464952` |
| `WAVE` | `0x45564157` |
| `fmt ` | `0x20746d66` |
| `data` | `0x61746164` |

## Windows API Usage

| Function | Purpose |
| --- | --- |
| `mmioOpenA` | Open multimedia file |
| `mmioClose` | Close multimedia file |
| `mmioRead` | Read from multimedia file |
| `mmioDescend` | Descend into RIFF chunk |
| `mmioAscend` | Ascend from RIFF chunk |
| `mmioSeek` | Seek in multimedia file |
| `mmioGetInfo` | Get mmio buffer info |
| `mmioSetInfo` | Set mmio buffer info |
| `mmioAdvance` | Advance mmio buffer |

## Wave 537 Note (2026-05-18)

Wave537 recovered and hardened thirteen WavRead/CWaveSoundRead targets. `ApplyWavReadWave537.java` reported dry `updated=0 skipped=13 renamed=0 would_rename=1 created=0 would_create=6 missing=0 bad=0`, apply `updated=13 skipped=0 renamed=1 would_rename=0 created=6 would_create=0 missing=0 bad=0`, and final verify dry `updated=0 skipped=13 renamed=0 would_rename=0 created=0 would_create=0 missing=0 bad=0`, with `REPORT: Save succeeded`.

Read-back verified `13` metadata rows, `13` tag rows, `13` target xref rows, `1885` instruction rows, `13` target decompile exports, `14` expected vtable-slot rows, focused probe PASS, npm probe PASS, queue refresh PASS, and backup `[maintainer-local-ghidra-backup-root]\BEA_20260518-072526_post_wave537_wavread_verified` with `19` files, `159288199` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

The refreshed queue reports `6089` total functions, `2622` commented, `3467` commentless, `1538` exact-undefined signatures, and `1315` `param_N` signatures. Runtime WAV loading, DirectSound integration, exact source-body identity, complete layouts, BEA patching, and rebuild parity remain deferred.

## Related Systems

- `pcsoundmanager.cpp` owns the `CWaveSoundRead*` at observed `CPCSoundManager +0x2C8` during PC sound initialization.
- `SoundManager.cpp` and `pcsoundmanager.cpp` remain the broader sample/effect/channel orchestration surfaces.
