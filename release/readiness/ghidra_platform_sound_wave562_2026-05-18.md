# Ghidra Platform / PC Sound Wave562 Readiness - 2026-05-18

## Scope

Wave562 hardened nine adjacent PCPlatform / PCSound targets from `0x005154e0` through `0x00517fa0`:

- `PCPlatform__Init`
- `PCPlatform__LoadFonts`
- `CPCPlatform__UnloadFonts`
- `CPCSoundManager__Init`
- `CPCSoundManager__CreateSampleFromFile`
- `CPCSoundManager__CreateSoundBuffer`
- `CPCSoundManager__ConvertAudioFormat`
- `CPCSoundManager__CreateSampleFromData`
- `CPCSoundManager__DecodeADPCM`

## Evidence

`ApplyPlatformSoundWave562.java` dry/apply/final dry ran serialized through headless Ghidra. Dry reported `updated=0 skipped=9 missing=0 bad=0`; apply reported `updated=9 skipped=0 missing=0 bad=0`; final dry reported `updated=0 skipped=9 missing=0 bad=0`, all with `REPORT: Save succeeded`.

Read-back exports verified `9` metadata rows, `9` tag rows, `13` xref rows, `2025` target instruction rows, and `9` decompile rows. Focused probe and npm wrapper both passed. The refreshed queue reports `6089` total functions, `2791` commented, `3298` commentless, `1503` exact-undefined signatures, `1185` `param_N` signatures, and strict clean-signature proxy `2737/6089 = 44.95%`.

The post-wave project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260518-194746_post_wave562_platform_sound_verified` with `19` files, `159812487` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Limits

This is static saved-Ghidra evidence only. Runtime DirectSound device initialization, sample loading/playback, Bink voice playback, ADPCM decode quality, exact CPCPlatform/CPCSoundManager/CPCSample layouts, BEA launch behavior, patching, and rebuild parity remain unproven.
