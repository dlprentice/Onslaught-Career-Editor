# OggLoader.cpp

Wave1219 final current-risk closure note: `COggLoader__readerSubobject_dtor_body`, `COggLoader__ctor_base`, and `COggFileRead__scalar_deleting_dtor` remain mapped to Ogg loader/file-reader construction and cleanup; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`. Runtime Ogg/audio streaming behavior, exact layouts, and rebuild parity remain separate proof.

> Retail static evidence bucket for `COggLoader` helpers in `BEA.exe`.

> **Queue status (2026-05-31):** Ghidra export-contract closure **6238/6238** (Wave1015: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Wave453 corrected the Ogg loader cluster immediately before the MessageBox/CMessage queue code. Wave568 extended the bucket to the adjacent Ogg/Vorbis stream and `COggFileRead` implementation at `0x00523df0` through `0x00524820`, including four recovered `COggFileRead` vtable-slot boundaries. The evidence is static retail Ghidra evidence only; it does not prove runtime Ogg streaming or exact source body identity.

Wave908 audio/media/cutscene static review (`audio-media-cutscene-static-review-wave908`) keeps the Ogg loader and reader rows inside the static-coherent audio/media/cutscene/camera core. The read-only slice records `COggLoader 4`, `COggFileRead 9`, and `OggVorbisStream 2` rows in the `171` selected-row, `26` family evidence set. Anchors include `COggLoader__ThreadProc_ReadPathIntoBuffer`, `COggFileRead__OpenFileAndPrimeDecoder`, `COggFileRead__ReadDecodedPcm`, and `OggVorbisStream__ReadPcmSamples`, connecting the waiting-thread path, buffered Ogg reader, and Vorbis PCM decode loop. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified`. Runtime Ogg streaming/audio playback, exact reader/source identity, patch behavior, and rebuild parity remain separate proof.

Wave1015 (`ogg-message-lifecycle-review-wave1015`) re-read the adjacent Ogg loader lifecycle rows with fresh metadata/tags/xrefs/instructions/decompile and no mutation. The pass verified `0x004b6cd0 COggLoader__readerSubobject_dtor_body`, `0x004b6d30 COggLoader__ctor_base`, `0x004b6d90 COggLoader__ThreadProc_ReadPathIntoBuffer`, and `0x004b6df0 COggLoader__readerSubobject_scalar_deleting_dtor` against `CWaitingThread__ctor_base`, `CWaitingThread__dtor_body`, and Wave568 `COggFileRead` reader context. It also re-read adjacent `CMessage` rows in `MessageBox.cpp`; Wave911 focused progress advanced to `511/1408 = 36.29%`, expanded static surface progress to `736/1493 = 49.30%`, and top-500 coverage to `437/500 = 87.40%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-192131_post_wave1015_ogg_message_lifecycle_review_verified`. Runtime Ogg streaming/audio playback, exact source-body identity, concrete `COggLoader`/`COggFileRead` layouts, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1015; ogg-message-lifecycle-review-wave1015; 0x004b6cd0 COggLoader__readerSubobject_dtor_body; 0x004b6d30 COggLoader__ctor_base; 0x004b6d90 COggLoader__ThreadProc_ReadPathIntoBuffer; 0x004b6df0 COggLoader__readerSubobject_scalar_deleting_dtor; 0x004b6e50 CMessage__ctor_base; 0x004b6f10 CMessage__scalar_deleting_dtor; 0x004b7160 CMessage__dtor_base; 511/1408 = 36.29%; 736/1493 = 49.30%; 437/500 = 87.40%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-192131_post_wave1015_ogg_message_lifecycle_review_verified; no mutation.

## Functions

