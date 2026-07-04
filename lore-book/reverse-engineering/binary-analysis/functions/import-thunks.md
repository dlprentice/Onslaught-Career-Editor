# Import Thunks Function Mappings

> Static Ghidra notes for external import thunks in the Steam retail `BEA.exe`.
> Last updated: 2026-05-22

## Overview

This page records import-thunk evidence only. The rows below are six-byte retail thunks that jump through IAT slots into Windows or third-party libraries. They are useful for decompile readability and callsite typing, but they do not prove runtime library behavior or exact third-party library versions.

## Wave740 DInput/CRT Tail Static Read-Back Note

Wave740 DInput/CRT tail hardened the later `DINPUT8.DLL` thunk at `0x005d04e0` as part of the DInput/CRT tail pass with the `dinput-crt-tail-wave740` and `wave740-readback-verified` tags.

| Address | Function | Saved Ghidra state | Evidence |
| --- | --- | --- | --- |
| `0x005d04e0 DirectInput8Create` | `DirectInput8Create` | `int __stdcall DirectInput8Create(void * hinstance, uint directinput_version, void * riid_directinput8, void * * directinput_out, void * outer_unknown)` | Six-byte thunk to IAT `0x005d8020`; `PlatformInput__InitDirectInput` callsite `0x00513178` pushes hinstance, DirectInput version `0x800`, IID pointer `0x0060c14c`, interface output `ESI`, and null outer pointer. |

