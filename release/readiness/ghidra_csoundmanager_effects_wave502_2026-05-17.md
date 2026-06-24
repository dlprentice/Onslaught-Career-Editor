# Ghidra CSoundManager Effects Wave502 Readiness Note

Status: static RE evidence captured
Date: 2026-05-17
Scope: public-safe static Ghidra correction note

Wave502 saved static Ghidra name/signature/comment/tag hardening for eleven `CSoundManager` / `CEffect` / `CSoundEvent` effect-definition and playback helpers:

| Address | Saved state |
| --- | --- |
| `0x004e00d0` | `bool __thiscall CSoundManager__Init(void * this)` |
| `0x004e1800` | `void __thiscall CSoundManager__StopSample(void * this, char * sample_name, void * owner)` |
| `0x004e1880` | `void * __thiscall CSoundManager__GetSoundEventForThing(void * this, char * sample_name, void * owner)` |
| `0x004e1910` | `void * __thiscall CSoundManager__GetEffectByName(void * this, char * name, int ordinal)` |
| `0x004e1940` | `void __thiscall CSoundManager__PlayEffect(void * this, void * effect, void * owner, float volume, int tracking_type, int once, float fade_seconds, float from_point_seconds, float to_point_seconds, int repeat, float pitch, int sound_type, int ignore_owner_pos)` |
| `0x004e1ab0` | `bool __thiscall CSoundManager__IsEffectPlaying(void * this, void * effect, void * owner)` |
| `0x004e2360` | `void __thiscall CSoundManager__GetDebugMenuText(void * this, int entry_index, char * text)` |
| `0x004e2530` | `void __cdecl CEffect__LoadSFXFile(char * filename)` |
| `0x004e2a90` | `void * __cdecl CEffect__GetEffectByName(char * name, int ordinal)` |
| `0x004e2b30` | `void __thiscall CSoundEvent__DestructorBody(void * this)` |
| `0x004e2c50` | `void __thiscall CSoundManager__ReloadLanguageSampleBank(void * this)` |

Evidence:

- Apply script: `tools/ApplyCSoundManagerEffectsWave502.java`
- Focused probe: `tools/ghidra_csoundmanager_effects_wave502_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave502-soundmanager-effects-scout-004e1800/`
- Dry run: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=8 missing=0 bad=0`
- Apply: `updated=11 skipped=0 created=0 would_create=0 renamed=8 would_rename=0 missing=0 bad=0`
- Final verify dry: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- All Ghidra runs reported `REPORT: Save succeeded`.
- Read-back verified `13` metadata rows, `13` tag rows, `117` xref rows, `481` instruction rows, and `13` decompile exports. The two non-mutated scout targets were `0x004e2bb0` and `0x004e2e60`.
- Focused probe passed: `py -3 tools\ghidra_csoundmanager_effects_wave502_probe.py --check`
- npm probe passed: `cmd.exe /c npm run test:ghidra-csoundmanager-effects-wave502`
- Static queue check passed: `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260517-140251_post_wave502_csoundmanager_effects_verified`

Queue snapshot after Wave502:

| Metric | Value |
| --- | ---: |
| Function objects | 6078 |
| Functions with non-empty function comments | 2295 |
| Commentless functions | 3783 |
| `undefined` signatures | 1651 |
| Signatures still using `param_N` names | 1493 |
| Comment-backed proxy | `2295/6078 = 37.76%` |
| Strict comment-plus-clean-signature proxy | `2238/6078 = 36.82%` |

Backup verification:

| Metric | Value |
| --- | ---: |
| Source files | 19 |
| Backup files | 19 |
| Source bytes | 157944711 |
| Backup bytes | 157944711 |
| Missing files | 0 |
| Extra files | 0 |
| Hash differences | 0 |

Not proven by this wave:

- Exact `CSoundManager`, `CEffect`, `CSoundEvent`, backend channel, sample-bank, owner-reader, or debug-marker layouts.
- Runtime SFX parse behavior, effect random selection, playback, mixing, language-bank reload, or visible debug menu behavior.
- BEA launch behavior, executable patching behavior, or rebuild parity.

Nearby exclusions:

- Wave502 deliberately left `0x004e2bb0` `CUnit__BuildVoiceXapPathIfChanged` and `0x004e2e60` `CUnit__PlayImpactSoundForMaterials` as scout/context targets only.
- Broader monitor/BattleEngine callers, exact enum names, locals/types, and runtime audio proof remain queued for later passes.
