# Ghidra CSoundManager Sample Playback Wave501 Readiness Note

Status: static RE evidence captured
Date: 2026-05-17
Scope: public-safe static Ghidra correction note

Wave501 saved static Ghidra name/signature/comment/tag hardening for seven `CSample` / `CSoundManager` sample lifecycle and playback helpers:

| Address | Saved state |
| --- | --- |
| `0x004dff30` | `void __fastcall CSample__DestructorBody(void * this)` |
| `0x004dffc0` | `void * __thiscall CSample__DeletingDestructor(void * this, int delete_flags, int unused)` |
| `0x004e0890` | `void * __thiscall CSoundManager__CreateSample(void * this, char * name, int channel_type, void * sample_source, int reuse_existing)` |
| `0x004e0a00` | `void * __thiscall CSoundManager__GetOrCreateSample(void * this, char * name, int channel_type, int reload_if_exists)` |
| `0x004e0a90` | `void __thiscall CSoundManager__PlayNamedSample(void * this, char * sample_name, void * owner, float volume, int tracking_type, int once, float fade_seconds, float from_point_seconds, float to_point_seconds, int repeat, float pitch, int inform_owner_when_complete, int ignore_owner_pos, int sound_type)` |
| `0x004e0b30` | `void __thiscall CSoundManager__PlaySample(void * this, void * sample, void * owner, float volume, int tracking_type, int once, float fade_seconds, float from_point_seconds, float to_point_seconds, int repeat, float pitch, int inform_owner_when_complete, int ignore_owner_pos, int sound_type)` |
| `0x004e0bd0` | `void * __thiscall CSoundManager__StartSoundEvent(void * this, void * owner, void * sample, int tracking_type, float volume, float fade_seconds, float from_point_seconds, float to_point_seconds, int loop, float pitch, int inform_owner_when_complete, int ignore_owner_pos, int sound_type)` |

Evidence:

- Apply script: `tools/ApplyCSoundManagerSamplePlaybackWave501.java`
- Focused probe: `tools/ghidra_csoundmanager_sample_playback_wave501_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave501-csoundmanager-sample-playback-004dff30/`
- Dry run: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`
- Apply: `updated=7 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`
- Final verify dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- All Ghidra runs reported `REPORT: Save succeeded`.
- Read-back verified `7` metadata rows, `7` tag rows, `20` xref rows, `847` instruction rows, and `7` decompile exports.
- Focused probe passed: `py -3 tools\ghidra_csoundmanager_sample_playback_wave501_probe.py --check`
- npm probe passed: `cmd.exe /c npm run test:ghidra-csoundmanager-sample-playback-wave501`
- Static queue check passed: `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-132737_post_wave501_csoundmanager_sample_playback_verified`

Queue snapshot after Wave501:

| Metric | Value |
| --- | ---: |
| Function objects | 6078 |
| Functions with non-empty function comments | 2284 |
| Commentless functions | 3794 |
| `undefined` signatures | 1653 |
| Signatures still using `param_N` names | 1502 |
| Comment-backed proxy | `2284/6078 = 37.58%` |
| Strict comment-plus-clean-signature proxy | `2227/6078 = 36.64%` |

Backup verification:

| Metric | Value |
| --- | ---: |
| Source files | 19 |
| Backup files | 19 |
| Source bytes | 157846407 |
| Backup bytes | 157846407 |
| Missing files | 0 |
| Extra files | 0 |
| Hash differences | 0 |

Not proven by this wave:

- Exact `CSample`, `CSoundManager`, `CSoundEvent`, backend sample-source, channel, or active-reader layouts.
- Runtime sample unload, sample loading, playback, mixing, distance attenuation, or once-only behavior.
- BEA launch behavior, executable patching behavior, or rebuild parity.

Nearby exclusions:

- Wave501 deliberately stayed on sample lifecycle/playback wrappers and `StartSoundEvent`.
- `CSoundManager__Init`, `CSoundManager__GetDebugMenuText`, `CSoundManager__LoadSoundDefinitions`, and the nearby monitor/BattleEngine sound-event helper cluster remain queued for later passes.