Wave740 queue telemetry after this pass is `6098` total, `4361` commented, `1737` commentless, `1214` exact-undefined signatures, `27` `param_N`, comment-backed proxy `4361/6098 = 71.51%`, strict proxy `4303/6098 = 70.56%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005d0f10 Unwind@005d0f10`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-141639_post_wave740_dinput_crt_tail_verified`.

This is static retail import-thunk/API evidence only. Imported DirectInput runtime behavior, device enumeration behavior, BEA patching, and rebuild parity remain deferred.

Cross-doc Wave740 DInput/CRT tail anchors: `0x005d04ec CFEPSaveGame__WideStrCaseInsensitiveCompare`, `0x005d070f CRT__VsnprintfAndTerminate_005d070f`, and `0x005d0eb8 CRT__GetCharTypeMaskCompat`.

## Wave619 Static Read-Back Note

Wave619 hardened the contiguous import-thunk island from `0x0055d5e0` through `0x0055d69a`.

| Address | Function | Saved Ghidra state | Evidence |
| --- | --- | --- | --- |
| `0x0055d5e0` | `DirectSoundCreate8` | `int __stdcall DirectSoundCreate8(void * pcGuidDevice, void * * ppDS8, void * pUnkOuter)` | Six-byte thunk to IAT `0x005d802c`; xrefs include `CPCSoundManager__Init`. |
| `0x0055d5e6` | `DirectSoundEnumerateA` | `int __stdcall DirectSoundEnumerateA(void * pDSEnumCallback, void * pContext)` | Six-byte thunk to IAT `0x005d8028`; xrefs include `CPCSoundManager__Init`. |
| `0x0055d5ec` | `AVIStreamWrite` | `int __stdcall AVIStreamWrite(void * pavi, int lStart, int lSamples, void * lpBuffer, int cbBuffer, uint dwFlags, int * plSampWritten, int * plBytesWritten)` | Six-byte thunk to IAT `0x005d8018`; xref from `CDXEngine__CaptureAviFrame`. |
| `0x0055d5f2` | `uncompress` | `int __cdecl uncompress(void * dest, uint * destLen, void * source, uint sourceLen)` | Six-byte thunk to IAT `0x005d83b8`; xrefs include `CDXMemBuffer__InitFromFile`, `CDXMemBuffer__Skip`, `CDXMemBuffer__Read`, and `CDXMemBuffer__ReadLine`. |
| `0x0055d5f8` | `compress` | `int __cdecl compress(void * dest, uint * destLen, void * source, uint sourceLen)` | Six-byte thunk to IAT `0x005d83bc`; xrefs include `CDXMemBuffer__WriteBytes` and `CDXMemBuffer__Close`. |
| `0x0055d5fe` | `ogg_sync_wrote` | `int __cdecl ogg_sync_wrote(void * oy, int bytes)` | Six-byte thunk to IAT `0x005d8354`; xrefs include `OggVorbisStream__InitDecoder` and `OggVorbisStream__ReadPcmSamples`. |
| `0x0055d604` | `ogg_sync_buffer` | `char * __cdecl ogg_sync_buffer(void * oy, int size)` | Six-byte thunk to IAT `0x005d8358`; xrefs include Ogg/Vorbis stream init and read paths. |
| `0x0055d60a` | `ogg_stream_packetout` | `int __cdecl ogg_stream_packetout(void * os, void * op)` | Six-byte thunk to IAT `0x005d8368`; xrefs include Ogg/Vorbis stream init and read paths. |
| `0x0055d610` | `ogg_stream_pagein` | `int __cdecl ogg_stream_pagein(void * os, void * og)` | Six-byte thunk to IAT `0x005d8360`; xrefs include Ogg/Vorbis stream init and read paths. |
| `0x0055d616` | `ogg_stream_init` | `int __cdecl ogg_stream_init(void * os, int serialno)` | Six-byte thunk to IAT `0x005d8364`; xref from `OggVorbisStream__InitDecoder`. |
| `0x0055d61c` | `ogg_page_serialno` | `int __cdecl ogg_page_serialno(void * og)` | Six-byte thunk to IAT `0x005d8370`; xref from `OggVorbisStream__InitDecoder`. |
| `0x0055d622` | `ogg_sync_pageout` | `int __cdecl ogg_sync_pageout(void * oy, void * og)` | Six-byte thunk to IAT `0x005d8374`; xrefs include Ogg/Vorbis stream init and read paths. |
| `0x0055d628` | `ogg_stream_clear` | `int __cdecl ogg_stream_clear(void * os)` | Six-byte thunk to IAT `0x005d8378`; xrefs include Ogg/Vorbis read, destructor, and close/reset paths. |
| `0x0055d62e` | `ogg_sync_clear` | `int __cdecl ogg_sync_clear(void * oy)` | Six-byte thunk to IAT `0x005d8350`; xrefs include Ogg/Vorbis read and COggFileRead open/close/destructor paths. |
| `0x0055d634` | `ogg_page_eos` | `int __cdecl ogg_page_eos(void * og)` | Six-byte thunk to IAT `0x005d836c`; xref from `OggVorbisStream__ReadPcmSamples`. |
| `0x0055d63a` | `ogg_sync_init` | `int __cdecl ogg_sync_init(void * oy)` | Six-byte thunk to IAT `0x005d835c`; xref from `OggVorbisStream__ReadPcmSamples`. |
| `0x0055d640` | `vorbis_block_init` | `int __cdecl vorbis_block_init(void * v, void * vb)` | Six-byte thunk to IAT `0x005d8380`; xref from `OggVorbisStream__InitDecoder`. |
| `0x0055d646` | `vorbis_synthesis_init` | `int __cdecl vorbis_synthesis_init(void * v, void * vi)` | Six-byte thunk to IAT `0x005d8384`; xref from `OggVorbisStream__InitDecoder`. |
| `0x0055d64c` | `vorbis_synthesis_headerin` | `int __cdecl vorbis_synthesis_headerin(void * vi, void * vc, void * op)` | Six-byte thunk to IAT `0x005d838c`; xrefs from Ogg/Vorbis header parsing. |
| `0x0055d652` | `vorbis_comment_init` | `void __cdecl vorbis_comment_init(void * vc)` | Six-byte thunk to IAT `0x005d8394`; xref from `OggVorbisStream__InitDecoder`. |
| `0x0055d658` | `vorbis_info_init` | `void __cdecl vorbis_info_init(void * vi)` | Six-byte thunk to IAT `0x005d8398`; xref from `OggVorbisStream__InitDecoder`. |
| `0x0055d65e` | `vorbis_info_clear` | `void __cdecl vorbis_info_clear(void * vi)` | Six-byte thunk to IAT `0x005d8390`; xrefs include Ogg/Vorbis read, destructor, and close/reset paths. |
| `0x0055d664` | `vorbis_comment_clear` | `void __cdecl vorbis_comment_clear(void * vc)` | Six-byte thunk to IAT `0x005d83a0`; xrefs include Ogg/Vorbis read, destructor, and close/reset paths. |
| `0x0055d66a` | `vorbis_dsp_clear` | `void __cdecl vorbis_dsp_clear(void * v)` | Six-byte thunk to IAT `0x005d83a4`; xrefs include Ogg/Vorbis read, destructor, and close/reset paths. |
| `0x0055d670` | `vorbis_block_clear` | `int __cdecl vorbis_block_clear(void * vb)` | Six-byte thunk to IAT `0x005d839c`; xrefs include Ogg/Vorbis read, destructor, and close/reset paths. |
| `0x0055d676` | `vorbis_synthesis_read` | `int __cdecl vorbis_synthesis_read(void * v, int samples)` | Six-byte thunk to IAT `0x005d8388`; xref from `OggVorbisStream__ReadPcmSamples`. |
| `0x0055d67c` | `vorbis_synthesis_pcmout` | `int __cdecl vorbis_synthesis_pcmout(void * v, float * * * pcm)` | Six-byte thunk to IAT `0x005d83ac`; xref from `OggVorbisStream__ReadPcmSamples`. |
| `0x0055d682` | `vorbis_synthesis_blockin` | `int __cdecl vorbis_synthesis_blockin(void * v, void * vb)` | Six-byte thunk to IAT `0x005d83a8`; xref from `OggVorbisStream__ReadPcmSamples`. |
| `0x0055d688` | `vorbis_synthesis` | `int __cdecl vorbis_synthesis(void * vb, void * op)` | Six-byte thunk to IAT `0x005d83b0`; xref from `OggVorbisStream__ReadPcmSamples`. |
| `0x0055d68e` | `VerQueryValueA` | `BOOL __stdcall VerQueryValueA(LPCVOID pBlock, LPCSTR lpSubBlock, LPVOID * lplpBuffer, PUINT puLen)` | Six-byte thunk to IAT `0x005d82e0`; existing WinAPI signature retained; xref from `CLTShell__WinMain`. |
| `0x0055d694` | `GetFileVersionInfoA` | `BOOL __stdcall GetFileVersionInfoA(LPCSTR lptstrFilename, DWORD dwHandle, DWORD dwLen, LPVOID lpData)` | Six-byte thunk to IAT `0x005d82dc`; existing WinAPI signature retained; xref from `CLTShell__WinMain`. |
| `0x0055d69a` | `GetFileVersionInfoSizeA` | `DWORD __stdcall GetFileVersionInfoSizeA(LPCSTR lptstrFilename, LPDWORD lpdwHandle)` | Six-byte thunk to IAT `0x005d82d8`; existing WinAPI signature retained; next queue head is `0x0055d6a0 CRT__SehPopExceptionFrameAndJump`. |

## Evidence Sources

- DirectSound/VFW/Version signatures: local Windows SDK headers (`dsound.h`, `Vfw.h`, `winver.h`).
- zlib signatures: local repo/reference zlib header evidence.
- Ogg/Vorbis signatures: local Ogg/Vorbis header evidence.
- IAT slots, thunk bytes, and xrefs: saved Ghidra post-Wave619 exports under `subagents/ghidra-static-reaudit/wave619-import-thunks/`.

## Queue Note

Wave619 moved the queue to `6093` total functions, `3217` commented, `2876` commentless, `1218` exact-undefined signatures, and `1056` `param_N` signatures. The next queue head is `0x0055d6a0 CRT__SehPopExceptionFrameAndJump`.

This is static retail import-thunk/API evidence only. Runtime audio, video capture, compression, Ogg/Vorbis decode, version-resource behavior, concrete third-party library versions, exact third-party structure layouts, BEA patching, and rebuild parity remain deferred.
