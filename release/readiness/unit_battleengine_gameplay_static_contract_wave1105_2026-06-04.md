# Unit / BattleEngine / Gameplay Static Contract Wave1105 Readiness Note

Status: complete static contract consolidation
Date: 2026-06-04
Scope: `unit-battleengine-gameplay-static-contract-wave1105`

Wave1105 consolidates existing Unit/BattleEngine/gameplay static evidence into `reverse-engineering/binary-analysis/unit-battleengine-gameplay-static-contract.md`. This is a documentation/probe wave only: no Ghidra export, no Ghidra mutation, no executable-byte change, no BEA launch, no save mutation, and no installed-game/runtime-file mutation occurred.

Contract anchors:

| Area | Evidence |
| --- | --- |
| Wave906 baseline | `633` rows across `75` selected owner families; `CUnit` `90`, `CUnitAI` `63`, `CBattleEngine` `47`, `CBattleEngineWalkerPart` `27`, `CBattleEngineJetPart` `23`, `CCollisionSeekingRound` `17`, `CRound` `13`, and `CWeapon` `12`; verified backup `G:\GhidraBackups\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified`. |
| CUnit lifecycle | `0x004f9a90 CUnit__ApplyDamage`, `0x004dfa40 CUnit__VFunc08_InitAndAddToWorld`, `0x004f84e0 CUnit__dtor_base`, `0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward`, `0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent`, `0x004fd140 CUnit__MarkDestroyedAndCleanupLinks`; backups `G:\GhidraBackups\BEA_20260602-060358_post_wave1075_cunit_vfunc08_boundary_verified` and `G:\GhidraBackups\BEA_20260604-182217_post_wave1097_cunit_dtor_thunk_lifecycle_review_verified`. |
| BattleEngine mode/targeting | `0x00404dd0 CBattleEngine__Init`, `0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`, `0x00406da0 CBattleEngine__SelectNearestForwardTargetFromGlobalSet`, `0x0040d0f0 CWeaponStatement__UsesBallisticArcNoLocks`, `0x0040dc30 CBattleEngine__EnableVolumeEntryGroupsByName`, `0x0040dcc0 CBattleEngine__ClearFlag58CAndMorphIfState3`, and `0x0040c180 CBattleEngine__HandleEvent`; backups `G:\GhidraBackups\BEA_20260528-013432_post_wave936_battleengine_init_morph_volume_review_verified` and `G:\GhidraBackups\BEA_20260531-163000_post_wave1010_battleengine_zoom_autoaim_review_verified`. |
| Weapon state | `0x00412bc0 CBattleEngineWalkerPart__ctor`, `0x00413cc0 CBattleEngineWalkerPart__FireWeapon`, `0x00413cf0 CBattleEngineWalkerPart__ChargeWeapon`, `0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon`, `0x004140d0 CBattleEngineWalkerPart__WeaponFired`, `0x00412050 CBattleEngineJetPart__WeaponFired`, `0x00505e00 CWeapon__ctor_base`, `0x005061f0 CWeapon__DoesTargetMaskMatchDistanceProfile`, and `0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned`; backups `G:\GhidraBackups\BEA_20260528-043815_post_wave943_unit_weapon_gameplay_review_verified`, `G:\GhidraBackups\BEA_20260601-014543_post_wave1027_battleengine_walkerpart_weapon_spine_review_verified`, and `G:\GhidraBackups\BEA_20260601-025247_post_wave1029_battleengine_jetpart_weapon_status_review_verified`. |
| AI/targeting/deploy | `0x00415140 CUnitAI__HandleLandedStateTransition`, `0x00415780 CUnitAI__PlayDeployingAnimationIfState0`, `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw`, `0x00428bc0 CUnitAI__GetTargetHeadingWithOffset`, `0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped`, `0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting`, and `0x004ff330 SharedUnitAI__HandleEventAndMaybeFire_004ff330`; backups `G:\GhidraBackups\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified`, `G:\GhidraBackups\BEA_20260527-225215_post_wave928_cunitai_deploy_state_review_verified`, and `G:\GhidraBackups\BEA_20260602-110925_post_wave1082_infantryai_vtable_boundary_verified`. |
| Projectile/collision-seeking | `CRound__SpawnConfiguredProjectile`, `CWeapon__HandleFireBurstEvent`, `0x00425b50 CCollisionSeekingRound__InitCollisionLineAndSound`, `0x00425e30 CCollisionSeekingRound__UpdatePrimarySeekerLeadVector`, `0x004264a0 CCollisionSeekingRound__ResolveRoundCollisionResponse`, and `0x00426a20 CCollisionSeekingRound__MarkDelayedCollisionReady`; backup `G:\GhidraBackups\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified`. |
| Unit-family vtables | `0x00489ed0 CInfantryUnitVFunc__ReturnFlag24Float005d856cOr005d8568_00489ed0`, `0x004d35d0 CPodVFunc__FlagArg70AndSeedMotion250_004d35d0`, `0x004deec0 CSentinelVFunc__BuildField164ContextAndDispatch_004deec0`, `0x004eee80 CSubmarineVFunc__UpdateMotionVectorsAndNormalize_004eee80`, `0x0050e9d0 CInfantryUnitVFunc__GetClassNameString_0050e9d0`, `0x0050fd10 CGillMHeadVFunc__ForwardArgWithFlags40082000_0050fd10`, and Wave1089 sample `1580` OK / `20` `NO_FUNCTION_AT_POINTER`; backup `G:\GhidraBackups\BEA_20260604-130410_post_wave1089_unit_family_residual_vtable_final_review_verified`. |

Counters remain unchanged: static Ghidra function-quality closure `6410/6410 = 100.00%`; expanded post-100 static surface `1560/1560 = 100.00%`; Wave911 focused queue `812/1408 = 57.67%`; Wave911 top-500 risk-ranked subset `500/500 = 100.00%`.

Latest completed Ghidra review backup remains Wave1100: `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

What this proves:

- Existing static evidence forms a coherent Unit/BattleEngine/gameplay contract across lifecycle, damage, AI, targeting, mode switching, weapon state, projectile/round handoffs, collision-seeking, and unit-family vtable boundaries.
- The claim is static Ghidra/source-reference coherence only, with public-safe evidence anchors suitable for later runtime-proof, patch, schema, and rebuild planning.

What remains separate:

- Runtime damage, AI, weapon, input, mode-switching, targeting, spawn, projectile, collision, cloak, stealth, and HUD behavior.
- Exact object layouts and exact source-body identity.
- Exact retail `CBattleEngine::WeaponFired` identity and `weapon_fire_breaks_stealth`.
- BEA patching behavior, gameplay outcomes, and clean-room rebuild parity.
