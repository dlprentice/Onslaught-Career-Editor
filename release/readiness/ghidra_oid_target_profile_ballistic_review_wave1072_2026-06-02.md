# Ghidra OID Target/Profile Ballistic Review Wave1072 Readiness Note

Status: complete static read-only evidence
Date: 2026-06-02
Scope: `oid-target-profile-ballistic-review-wave1072`

Wave1072 re-read fifteen existing Wave553/Wave554 OID, Unit, BattleEngine, target-profile, projectile-burst, and squad-mask rows plus sixteen caller/context rows without Ghidra mutation. The pass made no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00507ab0 OID__CanFireAtTarget_BallisticArcA` | Code xref `0x004fb578`; checks attachment/origin height, fear-grid clearance, yaw/pitch windows, ballistic-arc statement state, optional trace context, and line-hit selection before returning fire eligibility. |
| `0x005088b0 OID__CanFireAtTarget_BallisticArcB` | Code xref `0x004fb629`; checks target pitch/profile windows, static-shadow fallback behavior, and optional line trace visibility. |
| `0x00509140 OID__UpdateAimTransformAndAttachTargetReader` | Code xref `0x004fb664`; updates target-vector state at OID fields `+0x84..+0x90`, refreshes aim orientation, sets dirty flag `+0x80`, and registers the target reader at `+0x2c`. |
| `0x005094b0 OID__SolveBallisticPitchToTarget` | Xrefs from `0x0040cea4`, `0x004fb2fd`, and `0x00504baf`; solves pitch from target vector, owner origin, launch speed, gravity/profile fields, and active pitch-window fields. |
| `0x005096a0 CUnit__ComputeMinBallisticTravelDistance` | Five xrefs from auto-aim/range/support context; derives minimum ballistic travel distance from target height, speed, gravity, and pitch-window fields or returns the non-ballistic profile field. |
| `0x005099a0 CUnit__ComputeMaxBallisticTravelDistance` | Eight xrefs from auto-aim, range classification, support, ProjectileBurst, and projectile caller boundaries; derives maximum ballistic travel distance or returns the non-ballistic profile field. |
| `0x00509c80 CBattleEngine__ComputeProjectileMetricFromTargetProfile` | Code xref `0x0040ad64`; forwards active ballistic profiles to `CUnit__ComputeMaxBallisticTravelDistance` or selects a target/profile entry from `DAT_008553ec`. |
| `0x00509e40 TargetSet__GetEntryByIndex` | Code xref `0x00509d60`; cdecl global target/profile set iterator over `DAT_008553ec`. |
| `0x00509e90 ProjectileBurst__ResolvePresetByPercentBucketFallback` | Code xref `0x00506100`; resolves a burst-context percent bucket through the `+0xa4` bucket table and `DAT_008553ec` fallback scan. |
| `0x00509f70 TargetProfileContext__IsEligibleByDistanceBucketOrRange` | Eight xrefs from BattleEngine auto-targeting, Unit deploy/support, Sentinel flamethrower, and projectile-burst boundaries; shared distance/profile eligibility gate. |
| `0x0050a080 TargetProfileContext__CanProceedByTargetRangeGate` | Callers `0x00411c61 CGeneralVolume__DispatchMode3BurstProgressAndSpawn` and `0x00413d14 CBattleEngineWalkerPart__ChargeWeapon`; returns false only for active profiles whose range-time gate has not elapsed. |
| `0x0050a0b0 CSquadNormal__HasActiveMaskMatchWithTarget` | Two xrefs; checks active squad mask intersection between `this+0xa8` and `target_unit+0x34`. |
| `0x0050a0d0 CUnit__HasMaskBitsA8` | One xref from `CSquadNormal__SelectBestSupportOrEscort`; returns `this+0xa8 & mask_bits`. |
| `0x0050a0e0 OID__ComputeForwardProjectedPointTowardTarget` | Two OID ballistic-fire callsites; writes a forward-projected target point from OID/profile/target transform and velocity evidence, or copies the target transform fallback vector. |
| `0x0050a290 CUnit__IsTargetTimeoutBeforeProfileLimit` | Three xrefs from target-set, linked-unit, and support-selection predicates; tests unit timeout against profile `+0x44`. |

Read-back evidence:

- Primary exports: `15` metadata rows, `15` tag rows, `40` xref rows, `2997` function-body instruction rows, and `15` decompile rows.
- Context exports: `16` metadata rows, `70` xref rows, `1769` function-body instruction rows, and `16` decompile rows.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1334/1560 = 85.51%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-035902_post_wave1072_oid_target_profile_ballistic_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The current saved Ghidra names, signatures, comments, and tags for the fifteen primary rows remain internally coherent with fresh metadata, tag, xref, instruction, and decompile evidence.
- The Wave553/Wave554 OID/Unit/BattleEngine target-profile and ballistic rows still line up with their observed caller graph, `DAT_008553ec` target/profile set evidence, range-bucket gates, projectile-burst fallback, squad-mask helpers, and target-timeout predicates.
- The context rows tie the cluster to BattleEngine auto-aim/crosshair, CUnit range classification, CWeapon charge/fire progress, CGeneralVolume mode-3 burst progress, CBattleEngineWalkerPart fire/charge paths, ProjectileBurst fallback, and CMonitor render-pair update context.

What remains separate proof:

- Runtime targeting, projectile, weapon, squad, and auto-aim behavior.
- Exact OID, Unit, BattleEngine, CWeapon, CSquadNormal, target-profile, and projectile-burst layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next expanded static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1072; oid-target-profile-ballistic-review-wave1072; 0x00507ab0 OID__CanFireAtTarget_BallisticArcA; 0x00509c80 CBattleEngine__ComputeProjectileMetricFromTargetProfile; 0x00509e90 ProjectileBurst__ResolvePresetByPercentBucketFallback; 0x00509f70 TargetProfileContext__IsEligibleByDistanceBucketOrRange; 0x0050a0e0 OID__ComputeForwardProjectedPointTowardTarget; 812/1408 = 57.67%; 1334/1560 = 85.51%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-035902_post_wave1072_oid_target_profile_ballistic_review_verified; read-only review.
