# Ghidra BattleEngine Transition/Effects Review Wave948

> **Owner/name supersession (2026-07-12):** Wave948 remains a historical
> read-back record. Current static evidence identifies `0x004081c0` as
> `CBattleEngine__Move`, `0x00410c50` as `CBattleEngineJetPart__Move`, and
> `0x00411630` as `CBattleEngineJetPart__HandleGroundEffect`. See the
> [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

Status: complete read-only static read-back evidence
Date: 2026-05-28
Scope: `battleengine-transition-effects-review-wave948`

Wave948 re-reviewed the BattleEngine transition-completion, ground-effect, monitor movement-transition, and JetPart weapon-name bridge selected from the Wave911 focused queue. The pass was read-only: no Ghidra mutation, no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, and no BEA launch.

Primary targets:

| Address | Saved row | Fresh evidence |
| --- | --- | --- |
| `0x0040eeb0` | `CBattleEngine__FinishedPlayingCurrentAnimation` | Saved source-parity row still matches `references/Onslaught/BattleEngine.cpp` transition completion: decompile checks `flytowalk` / `walktofly` animation names, then dispatches the settled `walk` / `fly` animation. DATA xref `0x005d8ab0` remains the static callback/table anchor. |
| `0x0040ef20` | `CBattleEngine__GroundParticleEffect` | Fresh xrefs from `CMonitor__Process` and `CMonitor__UpdateMovementTransitionAndEffects`; decompile samples height from BattleEngine position fields around `this+0x1c..0x28`, chooses land/water particle manager context, and creates/positions the ground effect. |
| `0x00410c50` | `CMonitor__UpdateMovementTransitionAndEffects` | Sole checked caller remains `CMonitor__Process`; body calls `CMonitor__UpdateTrackedRenderPair`, `CBattleEngine__Morph` twice, `CMonitor__IntegrateMovementAgainstTerrain`, and `CBattleEngine__GroundParticleEffect`. This keeps the Wave253/Wave789 conservative monitor-owner boundary. |
| `0x004124d0` | `CBattleEngineJetPart__GetCurrentWeaponNameField04` | Fresh xref from `CBattleEngine__ChangeWeapon`; decompile walks the selected JetPart weapon entry and returns `*(char **)(*(int *)(entry + 0xa4) + 4)`, matching the saved bounded `field +0x04` name rather than a guessed source accessor. |

Context anchors:

- `0x004081c0 CMonitor__Process` calls `CBattleEngine__Morph`, `CBattleEngine__AugmentWeapon`, `CBattleEngine__GroundParticleEffect`, and `CMonitor__UpdateMovementTransitionAndEffects` context.
- `0x00409f70 CBattleEngine__ChangeWeapon` calls `CBattleEngineJetPart__ChangeWeapon`, `CBattleEngineJetPart__GetCurrentWeaponNameField04`, and the HUD sample string flow.
- `0x0040a580 CBattleEngine__Morph` calls `CBattleEngineJetPart__IsStateMachineActive`, `CGeneralVolume__BeginFlyToWalkTransition`, and `CGeneralVolume__BeginWalkToFlyTransition`.
- `0x0040dcc0 CBattleEngine__ClearFlag58CAndMorphIfState3` remains the adjacent `+0x58c/+0x260` morph gate.
- `0x00411e70 CBattleEngineJetPart__ChangeWeapon`, `0x00412520 CBattleEngineJetPart__GetWeaponIconName`, `0x00412570 CBattleEngineJetPart__CanWeaponFire`, and `0x00412610 CBattleEngineJetPart__GetCurrentWeapon` remain JetPart weapon context only.
- `0x005078f0 CMonitor__UpdateTrackedRenderPair` is called from both `CMonitor__UpdateMovementTransitionAndEffects` and `CBattleEngineWalkerPart__Move`.

Read-back evidence:

- Primary exports: 4 metadata rows, 4 tag rows, 5 xref rows, 860 instruction rows, and 4 decompile rows.
- Context exports: 13 metadata rows, 13 tag rows, 21 xref rows, 2818 instruction rows, and 13 decompile rows.
- Logs report `targets=4 found=4 missing=0`, `targets=4 dumped=4 missing=0 failed=0`, `targets=13 found=13 missing=0`, and `targets=13 dumped=13 missing=0 failed=0`.
- Wave911 focused re-audit progress after Wave948: `247/1408 = 17.54%`.
- Static export-contract function-quality closure remains `6150/6150 = 100.00%`.
- Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-073152_post_wave948_battleengine_transition_effects_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.

Consult note:

- A Cursor Composer 2.5 ask-mode consult recommended this four-row cluster as a behavioral BattleEngine morph/movement/FX/weapon bridge and warned against relitigating prior owner corrections without fresh evidence. Codex root audited that advice against live Ghidra exports and kept the wave read-only.

What this proves:

- The four saved primary rows still exist in the loaded Ghidra project with the expected names, signatures, comments, xrefs, and decompile outputs.
- The static join between monitor processing, morph decisions, transition completion, ground effect dispatch, BattleEngine weapon change, and the JetPart weapon-name field remains coherent under fresh read-back.
- The old stale owner labels for these rows should not be revived based on current evidence.

What remains unproven:

- Runtime morph behavior.
- Runtime particle behavior.
- Runtime weapon switching or HUD audio behavior.
- Runtime controller/input behavior.
- Exact `CBattleEngine`, `CMonitor`, `CBattleEngineJetPart`, weapon-entry, or particle layouts.
- Exact source method identity for the monitor body and JetPart `field +0x04` accessor.
- BEA patching behavior.
- Rebuild parity.

Probe token anchor: Wave948; `battleengine-transition-effects-review-wave948`; `0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation`; `0x0040ef20 CBattleEngine__GroundParticleEffect`; `0x00410c50 CMonitor__UpdateMovementTransitionAndEffects`; `0x004124d0 CBattleEngineJetPart__GetCurrentWeaponNameField04`; `0x00409f70 CBattleEngine__ChangeWeapon`; `0x0040a580 CBattleEngine__Morph`; `0x00411e70 CBattleEngineJetPart__ChangeWeapon`; `0x005078f0 CMonitor__UpdateTrackedRenderPair`; `247/1408 = 17.54%`; `6150/6150 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-073152_post_wave948_battleengine_transition_effects_review_verified`; no mutation.
