# Ghidra Message Voice Pump Wave818 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `message-voice-pump-wave818`

Wave818 message voice pump saved a comment/tag/signature correction for `0x004b7d90 CGame__PumpBinkVoiceSampleQueue`. The pass made no rename, no function-boundary change, and no executable-byte change.

Representative evidence:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004b7d90 CGame__PumpBinkVoiceSampleQueue` | `void __thiscall CGame__PumpBinkVoiceSampleQueue(void * this)` | `CGame__Update` calls this row from `0x0046ea77` after loading `ECX` from game state `+0x2ec`; the body uses global Bink/audio queue state, gates on `DAT_008a9ac4`, `DAT_008a9ac0`, and `DAT_00704e74`, waits for `CBinkOpenThread__IsRunning(&DAT_00704f78)`, releases prior queued sample `DAT_008073d0`, can call `FatalError__ExitWithLocalizedPrefix_A`, creates a sample through `CPCSoundManager__CreateSampleFromData(&DAT_00707288, DAT_0080738c, 0, NULL)`, optionally plays it through `CSoundManager__PlaySample(&DAT_00896988, ...)`, clears `DAT_00704e74`, and unbinds active reader `DAT_00704e70`. |

Read-back evidence:

- `ApplyMessageVoicePumpWave818.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyMessageVoicePumpWave818.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0`, with `REPORT: Save succeeded`
- `ApplyMessageVoicePumpWave818.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 69 target instruction rows, 56 callsite instruction rows, 7 helper metadata rows, and 1 decompile row.
- Queue after Wave818: 6098 total, 5606 commented, 492 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5606/6098 = 91.93%`, strict clean-signature proxy `5606/6098 = 91.93%`.
- Next raw commentless row: `0x004bc2d0 CWorld__ClearDynamicOccupancySet`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-161634_post_wave818_message_voice_pump_verified`, 19 files, 171379591 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved signature is `void __thiscall CGame__PumpBinkVoiceSampleQueue(void * this)`.
- The saved comment and tags include `message-voice-pump-wave818` and `wave818-readback-verified`.
- The observed behavior is static retail Ghidra metadata/decompile/xref/instruction evidence tied to existing Bink-thread, PC sound backend, sound-manager playback, fatal-error, and active-reader helper metadata.

What remains unproven:

- Exact global names/layouts.
- Exact source-body identity.
- Runtime Bink/voice playback behavior.
- BEA patching behavior.
- Rebuild parity.
