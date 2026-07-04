# Ghidra Music Wave454 Evidence

Date: 2026-05-16

## Scope

Wave454 saved Ghidra name/signature/comment/tag corrections for `11` contiguous `CMusic` lifecycle, playback, playlist, selection, and volume targets:

`0x004bb380`, `0x004bb400`, `0x004bb450`, `0x004bb490`, `0x004bb4b0`, `0x004bb530`, `0x004bb6b0`, `0x004bb7c0`, `0x004bb7e0`, `0x004bb8c0`, and `0x004bba10`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave454-music-current/`
- Apply script: `tools/ApplyMusicWave454.java`
- Probe: `tools/ghidra_music_wave454_probe.py`
- Test alias: `npm run test:ghidra-music-wave454`
- Dry summary: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=6 missing=0 bad=0`
- Apply summary: `updated=11 skipped=0 created=0 would_create=0 renamed=6 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `11` metadata rows, `11` tag rows, `39` xref rows, `11` decompile exports, and `979` focused instruction rows.
- Corrected source-parity names: `CMusic__FadeVolumes`, `CMusic__UpdateStatus`, `CMusic__AddToPlayList`, `CMusic__PlayFromList`, `CMusic__PlaySelection`, and `CMusic__SetVolume`.
- Corrected stack-argument signatures for direct play and playlist loading: `CMusic__Play(void * this, char * filename)` and `CMusic__LoadPlaylistFromDir(void * this, char * directory_path)`.
- Kept `CMusic__LoadPlaylistFromDir` behavior-bounded because the retail body is a platform extension-wrapper call using token `0x00630a04`, not full PC-source directory enumeration proof.
- Recorded that retail `CMusic__SetVolume` linearly converts input float into the `0..127` set-volume field, while the PC source tangent-volume path differs.
- Queue after refresh: `6057` functions, `1989` commented, `4068` commentless, `1733` undefined signatures, `1674` `param_N` signatures.
- Current telemetry proxies: comment-backed `1989/6057 = 32.84%`; strict clean-signature `1923/6057 = 31.75%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-141054_post_wave454_music_verified` (`19` files, `156699527` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime music playback, track selection, directory enumeration, audio loudness behavior, concrete `CMusic`/`CSong`/`CPCMusic` layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
