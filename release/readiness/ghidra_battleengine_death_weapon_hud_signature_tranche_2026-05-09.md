# Ghidra BattleEngine Death / Weapon HUD Signature Tranche - 2026-05-09

## Summary

This wave reparsed six saved Ghidra functions around BattleEngine death startup, projectile-burst helper context, and the HUD weapon readout path. Fresh metadata, decompile, xref, and instruction exports showed that `0x0040bfd0` already had a stable BattleEngine death-start label, while two burst helpers and three HUD helpers carried stale owner labels. A serial headless dry/apply pass saved corrected names, signatures, and proof-boundary comments, followed by fresh read-back and a focused probe.

## Corrected Targets

| Address | Previous state | Saved state after correction | Evidence boundary |
| --- | --- | --- | --- |
| `0x0040bfd0` | `int __fastcall CBattleEngine__StartDieProcess(int param_1)` | `int __thiscall CBattleEngine__StartDieProcess(void * this)` | Source-aligned death-start path: dying flag, player vibration stop, `CGame__DeclarePlayerDead`, mission-script cleanup, explode/pickup path, and oily-smoke effect context. |
| `0x0040c2e0` | `CEngine__CanSpawnBurstForResolvedEntry` | `int __thiscall CBattleEngine__CanSpawnBurstForResolvedEntry(void * this, void * burstContext)` | Burst quota helper called from the current-preset projectile-burst body; it checks `+0x57c` and `+0x578` part paths and clears `+0x5d8` on success. |
| `0x0040c340` | `CEngine__RandomizeBurstOffsetsAndAccumulateRange` | `void __thiscall CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange(void * this, void * burstContext)` | Burst spread helper called after projectile creation; randomizes `+0x4b8/+0x4c0` style offsets and accumulates range context into `+0x604`. |
| `0x0040c3a0` | `CExplosionInitThing__GetCurrentEntrySlotFlag_544` | `int __thiscall CBattleEngine__IsEnergyWeapon(void * this)` | Source/caller bridge: HUD rendering calls through the BattleEngine pointer and the body dispatches to walker/jet current-entry energy/ammo-store flag context. |
| `0x0040c3c0` | `CExplosionInitThing__GetCurrentEntrySlotFillRatioOrRacerSpeed` | `float __thiscall CBattleEngine__GetWeaponAmmoPercentage(void * this)` | Source/caller bridge: HUD rendering uses the value for the weapon meter; the body handles Racer velocity and walker/jet ammo percentage helpers. |
| `0x0040c460` | `CExplosionInitThing__GetCurrentEntryRoundedSlotValue` | `int __thiscall CBattleEngine__GetWeaponAmmoCount(void * this)` | Source/caller bridge: HUD rendering formats the non-meter weapon readout; the body dispatches to walker/jet current-entry rounded count helpers. |

## Validation

- Focused tests: `py -3 tools\ghidra_battleengine_death_weapon_hud_signature_tranche_probe_test.py` passed `2/2`.
- Headless dry/apply: `updated=0 skipped=6 missing=0 bad=0`, then `updated=6 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `6/6` targets.
- Fresh xref read-back: `7` rows.
- Fresh instruction read-back: `1998` rows.
- Focused probe: `cmd.exe /c npm run test:ghidra-battleengine-death-weapon-hud-signature-tranche` passes with `6` targets, `5` renamed targets, `0` `param_N` signature hits, and `0` overclaim hits.
- Refreshed queue after this tranche reported `5866` functions, `483` commented functions, `5383` commentless functions, `2076` undefined signatures, and `2468` `param_N` signatures.

## Non-Claims

This is saved Ghidra name/signature/comment refinement only. It does not prove concrete `CBattleEngine`, part, weapon, event, or HUD layouts; exact `CWeapon::Fire`; exact retail `CBattleEngine::WeaponFired`; `weapon_fire_breaks_stealth`; runtime death behavior; runtime HUD behavior; runtime cloak activation; fire-while-cloaked behavior; BEA launch behavior; game patching; or rebuild parity.
