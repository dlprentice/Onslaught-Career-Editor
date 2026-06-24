# Ghidra CWeapon Distance-Profile Wave539 Readiness Note

Date: 2026-05-18

## Scope

Wave539 saved static Ghidra name/signature/comment/tag corrections for seven `CWeapon` distance-profile helpers reached from BattleEngine firing and target-selection paths:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x005061f0` | `CWeapon__DoesTargetMaskMatchDistanceProfile` | `bool __thiscall CWeapon__DoesTargetMaskMatchDistanceProfile(void * this, void * target_unit)` |
| `0x00506350` | `CWeapon__GetDistanceProfileField90` | `int __fastcall CWeapon__GetDistanceProfileField90(void * this)` |
| `0x00506440` | `CWeapon__GetDistanceProfileField94` | `double __fastcall CWeapon__GetDistanceProfileField94(void * this)` |
| `0x00506530` | `CWeapon__GetDistanceProfileFieldA8` | `int __fastcall CWeapon__GetDistanceProfileFieldA8(void * this)` |
| `0x00506620` | `CWeapon__GetDistanceProfileField98` | `double __fastcall CWeapon__GetDistanceProfileField98(void * this)` |
| `0x00506710` | `CWeapon__GetDistanceProfileField9C` | `double __fastcall CWeapon__GetDistanceProfileField9C(void * this)` |
| `0x00506800` | `CWeapon__GetDistanceProfileFieldA0` | `double __fastcall CWeapon__GetDistanceProfileFieldA0(void * this)` |

The important owner correction is that BattleEngine firing callers obtain a current weapon through `CBattleEngineJetPart__GetCurrentWeapon` or `CBattleEngineWalkerPart__GetCurrentWeapon`, then pass that pointer as `ECX` to this helper cluster. The prior `CBattleEngine__...` owner prefix was stale.

## Evidence

- Apply script: `tools/ApplyCWeaponDistanceProfileWave539.java`.
- Probe: `tools/ghidra_cweapon_distance_profile_wave539_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave539-battleengine-profile-distance-005061f0/`.
- Dry run: `updated=0 skipped=7 renamed=0 would_rename=7 missing=0 bad=0`.
- Apply: `updated=7 skipped=0 renamed=7 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back verified `7` metadata rows, `7` tag rows, `19` xref rows, `1827` instruction rows, `7` decompile exports, and `2` caller decompile exports.
- Focused probe: `py -3 tools\ghidra_cweapon_distance_profile_wave539_probe.py --check` PASS.
- Npm wrapper: `cmd.exe /c npm run test:ghidra-cweapon-distance-profile-wave539` PASS.
- Queue refresh: `cmd.exe /c npm run test:ghidra-static-reaudit-queue` PASS after the mutation.
- Backup: `G:\GhidraBackups\BEA_20260518-082127_post_wave539_cweapon_distance_profile_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Queue Snapshot

Fresh queue telemetry after Wave539:

| Metric | Value |
| --- | ---: |
| Function objects | `6089` |
| Commented functions | `2635` |
| Commentless functions | `3454` |
| Exact-undefined signatures | `1535` |
| `param_N` signatures | `1306` |
| Comment-backed proxy | `2635/6089 = 43.27%` |
| Strict comment-plus-clean-signature proxy | `2581/6089 = 42.39%` |

This is telemetry only, not a completion milestone.

## Not Proven

- Runtime target acquisition, lock filtering, firing cadence, projectile behavior, or target-selection behavior.
- Exact `CWeapon`, distance-profile entry, distance-table, or target-unit layouts beyond observed offsets.
- Exact field semantics for profile offsets `+0x90`, `+0x94`, `+0x98`, `+0x9c`, `+0xa0`, `+0xa4`, and `+0xa8`.
- Exact source-body identity; source is only supporting owner/context evidence here.
- BEA launch, executable patching, and rebuild parity.
