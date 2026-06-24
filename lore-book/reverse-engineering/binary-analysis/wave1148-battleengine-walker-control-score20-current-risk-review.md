# Wave1148 BattleEngine/Walker Control Score20 Current-Risk Review

Wave1148 (`wave1148-battleengine-walker-control-score20-current-risk-review`) accounts for `13 current-risk rows` from the Wave1108 current focused denominator as a BattleEngine/walker-control score20 current-risk review. It is a fresh Ghidra read-only review with no mutation and no Codex subagent.

Probe token anchor: Wave1148; wave1148-battleengine-walker-control-score20-current-risk-review; 329/1179 = 27.91%; 13 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 850; current risk candidates: 6166; BattleEngine/walker-control score20 current-risk review; fresh Ghidra export; BattleEngine zoom/morph/rearm/crosshair/auto-aim/augment/transition/ground-effect helpers; WalkerPart constructor/dash/landing-jets/current-weapon helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CBattleEngine__AutoZoomOut; CBattleEngine__Morph; CBattleEngine__Rearm; CBattleEngine__CalcUnitOverCrossHair; CBattleEngine__UpdateAutoAim; CBattleEngine__ClearFlag58CAndMorphIfState3; CBattleEngine__AugmentWeapon; CBattleEngine__FinishedPlayingCurrentAnimation; CBattleEngine__GroundParticleEffect; CBattleEngineWalkerPart__ctor; CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove; CBattleEngineWalkerPart__ActivateLandingJets; CBattleEngineWalkerPart__GetCurrentWeapon; G:\GhidraBackups\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

| Address | Current name | Static evidence |
| --- | --- | --- |
| `0x00409e80` | `CBattleEngine__AutoZoomOut` | Source-parity zoom helper; xrefs from weapon-change and morph-adjacent paths. |
| `0x0040a580` | `CBattleEngine__Morph` | State-gated morph transition with `CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove`, JetPart state-machine checks, transform events, animation paths, part transition calls, and audio hooks. |
| `0x0040ac50` | `CBattleEngine__Rearm` | `RET 0x4` rearm helper over six stores, heat-store skip, `inAmount` scaling, and max clamp. |
| `0x0040acc0` | `CBattleEngine__CalcUnitOverCrossHair` | `RET 0xc` target helper with optional current-target reader reset, view/collision selection, range filtering, reader update, and event reschedule. |
| `0x0040b120` | `CBattleEngine__UpdateAutoAim` | Current weapon and target-reader refresh, predictive/direct yaw-pitch offsets, and smoothing through `AngleDifference`-style helpers. |
| `0x0040dcc0` | `CBattleEngine__ClearFlag58CAndMorphIfState3` | Clears `+0x58c`, checks state `+0x260 == 3`, and tail-jumps to Morph. |
| `0x0040de40` | `CBattleEngine__AugmentWeapon` | Selected weapon checks, charge/slow-movement reset path, event timestamps from `DAT_00672fd0`, aug value `10.0`, aug-active flag, and `hud_weapon_augmented`. |
| `0x0040eeb0` | `CBattleEngine__FinishedPlayingCurrentAnimation` | Transition animation completion helper for `flytowalk`/`walktofly`. |
| `0x0040ef20` | `CBattleEngine__GroundParticleEffect` | Water/terrain height sample and land/water particle-link helper path. |
| `0x00412bc0` | `CBattleEngineWalkerPart__ctor` | Stores main part, calls `CBattleEngineWalkerPart__ResetConfiguration`, and registers dash console variables. |
| `0x004135d0` | `CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove` | `+0x44` dash/special-walker counter predicate used by Morph. |
| `0x004135e0` | `CBattleEngineWalkerPart__ActivateLandingJets` | Main-part velocity sampling, walk velocity limit, and movement-latch write. |
| `0x00414030` | `CBattleEngineWalkerPart__GetCurrentWeapon` | Primary/augmented/fallback weapon resolver with broad HUD/weapon caller fan-in. |

Fresh primary exports verified `13` metadata rows, `13` tag rows, `48` xref rows, `1436` body-instruction rows, and `13` decompile rows. The verified Ghidra project backup is `G:\GhidraBackups\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified` with `19` files, `175967111` bytes, `DiffCount=0`, and `HashDiffCount=0`.

## Boundary

This wave proves static Ghidra read-back coherence for the selected rows only. Runtime BattleEngine behavior, runtime WalkerPart behavior, runtime weapon/zoom/auto-aim/morph/landing-jets/particle behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
