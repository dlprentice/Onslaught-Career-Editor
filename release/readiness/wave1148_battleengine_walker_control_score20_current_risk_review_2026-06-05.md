# Wave1148 BattleEngine/Walker Control Score20 Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1148-battleengine-walker-control-score20-current-risk-review`

Wave1148 re-read thirteen BattleEngine/walker-control score20 current-risk rows with fresh Ghidra exports and made no mutation: no rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, runtime-file mutation, or Codex subagent.

Probe token anchor: Wave1148; wave1148-battleengine-walker-control-score20-current-risk-review; 329/1179 = 27.91%; 13 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 850; current risk candidates: 6166; BattleEngine/walker-control score20 current-risk review; fresh Ghidra export; BattleEngine zoom/morph/rearm/crosshair/auto-aim/augment/transition/ground-effect helpers; WalkerPart constructor/dash/landing-jets/current-weapon helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CBattleEngine__AutoZoomOut; CBattleEngine__Morph; CBattleEngine__Rearm; CBattleEngine__CalcUnitOverCrossHair; CBattleEngine__UpdateAutoAim; CBattleEngine__ClearFlag58CAndMorphIfState3; CBattleEngine__AugmentWeapon; CBattleEngine__FinishedPlayingCurrentAnimation; CBattleEngine__GroundParticleEffect; CBattleEngineWalkerPart__ctor; CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove; CBattleEngineWalkerPart__ActivateLandingJets; CBattleEngineWalkerPart__GetCurrentWeapon; [maintainer-local-ghidra-backup-root]\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `13` rows, `targets=13 found=13 missing=0`.
- `pre-tags.tsv`: `13` rows, `missing=0`.
- `pre-xrefs.tsv`: `48` rows.
- `pre-instructions.tsv`: `1436` instruction rows, `targets=13 missing=0`.
- `pre-decompile/index.tsv`: `13` rows, `targets=13 dumped=13 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified`.
- Codex subagent usage: none for this slice; Codex root selected and audited the tranche locally.

Reviewed rows:

| Address | Static read-back |
| --- | --- |
| `0x00409e80 CBattleEngine__AutoZoomOut` | Source-parity zoom helper writing the desired zoom-out field. |
| `0x0040a580 CBattleEngine__Morph` | Morph transition body with special-move gates, weapon-charge loss, transform events, animation paths, cockpit/part transition calls, and audio hooks. |
| `0x0040ac50 CBattleEngine__Rearm` | Store rearm loop with heat-store skip, `inAmount` scaling, and configured maximum clamp. |
| `0x0040acc0 CBattleEngine__CalcUnitOverCrossHair` | Crosshair target acquisition helper with optional reader reset, view-ray/collision path, range filtering, and event reschedule. |
| `0x0040b120 CBattleEngine__UpdateAutoAim` | Current weapon/target reader refresh and predictive/direct yaw-pitch smoothing helper. |
| `0x0040dcc0 CBattleEngine__ClearFlag58CAndMorphIfState3` | Tiny transition helper that clears `+0x58c`, checks state `+0x260 == 3`, and tail-jumps to Morph only in that state. |
| `0x0040de40 CBattleEngine__AugmentWeapon` | Augmented-weapon activation bridge with selected-weapon checks, aug timestamps, `MAX_AUG_VALUE` `10.0`, aug-active flag, and `hud_weapon_augmented`. |
| `0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation` | Transition animation completion helper for `flytowalk`/`walktofly` paths. |
| `0x0040ef20 CBattleEngine__GroundParticleEffect` | Water/terrain-height ground-effect particle helper that reaches static-shadow sampling and particle-link helpers. |
| `0x00412bc0 CBattleEngineWalkerPart__ctor` | WalkerPart constructor storing the main part, resetting configuration, and registering dash console variables. |
| `0x004135d0 CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove` | Dash/special-walker predicate over the `+0x44` counter. |
| `0x004135e0 CBattleEngineWalkerPart__ActivateLandingJets` | Landing-jets helper that samples main-part velocity, limits walk velocity, and sets the main-part movement latch. |
| `0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon` | Walker current-weapon resolver over primary/augmented/fallback weapon entries, with broad HUD/weapon caller fan-in. |

Accounting after Wave1148:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `329/1179 = 27.91%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 850.

This is static Ghidra evidence only. Runtime BattleEngine behavior, runtime WalkerPart behavior, runtime weapon/zoom/auto-aim/morph/landing-jets/particle behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
