# Ghidra Wave900+ Through Wave1027 Recheck

Status: complete structural static evidence recheck
Date: 2026-06-01
Scope: `wave900-plus-through-wave1027-recheck`

This note extends the Wave900+ static re-audit recheck through Wave1027. It validates the Wave1027 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1026 gate and current live queue closure at `6238/6238 = 100.00%`.

Validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1027-recheck
```

Expected coverage:

- Wave900-Wave981 remain covered by the prior focused-probe sweep and evidence audit.
- Wave982-Wave1027 focused probes are rerun directly by `tools/ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1027 --check`.
- Wave910 and Wave911 remain queue/planning records without per-wave backup notes.
- Current queue closure remains `6238/6238 = 100.00%`, with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave1027 readiness/evidence anchor: `battleengine-walkerpart-weapon-spine-review-wave1027`, `0x00412bc0 CBattleEngineWalkerPart__ctor`, `0x00413cc0 CBattleEngineWalkerPart__FireWeapon`, `0x00413cf0 CBattleEngineWalkerPart__ChargeWeapon`, `0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon`, `0x004140d0 CBattleEngineWalkerPart__WeaponFired`, `0x004145f0 CBattleEngineWalkerPart__GetCurrentWeaponZoomMode`, `600/1408 = 42.61%`, `829/1493 = 55.53%`, `500/500 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260601-014543_post_wave1027_battleengine_walkerpart_weapon_spine_review_verified`, no mutation.

This is structural static evidence validation only. It does not prove runtime firing, charging, HUD, heat, overheat, or zoom behavior, exact `CBattleEngine::WeaponFired` identity, `weapon_fire_breaks_stealth`, exact source-layout identity, BEA patch behavior, gameplay outcomes, or rebuild parity.
