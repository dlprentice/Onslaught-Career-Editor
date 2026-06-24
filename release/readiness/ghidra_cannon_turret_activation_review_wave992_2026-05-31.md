# Ghidra Cannon Turret Activation Review Wave992 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-31
Scope: `cannon-turret-activation-review-wave992`

Wave992 re-audited the Cannon/turret activation cluster after the Wave900-Wave991 recheck gate and saved seven bounded Ghidra comment/tag normalizations. The pass made no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary saved normalizations:

| Address | Result |
| --- | --- |
| `0x0041b1a0 CCannon__Init` | Refreshed the saved init comment and tags around `CGroundUnit__Init`, Active/Inactive animation-state selection, helper allocation/storage at `+0x208/+0x13c/+0x70`, state/timestamp fields `+0x260/+0x264`, occupancy-grid registration, and height-threshold flag `+0x258`. |
| `0x0041b370 CCannon__UpdateState` | Refreshed activation update evidence for enable/target-controller fields `+0x214/+0x13c`, Activate/Deactivate animation requests, state/timestamp writes, and both calls to `CGroundUnit__UpdateLinkedEffectsByHeightClearance`. |
| `0x0041b450 CCannon__VFuncSlot_02_RemoveFromWorldAndForward` | Reaffirmed that the row is not a destructor body; DATA refs place it in CCannon/CSentinel/CWarspiteDome slot-2 tables, and the body removes world occupancy-grid state before forwarding to `CUnit__VFunc02_CleanupWorldLinksAndForward`. |
| `0x0041b470 CCannon__AdvanceActivationAnimationState` | Refreshed the no-argument activation animation-state helper: it reads current animation ids, advances completed Activate/Deactivate transitions, and writes Active/Inactive state at `+0x260`. |
| `0x0041b540 CCannon__GetMidpoint` | Refreshed midpoint evidence: resolves target position through `CCannon__SelectTarget`, adds this unit position at `+0x1c/+0x20/+0x24`, and scales by the 0.5 constant. |
| `0x0041b590 CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph` | Reaffirmed that current read-back does not support the old CanFire label; slot-50 refs span CCannon/CWarspiteDome/CGroundVehicle, and the body calls `CGroundUnit__MarkDestroyedAndResetState` before `CUnit__ResetDeploymentGraphAndScheduleEvent` on success. |
| `0x004fd4d0 CCannon__SelectTarget` | Replaced stale fallback wording with current `CThing__GetCentrePos` evidence; linked targets at `+0x178` still forward to `CDiveBomber__SelectTarget`. |

Context targets re-exported without mutation:

- `0x0047c970 CGroundUnit__UpdateLinkedEffectsByHeightClearance`
- `0x0047ce80 CGroundUnit__MarkDestroyedAndResetState`
- `0x00495230 CMCCannon__Ctor`
- `0x00495260 CMCCannon__ScalarDeletingDestructor`
- `0x00495280 CMCCannon__Dtor`
- `0x004952a0 CMCCannon__VFunc_04_UpdateTurretBarrelTransform`

Read-back evidence:

- `ApplyCannonTurretActivationWave992.java` dry: `updated=0 skipped=7 comment_only_updated=7 tags_added=69 missing=0 bad=0`
- `ApplyCannonTurretActivationWave992.java` apply: `updated=7 skipped=0 comment_only_updated=7 tags_added=69 missing=0 bad=0`
- `ApplyCannonTurretActivationWave992.java` final dry: `updated=0 skipped=7 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Post exports: `13` metadata rows, `13` tag rows, `57` xref rows, `1044` body-instruction rows, and `13` decompile rows.
- Queue closure after refresh remains `6222/6222 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused re-audit progress is `446/1408 = 31.68%`; expanded static surface progress is `538/1478 = 36.40%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-053822_post_wave992_cannon_turret_activation_review_verified`, 19 files, 173837191 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved Ghidra project now records current static Cannon/turret activation comments and tags for the seven primary rows.
- The Cannon activation/update/cleanup/target-selection cluster is statically coherent with the Wave392 `CGroundUnit` owner corrections and Wave355 `CMCCannon` motion-controller rows.
- The existing names and signatures for all thirteen exported rows still read back cleanly.

What remains unproven:

- Runtime turret activation behavior.
- Runtime firing behavior.
- Exact `CCannon`, `CGroundUnit`, or `CMCCannon` concrete layouts.
- Exact source-body or virtual-method identity.
- BEA patching behavior.
- Rebuild parity.