| Address | Name | Status | Notes |
| --- | --- | --- | --- |
| `0x004b6cd0` | `COggLoader__readerSubobject_dtor_body` | SAVED | Wave453 corrected the former `COggLoader__InitReadAndWaitThread` label. The body is reached by the reader-subobject scalar-deleting destructor, calls the current `COggFileRead` cleanup label, then calls the `CWaitingThread` cleanup label. |
| `0x004b6d30` | `COggLoader__ctor_base` | SAVED | Wave453 corrected the ctor-like label to a base constructor. It calls `CWaitingThread` construction on the base object, constructs the `COggFileRead`-style reader at `+0x20`, installs base and reader-subobject vtables, and returns `this`. |
| `0x004b6d90` | `COggLoader__ThreadProc_ReadPathIntoBuffer` | SAVED | Wave453 corrected the vfunc-style label. The waiting-thread body checks the path byte at `+0x102310`, opens the reader subobject at `+0x20`, reads up to `0x100000` bytes into the buffer at `+0x2310`, stores byte count/status at `+0x102414`, and closes the reader on success. |
| `0x004b6df0` | `COggLoader__readerSubobject_scalar_deleting_dtor` | SAVED | Wave453 corrected the vfunc-style label and final read-back signature. `ret 0x4` confirms one stack `flags` argument; the wrapper calls `COggLoader__readerSubobject_dtor_body`, conditionally frees the adjusted base pointer when flag bit 0 is set, and returns that adjusted pointer. |
| `0x00523df0` | `OggVorbisStream__InitDecoder` | SAVED | Wave568 hardened the stream initializer that reads Vorbis headers, sets stream/comment/info/block state, and records decode fields. No source-parity tag was applied. |
| `0x00524180` | `OggVorbisStream__ReadPcmSamples` | SAVED | Wave568 hardened the PCM decode loop. `RET 0x8` proves output buffer plus requested byte count; the prior third `param_N` was treated as a decompiler artifact. |
| `0x005245a0` | `COggFileRead__ctor_base` | SAVED | Wave568 corrected the reader constructor. It installs vtable `0x005e4a44`, initializes the open-state/stream fields, and is called by `COggLoader__ctor_base` plus `PCPlatform__InitAsyncMusicStream`. |
| `0x005245e0` | `COggFileRead__scalar_deleting_dtor` | SAVED | Wave568 corrected the scalar-deleting destructor wrapper; `RET 0x4` confirms `this, flags`, and flag bit 0 controls memory free. |
| `0x00524600` | `COggFileRead__dtor_body` | SAVED | Wave568 hardened the destructor/close body that clears Ogg/Vorbis state, closes the file when present, and restores the base `CWaveSoundRead` vtable. |
| `0x005246a0` | `COggFileRead__OpenFileAndPrimeDecoder` | SAVED | Wave568 corrected vtable slot 1. The body opens the path, uses the base reader open/read hook, and primes the Ogg/Vorbis decoder through `OggVorbisStream__ReadPcmSamples(this, null, 0)`. |
| `0x00524710` | `COggFileRead__ReadDecodedPcm` | SAVED | Wave568 recovered the slot 2 boundary and is argument-order-corrected: the final signature is `this, requested_byte_count, out_pcm_bytes, out_bytes_read`, then the body forwards to `OggVorbisStream__ReadPcmSamples(this, out_pcm_bytes, requested_byte_count)`. |
| `0x00524770` | `COggFileRead__CloseAndReset` | SAVED | Wave568 corrected vtable slot 3 close/reset behavior and file/stream cleanup. |
| `0x00524800` | `COggFileRead__IsOpen` | SAVED | Wave568 recovered vtable slot 4 as the open-state field reader at `+0x2008`. |
| `0x00524810` | `COggFileRead__GetSampleRate` | SAVED | Wave568 recovered vtable slot 5 as the sample-rate field reader at `+0x21d0`. |
| `0x00524820` | `COggFileRead__GetChannelCount` | SAVED | Wave568 recovered vtable slot 6 as the channel-count field reader at `+0x21cc`. |

## Wave568 Evidence Boundary

Wave568 saved names/signatures/comments/tags for `11` Ogg/Vorbis / `COggFileRead` targets at `0x00523df0`, `0x00524180`, `0x005245a0`, `0x005245e0`, `0x00524600`, `0x005246a0`, `0x00524710`, `0x00524770`, `0x00524800`, `0x00524810`, and `0x00524820`. The pass created/recovered four missing `COggFileRead` boundaries and renamed five stale or generic rows. Read-back artifacts are under `subagents/ghidra-static-reaudit/wave568-ogg-vorbis-stream-00523df0/`; public-safe readiness evidence is at `release/readiness/ghidra_ogg_vorbis_wave568_2026-05-19.md`.

The first post-readback snapshot is preserved under `post_before_slot2_argument_order_correction/`. It exposed that slot 2 takes the requested byte count before the output buffer; `tools/ApplyOggVorbisWave568Slot2Correction.java` then corrected `COggFileRead__ReadDecodedPcm` and tagged it `argument-order-corrected`. Runtime Ogg streaming/audio playback, exact `COggFileRead` layout, exact source identity, BEA launch behavior, game patching, and rebuild parity remain unproven by this wave.

## Wave1015 Evidence Boundary

Wave1015 re-read the Wave453 Ogg loader rows plus Wave568/571 reader/thread context with no Ghidra mutation. Target exports verified `7` metadata rows, `7` tag rows, `14` xref rows, `195` body-instruction rows, and `7` decompile rows across the combined Ogg/message primary set; context exports verified `17` metadata rows, `549` xref rows, `548` body-instruction rows, and `17` decompile rows. The Ogg-specific static evidence confirms the reader-subobject destructor calls `COggFileRead__dtor_body` and `CWaitingThread__dtor_body`, the constructor builds the waiting-thread base and `COggFileRead` reader at `+0x20`, the thread body reads from path `+0x102310` into buffer `+0x2310` with count/status `+0x102414`, and `0x004b6df0` retains the corrected `this, flags` scalar-deleting destructor shape with `RET 0x4`.

Runtime Ogg streaming/audio playback, exact `COggLoader`/`COggFileRead` layouts, exact source identity, BEA launch behavior, game patching, and rebuild parity remain unproven by this wave.

## Wave453 Evidence Boundary

Wave453 saved names/signatures/comments/tags for `4` COggLoader targets at `0x004b6cd0`, `0x004b6d30`, `0x004b6d90`, and `0x004b6df0`. Dry/apply/verify-dry and post-export probes passed, with read-back artifacts under `subagents/ghidra-static-reaudit/wave453-ogg-message-current/` and public-safe readiness evidence at `release/readiness/ghidra_ogg_message_wave453_2026-05-16.md`.

The initial apply exposed a scalar-deleting destructor signature issue at `0x004b6df0`; the final corrective apply/read-back records the intended `this, flags` form. Runtime streaming/audio playback, exact COggLoader/COggFileRead layout, exact source identity, BEA launch behavior, game patching, and rebuild parity remain unproven by this wave.
