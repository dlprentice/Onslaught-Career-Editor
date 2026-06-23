# Ghidra Weapon / Burst Provisional Review - 2026-05-09

Status: public-safe saved-Ghidra owner-neutral correction evidence

## Summary

This wave revisited the two weapon/burst-cluster helpers that earlier waves deliberately left provisional: `0x005069f0` and `0x00506010`. Fresh caller/decompile review showed that the old owner-prefixed names were too specific for the current evidence. Both functions are better represented as owner-neutral projectile-burst helpers until raw caller boundaries, exact source identity, or runtime proof narrows them further.

A serial headless dry/apply pass saved the owner-neutral names, hardened `burstContext` signatures, and proof-boundary comments. Fresh read-back plus a focused probe then verified the saved state.

## Corrected Targets

| Address | Previous state | Saved state after correction | Evidence boundary |
| --- | --- | --- | --- |
| `0x005069f0` | `int __fastcall CEngine__SpawnProjectileBurstFromCurrentPreset(void * param_1)` | `int __fastcall ProjectileBurst__SpawnFromCurrentPreset(void * burstContext)` | Creates projectile/effect objects from `burstContext +0xa0`, is reached from `CWeapon__HandleFireBurstEvent` and the percent-bucket fallback helper, and calls projectile/target helper paths. Exact `CWeapon::Fire`, exact `CBattleEngine::WeaponFired`, runtime stealth behavior, and raw caller boundaries remain unproven. |
| `0x00506010` | `int __fastcall CGeneralVolume__SpawnBurstFromPresetWithFallback(void * param_1)` | `int __fastcall ProjectileBurst__SpawnFromPercentBucketFallback(void * burstContext)` | Selects a preset from `burstContext +0xa4` bucket data, updates cooldown/progress fields, calls `ProjectileBurst__SpawnFromCurrentPreset`, and may reschedule event `0x1389`. Exact source identity, runtime stealth behavior, and raw caller boundaries remain unproven. |

## Validation

- Focused tests: `py -3 tools\ghidra_weapon_burst_provisional_review_probe_test.py` passed `2/2`.
- Python compile: `py -3 -m py_compile tools\ghidra_weapon_burst_provisional_review_probe.py tools\ghidra_weapon_burst_provisional_review_probe_test.py` passed.
- Headless dry/apply: `updated=0 skipped=2 missing=0 bad=0`, then `updated=2 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `2/2` targets.
- Fresh xref read-back: `12` rows.
- Fresh instruction read-back: `2202` rows from a widened instruction window.
- Focused probe: `cmd.exe /c npm run test:ghidra-weapon-burst-provisional-review` passed with `2` targets, `2` renamed targets, `2` hardened signatures, `2` raw caller boundaries still open at that time, and stealth status `unresolved`.
- Refreshed queue probe after this and the volume/augment/pickup tranche: `5866` functions, `511` commented functions, `5355` commentless functions, `2069` undefined signatures, and `2437` `param_N` signatures.

## Process Notes

- A read-only export attempt through the shell wrapper hit a Ghidra project `LockException`; it was rerun serially through direct Windows `analyzeHeadless.bat` and passed. No source data or saved Ghidra data was lost.
- The first focused probe run failed because the instruction read-back window was too short to include the `RET` evidence for `0x005069f0`; the instruction read-back was widened and the probe then passed.
- The two raw callsites into `0x00506010`, `0x0044e093` and `0x004f4bd6`, had no recovered Ghidra function owner in this evidence set. `release/readiness/ghidra_weapon_burst_raw_boundary_recovery_2026-05-10.md` is the later follow-up that recovers owner-neutral boundaries for those callsites without closing exact source/runtime identity.

## Non-Claims

This is saved Ghidra owner-name/signature/comment refinement only. It does not prove exact source `CWeapon::Fire`, exact source `CBattleEngine::WeaponFired`, `weapon_fire_breaks_stealth`, runtime cloak activation, runtime fire-while-cloaked behavior, runtime stealth reset behavior, concrete burst-context layout, tags/local names/types, BEA launch behavior, game patching, or rebuild parity.

## Privacy / Release Safety

This note includes repo-relative paths, public addresses, function names, aggregate counts, command summaries, and proof boundaries only. Raw decompile output, screenshots, frame data, copied saves, copied executables, private install paths, and generated JSON remain under ignored `subagents/`.
