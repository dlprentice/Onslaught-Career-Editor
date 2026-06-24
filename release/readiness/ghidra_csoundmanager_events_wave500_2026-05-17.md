# Ghidra CSoundManager Events Wave500 Readiness Note

Status: static RE evidence captured
Date: 2026-05-17
Scope: public-safe static Ghidra correction note

Wave500 saved static Ghidra signature/comment/tag hardening for ten `CSoundManager` event-lifecycle helpers:

| Address | Saved state |
| --- | --- |
| `0x004e0f70` | `void __stdcall CSoundManager__StopSoundEvent(void * sound_event, int block_until_stopped)` |
| `0x004e0fb0` | `void * __thiscall CSoundManager__AllocateSoundEvent(void * this, int insert_at_top)` |
| `0x004e1040` | `void __thiscall CSoundManager__SortEventList(void * this)` |
| `0x004e1130` | `void __thiscall CSoundManager__KillSamplesForThing(void * this, void * owner)` |
| `0x004e1190` | `void __thiscall CSoundManager__KillSample(void * this, void * owner, void * sample)` |
| `0x004e12b0` | `void __thiscall CSoundManager__KillAllSamples(void * this)` |
| `0x004e1300` | `void __thiscall CSoundManager__PauseAllSamples(void * this)` |
| `0x004e1330` | `void __thiscall CSoundManager__UnPauseAllSamples(void * this)` |
| `0x004e1360` | `void __stdcall CSoundManager__UpdateSoundPosition(void * sound_event, int first_time)` |
| `0x004e18d0` | `void __thiscall CSoundManager__SetPitch(void * this, void * sound_event, float desired_pitch_factor, float fade_time_seconds)` |

Evidence:

- Apply script: `tools/ApplyCSoundManagerEventsWave500.java`
- Focused probe: `tools/ghidra_csoundmanager_events_wave500_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave500-csoundmanager-events-004e0f70/`
- Dry run: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=10 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Final verify dry: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- All Ghidra runs reported `REPORT: Save succeeded`.
- Read-back verified `10` metadata rows, `10` tag rows, `17` xref rows, instruction exports, and `10` decompile exports.
- Focused probe passed: `py -3 tools\ghidra_csoundmanager_events_wave500_probe.py --check`
- npm probe passed: `cmd.exe /c npm run test:ghidra-csoundmanager-events-wave500`
- Static queue check passed: `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260517-125819_post_wave500_csoundmanager_events_verified`

Queue snapshot after Wave500:

| Metric | Value |
| --- | ---: |
| Function objects | 6078 |
| Functions with non-empty function comments | 2277 |
| Commentless functions | 3801 |
| `undefined` signatures | 1655 |
| Signatures still using `param_N` names | 1504 |
| Comment-backed proxy | `2277/6078 = 37.46%` |
| Strict comment-plus-clean-signature proxy | `2223/6078 = 36.57%` |

Backup verification:

| Metric | Value |
| --- | ---: |
| Source files | 19 |
| Backup files | 19 |
| Source bytes | 157780871 |
| Backup bytes | 157780871 |
| Missing files | 0 |
| Extra files | 0 |
| Hash differences | 0 |

Not proven by this wave:

- Exact `CSoundManager`, `CSoundEvent`, channel, sample, or active-reader layouts.
- Runtime audio playback, mixing, pause/unpause, 3D positioning, or pitch behavior.
- BEA launch behavior, executable patching behavior, or rebuild parity.

Nearby exclusions:

- `0x004e1200`, `0x004e1800`, `0x004e1880`, `0x004e1910`, `0x004e1940`, and `0x004e1ab0` were left out because current evidence points to non-CSoundManager or separate-owner helpers.
- Deeper audio targets including `CSoundManager__Init`, `CSoundManager__PlayNamedSample`, `CSoundManager__PlaySound`, `CSoundManager__GetDebugMenuText`, and `CSoundManager__LoadSoundDefinitions` remain queued for later passes.
