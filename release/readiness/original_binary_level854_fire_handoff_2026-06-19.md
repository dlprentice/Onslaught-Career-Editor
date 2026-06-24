# Original Binary Level854 Fire-Handoff Readiness Note

Status: complete public-safe copied-runtime fire-handoff/projectile diagnostic with pointer-correlated fire-to-burst chain
Date: 2026-06-19
Schema: `winui-original-binary-level854-fire-handoff.v1`
Scope: `level854-fire-input-to-weapon-handoff-not-online-proof`

This slice extends the prior level `854` fire/weapon handoff proof with a longer repeated Q/E stimulus sequence, a wider non-mutating CDB observer over CWeapon, BattleEngine projectile, projectile-factory, and CRound-side anchors, and a stricter pointer-chain guard. It launched one app-owned safe copy from the clean specimen, materialized Fire weapon Q/E only in the copied `defaultoptions.bea`, attached CDB to the exact managed BEA process, sent repeated Q/E stimulus plus wait/no-input controls, captured bounded frames, and stopped the copied process cleanly.

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
| `sameWindowInputFireHandoffWindowCount=3` | accepted |
| `sameWindowInputFireHandoffObserved=true` | accepted |
| `sameWindowFireBurstPointerChainWindowCount=1` | accepted |
| `sameWindowFireBurstPointerChainObserved=true` | accepted |
| `sameWindowOrderedFireBurstPointerChainWindowCount=0` | stricter ordered chain not proven |
| `sameWindowOrderedFireBurstPointerChainObserved=false` | accepted non-promotion boundary |
| `fireBurstPointerChainContextCount=1` | public-safe count only; raw runtime pointer remains private |
| `waitWindowFireButtonDispatchCount=0` | wait controls did not dispatch fire input |
| `waitWindowAmbientHandoffHitCount=311` | ambient non-causal burst/handoff hits |
| `waitWindowCausalProof=false` | unchanged |
| `directFireDispatchHitCount=23` | accepted CDB handoff surface count |
| `burstOrProjectilePresetHitCount=1209` | accepted CDB handoff surface count |
| `battleEngineProjectileTotalHitCount=1200` | accepted diagnostic count |
| `shellMaterializationTotalHitCount=0` | no OID/CShell materialization hit in this proof |
| `projectileFactoryTotalHitCount=2045` | accepted diagnostic count |
| `roundProjectileTotalHitCount=2045` | accepted diagnostic count |
| `sameWindowBattleEngineProjectileObserved=true` | accepted diagnostic |
| `sameWindowShellMaterializationObserved=false` | unchanged |
| `sameWindowProjectileFactoryObserved=true` | accepted diagnostic |
| `roundProjectileSameWindowCoincidenceObserved=true` | accepted diagnostic |
| `roundProjectileCausalityProof=false` | unchanged |
| `roundProjectileSameWindowCausalityProof=false` | unchanged |
| `runtimeOutcomeProof=false` | unchanged |
| `newBeaLaunchCount=1` | accepted |
| `cdbAttachCount=1` | accepted |
| `boundedCaptureCount=10` | accepted |
| `visualCaptureCount=10` | bounded copied-window captures accepted |
| `renderPlayers=2` | P1/P2 render graph observed |
| `renderLevel=854` | selected runtime candidate observed |
| `hookTargetCount=27` | accepted |
| `baseOnlineMultiplayerReady=false` | unchanged |
| `publicMatchmakingProof=false` | unchanged |
| `nativeBeaNetcodeProof=false` | unchanged |
| `activeP3P4OriginalBinaryGameplayProof=false` | unchanged |

The stimulus windows were `down:Q,wait:2500,up:Q`, repeated once, and `down:E,wait:2500,up:E`, surrounded by wait/no-input controls. The accepted proof requires same-window observed runtime button 19 dispatch plus weapon/fire handoff hits, and at least one same-window pointer-correlated `WeaponFired.weapon -> CWeapon::HandleFireBurstEvent.this -> ProjectileBurst` context chain. The stricter ordered chain was tested separately and remains unproven in this run: `sameWindowOrderedFireBurstPointerChainWindowCount=0` and `sameWindowOrderedFireBurstPointerChainObserved=false`. The source-expected button 18 did not dispatch in this run, so `button18RuntimeDispatchObserved=false` and `button19RuntimeDispatchObserved=true` are explicit guard tokens.

Boundary: this is a P1/P2 local copied-runtime fire-input-to-weapon/projectile diagnostic. It proves the copied Fire weapon Q/E materialization, same-window weapon/fire handoff anchors, one same-window fire-to-burst pointer chain, ordered fire/burst correlation still false, and same-window BattleEngine/projectile-factory/CRound-side activity. It does not promote round/projectile causality because wait/no-input windows also contained ambient projectile-side activity. It does not prove true online multiplayer, second-host LAN, public matchmaking, native BEA netcode, co-op, versus, team-versus, spectator/admin runtime behavior, natural win/death/respawn transitions, runtime outcome proof, damage proof, kill proof, visual projectile proof, round/projectile causality proof, active P3/P4 original-binary gameplay, deterministic sync, rollback, anti-cheat, rebuild parity, or no-noticeable-difference online parity.

Validation:

- `py -3 tools\build_winui_original_binary_level854_fire_handoff_bundle.py`: PASS
- `py -3 tools\winui_safe_copy_online_level854_fire_handoff_check.py`: PASS

Private proof material remains under ignored local evidence storage and is release-excluded by policy. Public docs record only bounded counts, schema/scope names, and non-claim tokens.
