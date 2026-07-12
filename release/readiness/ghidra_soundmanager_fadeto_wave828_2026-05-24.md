# Ghidra SoundManager FadeTo Wave828 Readiness Note

> **Owner/name supersession (2026-07-12):** Wave828 remains a historical
> callsite/read-back record. Current static evidence identifies `0x004081c0`
> as `CBattleEngine__Move`, not `CMonitor__Process`; the observed sound-manager
> call remains evidence within that body. See the
> [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `soundmanager-fadeto-wave828`

Wave828 SoundManager FadeTo corrected the raw commentless head at `0x004e1260` from the stale `CMonitor__UpdateTrackedValueAndDirection` label to `CSoundManager__FadeTo`, with the saved signature `void __thiscall CSoundManager__FadeTo(void * this, void * sample, float fade_value, float speed, void * owner)`. The pass made no function-boundary changes and no executable-byte changes.

Static evidence:

| Address | Evidence |
| --- | --- |
| `0x004e1260 CSoundManager__FadeTo` | Source-aligns to `CSoundManager::FadeTo(const CSample *sample, float fadeval, float speed, IAudibleThing *owner)` from `references/Onslaught/SoundManager.cpp`. |
| `0x004e1260 CSoundManager__FadeTo` | Retail body walks the active sound-event list rooted at `this+0x0c`, matches sample at `event+0x0c` and owner reader at `event+0x00`, writes fade destination at `event+0x28`, and writes fade speed at `event+0x24` as `+/-speed` depending on current subvolume at `event+0x20`. |
| `0x004081c0 CMonitor__Process` | Calls `CSoundManager__FadeTo(&DAT_00896988, event+0x0c sample, 0.0, 0.02, monitor)` at `0x00408d56`. |
| `0x00409950 CMonitor__UpdateSoundEventPlaybackForReader` | Calls the fade helper at `0x00409ad8`, `0x00409b0b`, and `0x00409b3a` for monitor sound-event state changes. |
| `0x0040a580 CBattleEngine__Morph` | Calls the fade helper at `0x0040a6aa` and `0x0040a878`, matching source `BattleEngine.cpp` fade-out/fade-in transform sound evidence. |
| `0x0040eb50 CMonitor__FlushTrackedList_1D4` | Calls the fade helper at `0x0040ebd2` when flushing tracked sound context. |

Read-back evidence:

- `ApplySoundManagerFadeToWave828.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplySoundManagerFadeToWave828.java apply`: `READBACK_OK` for `0x004e1260 CSoundManager__FadeTo`, then `updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`.
- The first apply log also records a redundant explicit-save `Unable to lock due to active transaction` script error after read-back; the script was corrected to rely on the headless save path.
- `ApplySoundManagerFadeToWave828.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Fixed-script clean read-back pass: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with no script error.
- Post exports: 16 context metadata rows, 16 context tag rows, 134 xref rows, 592 context instruction rows, 16 context decompile rows, and 4 caller decompile rows.
- Queue after Wave828: `6098` total functions, `5641` commented, `457` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed proxy `5641/6098 = 92.51%`, strict clean-signature proxy `5641/6098 = 92.51%`.
- Next raw commentless row: `0x004eb1e0 CGame__ResetRenderStateForWorldRender`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-210153_post_wave828_soundmanager_fadeto_verified`, 19 files, 171576199 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra row at `0x004e1260` now has the `CSoundManager__FadeTo` name, source-aligned signature, bounded comment, and `soundmanager-fadeto-wave828` / `wave828-readback-verified` tags.
- The observed callers and source references support the SoundManager fade helper identity.
- The queue snapshot now has one fewer raw commentless function than Wave827.

What remains unproven:

- Exact `CSoundManager`, `CSoundEvent`, `CSample`, and active-reader field schemas.
- Runtime audio fade behavior.
- BEA patching behavior.
- Rebuild parity.
