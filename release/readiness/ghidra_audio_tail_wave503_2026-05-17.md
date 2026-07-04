# Ghidra Audio Tail Wave503 Readiness Note

Status: static RE evidence captured
Date: 2026-05-17
Scope: public-safe static Ghidra correction note

Wave503 saved static Ghidra name/signature/comment/tag hardening for three adjacent audio-tail helpers:

| Address | Saved state |
| --- | --- |
| `0x004e1200` | `void __thiscall CSoundManager__KillAllInstancesOfSample(void * this, void * sample)` |
| `0x004e2bb0` | `bool __thiscall CSoundManager__BuildLanguageSampleBankPathIfChanged(void * this, char * out_path)` |
| `0x004e2e60` | `void __cdecl CUnit__PlayImpactSoundForMaterials(void * primary_unit, void * secondary_unit)` |

Evidence:

- Apply script: `tools/ApplyAudioTailWave503.java`
- Focused probe: `tools/ghidra_audio_tail_wave503_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave503-audio-tail-004e1200/`
- Dry run: `updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=2 missing=0 bad=0`
- Apply: `updated=3 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0`
- Final verify dry: `updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- All Ghidra runs reported `REPORT: Save succeeded`.
- Read-back verified `3` metadata rows, `3` tag rows, `6` xref rows, `111` instruction rows, and `3` decompile exports.
- Focused probe passed: `py -3 tools\ghidra_audio_tail_wave503_probe.py --check`
- npm probe passed: `cmd.exe /c npm run test:ghidra-audio-tail-wave503`
- Static queue check passed: `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-142753_post_wave503_audio_tail_verified`

Queue snapshot after Wave503:

| Metric | Value |
| --- | ---: |
| Function objects | 6078 |
| Functions with non-empty function comments | 2298 |
| Commentless functions | 3780 |
| `undefined` signatures | 1651 |
| Signatures still using `param_N` names | 1490 |
| Comment-backed proxy | `2298/6078 = 37.81%` |
| Strict comment-plus-clean-signature proxy | `2241/6078 = 36.87%` |

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

- Exact `CSoundManager`, `CSoundEvent`, sample, sample-bank path-buffer, `CText`, material enum, vtable slot, effect, or backend channel layouts.
- Runtime sample shutdown, language switching, collision/impact sound behavior, or visible audio behavior.
- BEA launch behavior, executable patching behavior, or rebuild parity.

Nearby exclusions:

- Larger `CSpawnerThng` and `CSafeSide`/`CShell` queue-head clusters remain queued for later passes.
- Runtime audio proof remains intentionally separate from static Ghidra cleanup.
