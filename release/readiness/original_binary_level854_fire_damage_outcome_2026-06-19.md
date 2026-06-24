# Original Binary Level854 Fire/Damage/Outcome Readiness Note

Status: complete public-safe copied-runtime fire-to-damage/outcome observer diagnostic
Date: 2026-06-19
Schema: `winui-original-binary-level854-fire-damage-outcome.v1`
Scope: `level854-fire-to-damage-outcome-observer-not-online-proof`

This slice follows the level `854` fire-handoff diagnostic with a wider non-mutating CDB observer over fire, projectile, round-collision, unit-damage, and outcome-transition anchors. It launched one app-owned safe copy from the clean specimen, materialized Fire weapon Q/E only in the copied `defaultoptions.bea`, attached CDB to the exact managed BEA process, sent repeated Q/E stimulus plus wait/no-input controls, captured bounded frames, and stopped the copied process cleanly.

Public-safe counters:

| Field | Value |
| --- | --- |
| `copiedDefaultOptionsFireWeaponQe=true` | accepted |
| `controlOptionsProofLever=copied-defaultoptions-weapon-fire-qe` | accepted |
| `sourceExpectedFireButton=18` | source/static expectation |
| `observedRuntimeFireButton=19` | copied-runtime observation |
| `button18DispatchCount=0` | no runtime button 18 dispatch observed |
| `button19DispatchCount=3` | accepted runtime dispatch count |
| `button18RuntimeDispatchObserved=false` | accepted caveat |
| `button19RuntimeDispatchObserved=true` | accepted proof boundary |
| `inputWindowCount=7` | accepted |
| `stimulusWindowCount=3` | two Q windows and one E window |
| `waitControlWindowCount=4` | wait/no-input controls |
| `sameWindowFireHandoffWindowCount=3` | accepted |
| `sameWindowFireBurstPointerChainWindowCount=2` | accepted |
| `sameWindowDamageSurfaceWindowCount=1` | diagnostic only |
| `sameWindowUnitApplyDamageWindowCount=1` | diagnostic only |
| `sameWindowOutcomeSurfaceWindowCount=0` | no outcome transition window |
| `waitWindowFireButtonDispatchCount=0` | wait controls did not dispatch fire input |
| `waitWindowDamageHitCount=27` | wait/no-input damage-side activity blocks damage promotion |
| `waitWindowOutcomeHitCount=0` | no wait/no-input outcome transition hit |
| `fireHitCount=426` | accepted CDB surface count |
| `projectileHitCount=3243` | accepted diagnostic count |
| `damageHitCount=151` | accepted diagnostic count |
| `unitApplyDamageHitCount=61` | accepted diagnostic count |
| `roundCollisionHitCount=90` | accepted diagnostic count |
| `outcomeHitCount=0` | no outcome transition hit |
| `damageProof=false` | unchanged; wait-window damage blocks causality |
| `runtimeOutcomeProof=false` | unchanged |
| `fireToDamageOutcomePromotion=false` | unchanged |
| `newBeaLaunchCount=1` | accepted |
| `cdbAttachCount=1` | accepted |
| `boundedCaptureCount=10` | accepted |
| `visualCaptureCount=10` | bounded copied-window captures accepted |
| `renderPlayers=2` | P1/P2 render graph observed |
| `renderLevel=854` | selected runtime candidate observed |
| `hookTargetCount=22` | accepted |
| `baseOnlineMultiplayerReady=false` | unchanged |
| `publicMatchmakingProof=false` | unchanged |
| `nativeBeaNetcodeProof=false` | unchanged |
| `activeP3P4OriginalBinaryGameplayProof=false` | unchanged |

The accepted proof requires same-window observed runtime button 19 dispatch plus weapon/fire handoff hits and same-window fire-to-burst pointer-chain evidence before evaluating damage/outcome counters. This run observed one stimulus window with damage-side activity and one stimulus window with `CUnit__ApplyDamage`, but it also observed wait/no-input damage activity. Therefore the checker keeps `damageProof=false`, `runtimeOutcomeProof=false`, and `fireToDamageOutcomePromotion=false`.

Machine-checkable guard: wait/no-input damage activity prevents damage promotion.

Boundary: this is a P1/P2 local copied-runtime fire-to-damage/outcome observer diagnostic. It proves the copied Fire weapon Q/E materialization, same-window fire handoff anchors, fire-to-burst pointer-chain evidence, and diagnostic round-collision/unit-damage surfaces. It does not prove true online multiplayer, second-host LAN, public matchmaking, native BEA netcode, co-op, versus, team-versus, spectator/admin runtime behavior, natural win/death/respawn transitions, damage causality, kill proof, active P3/P4 original-binary gameplay, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

Validation:

- `py -3 tools\build_winui_original_binary_level854_fire_damage_outcome_bundle.py`: PASS
- `py -3 tools\winui_safe_copy_online_level854_fire_damage_outcome_check.py`: PASS
- `py -3 tools\winui_safe_copy_online_level854_fire_damage_outcome_check_test.py`: PASS
- `py -3 tools\winui_safe_copy_online_level854_fire_damage_outcome_check.py --self-test`: PASS

Private proof material remains under ignored local evidence storage and is release-excluded by policy. Public docs record only bounded counts, schema/scope names, and non-claim tokens.
