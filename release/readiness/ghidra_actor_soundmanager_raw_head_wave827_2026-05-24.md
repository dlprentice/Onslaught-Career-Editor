# Ghidra Actor/SoundManager Raw Head Wave827 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `actor-soundmanager-raw-head-wave827`

Wave827 actor/SoundManager raw head saved comments, tags, and bounded name/signature corrections for six adjacent raw commentless functions from `0x004df520 CActor__dtor_base_Thunk` through `0x004e0820 CEffect__scalar_deleting_dtor`. The pass made no function-boundary changes and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004df520 CActor__dtor_base_Thunk` | One-instruction jump thunk to the already-commented `0x004013d0 CActor__dtor_base` body; xref comes from `0x004bfd00 CActorBase__shared_scalar_deleting_dtor_004bfd00`. |
| `0x004e0300 CSoundManager__UpdateVolumeForAllSoundEvents` | Source-backed correction from `CSoundManager__UpdateAllSoundVolumes`; walks `mFirstSoundEvent` at `this+0x0c`, writes event volume fields at `+0x68/+0x64`, and calls `CSoundManager__UpdateChannelParams` for active channels. |
| `0x004e04c0 CSoundManager__SetMasterVolume` | Retail decompile sets the master-volume field at `this+0x20`, logs `sound master volume`, writes `CAREER_mSoundVolume`, and recomputes active event volumes. |
| `0x004e06b0 CSoundManager__DeleteAllSamples` | Source-backed correction from `CSoundManager__StopAllStreams`; walks the sample list at `this+0x00`, preserves next from `sample+0x74`, calls the sample virtual deleting destructor with flag `1`, and clears the list head. |
| `0x004e06e0 CSoundManager__Shutdown` | Teardown called from `CLTShell__ShutdownRuntimeAndReleaseResources`; returns active events to the pool, frees pool entries, deletes samples, releases backend voice buffers, frees the debug menu, walks the CEffect list, and clears `mInitialised`. |
| `0x004e0820 CEffect__scalar_deleting_dtor` | Source-backed correction from `CSoundDefinition__Destructor`; recursively deletes `CEffect::mChainedEffect` at `this+0xd4`, unlinks from the global effect list via `this+0xd8`, optionally frees when `flags&1`, and returns `this`. |

Read-back evidence:

- `ApplyActorSoundManagerRawHeadWave827.java dry`: `updated=0 skipped=6 renamed=0 would_rename=4 signature_updated=5 comment_only_updated=1 missing=0 bad=0`
- `ApplyActorSoundManagerRawHeadWave827.java apply`: `updated=6 skipped=0 renamed=4 would_rename=0 signature_updated=4 comment_only_updated=2 missing=0 bad=0`
- `ApplyActorSoundManagerRawHeadWave827.java final dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 6 metadata rows, 6 tag rows, 9 xref rows, 1806 target instruction rows, 6 target decompile rows, 11 context metadata rows, 3311 context instruction rows, and 11 context decompile rows.
- Queue after Wave827: 6098 total, 5640 commented, 458 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5640/6098 = 92.49%`, strict clean-signature proxy `5640/6098 = 92.49%`.
- Next raw commentless row: `0x004e1260 CMonitor__UpdateTrackedValueAndDirection`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-203238_post_wave827_actor_soundmanager_raw_head_verified`, 19 files, 171576199 bytes, `DiffCount=0`.

What this proves:

- The six target function rows exist in the saved Ghidra project with the `actor-soundmanager-raw-head-wave827` and `wave827-readback-verified` tags.
- The saved SoundManager signatures use the observed ECX receiver where retail decompile previously had locked unknown calling conventions.
- `CSoundManager__UpdateVolumeForAllSoundEvents`, `CSoundManager__DeleteAllSamples`, and `CEffect__scalar_deleting_dtor` are source-backed name corrections for stale labels.
- `CActor__dtor_base_Thunk` is separated from the already-commented body at `0x004013d0`.

What remains unproven:

- Exact `CSoundManager`, `CSoundEvent`, `CSample`, and `CEffect` field schemas.
- Runtime audio behavior.
- Runtime lifetime behavior.
- BEA patching behavior.
- Rebuild parity.
