# Ghidra SoundManager Backend Tail Wave853 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004e0f70` comment correction; `0x004e1200` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `soundmanager-backend-tail-wave853`

Wave853 SoundManager backend tail saved names, signatures, comments, and tags for eighteen important PC audio backend connector rows from `0x005168d0 CPCSample__dtor` through `0x00517d00 CSoundManager__LoadCompressedSampleBank`. The pass corrected two stale CPCSample destructor names, corrected twelve stale CSoundManager labels to source-backed CPCSoundManager backend labels, hardened four signatures, and made no function-boundary changes or executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005168d0 CPCSample__dtor` | `void __fastcall CPCSample__dtor(void * this)` | Corrects stale `CPCSoundManager__dtor`; installs the CPCSample vtable, calls `CSoundManager__KillAllInstancesOfSample`, frees sample data at `this+0x78`, releases the DirectSound buffer at `this+0x80`, and chains to `CSample__DestructorBody`. |
| `0x00516960 CPCSample__scalar_deleting_dtor` | `void * __thiscall CPCSample__scalar_deleting_dtor(void * this, uchar free_flag)` | Corrects stale `CPCSoundManager__scalar_deleting_dtor`; DATA xref `0x005e4988` is CPCSample vtable slot 0. |
| `0x005171e0 CPCSoundManager__DeviceShutdown` | `void __fastcall CPCSoundManager__DeviceShutdown(void * this)` | Corrects stale `CSoundManager__ReleaseAllVoiceBuffers`; releases DS3D buffers, DirectSound buffers, the DirectSound object, and the wave-reader/helper. |
| `0x00517260 CPCSoundManager__DeviceReset` | `void __fastcall CPCSoundManager__DeviceReset(void * this)` | Corrects stale `CSoundManager__StopAllActiveVoices`; stops non-null DirectSound buffers without releasing them. |
| `0x00517290 CPCSoundManager__LoadSampleFromBuffer_StubFail` | `void * __stdcall CPCSoundManager__LoadSampleFromBuffer_StubFail(void * mem_buffer, int music)` | Corrects stale sample-create stub label and signature; body is `XOR EAX,EAX; RET 0x8`, matching the unimplemented PC source stub. |
| `0x00517790 CPCSoundManager__PlaySound` | `void __thiscall CPCSoundManager__PlaySound(void * this, void * sound_event)` | Corrects stale channel-play label; duplicates the sample DirectSound buffer, queries DS3D, seeds sound position/params, seeks, plays, and marks the event playing. |
| `0x00517960` through `0x005179b0` | `CPCSoundManager__UnPauseSound`, `CPCSoundManager__PauseSound`, `CPCSoundManager__StopSound` | Corrects stale channel loop/stop/release labels; source-backed pause, unpause, and stop/release channel behavior. |
| `0x00517a20 CPCSoundManager__UpdateGlobals` / `0x00517c40 CPCSoundManager__UpdatesDone` | Listener update/commit helpers | Build and commit deferred DirectSound3D listener state through the listener at `this+0x2c4`. |
| `0x00517ae0 CPCSoundManager__UpdateSound` | `void __thiscall CPCSoundManager__UpdateSound(void * this, void * sound_event, int first_time)` | Corrects stale channel-params label; updates DS3D position/velocity, attenuation/volume, frequency, and non-looping completion state. |
| `0x00517c60 CPCSoundManager__GetSampleLength` / `0x00517cb0 CPCSoundManager__FindFreeChannel` | Sample timing and channel allocation helpers | Source-backed sample length and free-channel selection over active events and DirectSound slots. |
| `0x00517d00 CSoundManager__LoadCompressedSampleBank` | `void __thiscall CSoundManager__LoadCompressedSampleBank(void * this, char stream_mode)` | Reads the cached XAP path at `this+0x88`, opens a mem-buffer, logs XAP/cache diagnostics, loads sample records, and calls `CSoundManager__CreateSample`. |

Read-back evidence:

- `ApplySoundManagerBackendTailWave853.java dry`: `updated=0 skipped=18 renamed=0 would_rename=14 signature_updated=4 comment_only_updated=18 missing=0 bad=0`
- `ApplySoundManagerBackendTailWave853.java apply`: `updated=18 skipped=0 renamed=14 would_rename=14 signature_updated=4 comment_only_updated=18 missing=0 bad=0`
- `ApplySoundManagerBackendTailWave853.java final dry`: `updated=0 skipped=18 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `18` metadata rows, `18` tag rows, `40` xref rows, `666` instruction rows, and `18` decompile rows.
- Additional read-only evidence: `12` context metadata rows, `12` context decompile rows, `32` vtable rows, `10` string dumps, and source-context hits from `pcsoundmanager.cpp`, `pcsoundmanager.h`, `SoundManager.cpp`, and `SoundManager.h`.
- Queue after Wave853: `6098` total functions, `5754` commented, `344` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy `5754/6098 = 94.36%`, strict clean-signature proxy `5754/6098 = 94.36%`.
- Next raw commentless row: `0x0051a6a0 CFastVB__RenderIndexedImmediate`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-101054_post_wave853_soundmanager_backend_tail_verified`, `19` files, `172133255` bytes, `DiffCount=0`.

What this proves:

- The eighteen target rows exist in the saved Ghidra project with the Wave853 names, signatures, comments, and tags above.
- These are important static connectors for CPCSample lifetime, DirectSound device shutdown/reset, sample creation stubs, playback/pause/stop, 3D listener commit, per-event mixing updates, sample duration, free-channel allocation, and compressed XAP sample-bank loading.

What remains unproven:

- Runtime DirectSound playback, pause/unpause, shutdown/reset, listener, channel allocation, sample-bank loading, and sample lifetime behavior.
- Exact `CPCSoundManager`, `CSoundManager`, `CPCSample`, `CSoundEvent`, DirectSound/DS3D interface, and XAP schemas.
- BEA patching behavior.
- Rebuild parity.
