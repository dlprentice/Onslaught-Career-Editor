# Weapon / Projectile Spawn Handoff Proof Plan

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`); `0x004dac90` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: active public-safe proof plan, not runtime proof
Last updated: 2026-06-08
Scope: `weapon-projectile-spawn-handoff-proof-plan`

This plan is the next selected static-to-proof slice from `roadmap/static-to-proof-rebuild-transition-backlog.md` after the Unit targeting / active-reader proof-plan slice. It converts the saved `unit-battleengine-gameplay-static-contract.md` weapon/projectile handoff evidence into a bounded proof design for one selected weapon path through WalkerPart or JetPart weapon state, `CWeapon` event/filtering helpers, `ProjectileBurst` preset/fallback dispatch, and `CRound` spawn/arming handoff.

This plan does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, start Godot work, or claim runtime weapon fire behavior, projectile collision, damage, terrain interaction, target kill, stealth/cloak behavior, exact `CBattleEngine::WeaponFired` identity, `weapon_fire_breaks_stealth`, exact layouts, gameplay outcomes, or rebuild parity.

The plan records copied-profile guardrails, weapon/burst/round field-role unknowns, and stop conditions before any runtime/proof work can start.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

The percentage front door remains `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and `reverse-engineering/binary-analysis/static-reaudit-progress.json`. This proof plan does not create a new static RE percentage.

Primary static contract source: `reverse-engineering/binary-analysis/unit-battleengine-gameplay-static-contract.md`.

Relevant retained evidence:

- Wave1160 weapon/projectile targeting current-risk review (`wave1160-weapon-projectile-targeting-current-risk-review`): `19` metadata rows, `19` tag rows, `51` xref rows, `3272` instruction rows, and `19` decompile rows. It tag-normalized `0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback` and `0x005069f0 ProjectileBurst__SpawnFromCurrentPreset` with no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-011357_post_wave1160_weapon_projectile_targeting_current_risk_review_verified`.
- Wave1027 WalkerPart weapon spine review (`battleengine-walkerpart-weapon-spine-review-wave1027`): `12` primary metadata rows, `12` tag rows, `39` xref rows, `704` body-instruction rows, and `12` decompile rows; plus `5` context metadata rows, `5` context tag rows, `13` context xref rows, `718` context body-instruction rows, and `5` context decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-014543_post_wave1027_battleengine_walkerpart_weapon_spine_review_verified`.
- Wave1029 JetPart weapon/status review (`battleengine-jetpart-weapon-status-review-wave1029`): `13` primary metadata rows, `13` tag rows, `19` xref rows, `790` body-instruction rows, and `13` decompile rows; plus `11` context metadata rows, `11` context tag rows, `20` context xref rows, `1583` context body-instruction rows, and `11` context decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-025247_post_wave1029_battleengine_jetpart_weapon_status_review_verified`.
- Wave1020 projectile-burst spawn spine review (`projectile-burst-spawn-spine-review-wave1020`): `5` primary metadata rows, `5` tag rows, `22` xref rows, `1651` body-instruction rows, and `5` decompile rows; `7` context metadata rows, `9` context xref rows, `970` context body-instruction rows, and `7` context decompile rows; plus a `48`-row pointer-table export from `0x005dfc94`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified`.

## Static Anchors

The proof plan is built around saved retail Ghidra evidence, not source-body identity. Stuart source labels are useful for planning, but exact source-body identity and concrete layouts remain unproven unless a later proof slice establishes them.

| Surface | Static anchor |
| --- | --- |
| Auto-target/projectile wrapper boundary | `0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` is projectile/auto-target evidence only, not exact `CBattleEngine::WeaponFired` identity. |
| WalkerPart fire dispatch | `0x00413cc0 CBattleEngineWalkerPart__FireWeapon` clears main-part state `+0x588`, resolves current weapon through `CBattleEngineWalkerPart__GetCurrentWeapon`, and dispatches `ProjectileBurst__SpawnFromPercentBucketFallback` when active. |
| WalkerPart fired bookkeeping | `0x004140d0 CBattleEngineWalkerPart__WeaponFired` has one explicit stack argument and updates list, primary, and augmented weapon store value/heat/overheat paths through caller `CBattleEngine__CanSpawnBurstForResolvedEntry`. |
| JetPart fired bookkeeping | `0x00412050 CBattleEngineJetPart__WeaponFired` has one explicit stack argument and static evidence for JetPart quota, ammo, heat/overheat, and cooldown bookkeeping through caller `CBattleEngine__CanSpawnBurstForResolvedEntry`. |
| Current weapon resolver | `0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon` resolves primary/augmented/list weapon entries and is the WalkerPart current-weapon source for fire, charge, HUD/accessor, and movement paths. |
| Weapon target/profile filter | `0x005061f0 CWeapon__DoesTargetMaskMatchDistanceProfile` receives the current weapon in `ECX`, one `target_unit` stack argument, buckets weapon distance from `this+0x60`, walks `DAT_008553ec`, and tests selected profile mask `+0xa4` against `target_unit+0x34`. |
| Weapon charge/progress helper | `0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned` scans assigned weapon slots and updates charge/progress before burst paths. |
| Weapon burst event handler | `0x00506930 CWeapon__HandleFireBurstEvent` is DATA pointer slot `0x005dfc94`; it checks event id `0x1389`, calls `ProjectileBurst__SpawnFromCurrentPreset`, and schedules another `0x1389` event. This remains behavior-backed event-handler naming, not final source `CWeapon::Fire` identity. |
| ProjectileBurst fallback dispatcher | `0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback` uses `burstContext +0xa4`, calls current-preset body at `0x00506143`, schedules follow-up event `0x1389`, and is reached from bounded caller rows including WalkerPart fire/charge. |
| ProjectileBurst current-preset body | `0x005069f0 ProjectileBurst__SpawnFromCurrentPreset` creates projectile/effect objects from `burstContext +0xa0`, calls `ProjectileBurstPreset__GetListEntryIdByIndex`, and copies resource names through `CShell__CopyResourceNameToInlineBuffer`. |
| Preset/list entry accessor | `0x005078b0 ProjectileBurstPreset__GetListEntryIdByIndex` is a one-argument preset/list entry id accessor used by current-preset spawn. |
| Round target-reader sync | `0x004dac90 CRound__SelectBestTargetReaderAndSyncAimState` is the aim-space target-reader selection and event scheduling companion to the spawn handoff, not a runtime hit/collision proof. |
| Round spawn helper | `0x004db150 CRound__SpawnConfiguredProjectile` creates a projectile through `CWorldPhysicsManager__CreateProjectile(this+0xf0)`, builds a CRoundInitThing-like stack payload, and dispatches the new projectile init slot. |
| Round arming/trail helper | `0x004db630 CRound__ArmProjectileAndSpawnTrailEffect` arms projectile launch state, clamps/normalizes/scales velocity, clears effect-link state, optionally creates the configured trail effect, and syncs effect transform rows. |

## Static Field Roles To Preserve

These are static role labels for proof planning. Do not promote them to final C++ field names until exact layout proof exists.

| Offset / slot | Planned role in later proof |
| --- | --- |
| BattleEngine main-part `+0x588` | WalkerPart fire path state cleared before current weapon resolution. |
| BattleEngine weapon-store `+0x52c` | Selected weapon store value used by ammo and fired bookkeeping. |
| BattleEngine weapon-store `+0x544` | Selected weapon overheat flag role in WalkerPart/JetPart status helpers. |
| BattleEngine weapon-store `+0x55c` | Selected weapon heat/energy flag role in WalkerPart/JetPart status helpers. |
| Weapon `+0x60` | Weapon distance/charge-progress role used by profile checks and charge helpers. |
| Weapon profile `+0xa4` | Static target-mask/profile role in target-distance profile checks. |
| Target unit `+0x34` | Static target mask/classification input used by `CWeapon__DoesTargetMaskMatchDistanceProfile`. |
| Burst context `+0xa0` | Current-preset projectile/effect source context. |
| Burst context `+0xa4` | Percent-bucket fallback dispatch context. |
| Event id `0x1389` | Weapon burst follow-up event id used by `CWeapon__HandleFireBurstEvent` and ProjectileBurst fallback scheduling. |
| Pointer table `0x005dfc94` | CWeapon event/destructor table boundary; not promoted as a full contiguous vtable claim. |
| CRound `+0xf0` | Projectile creation configuration source passed to `CWorldPhysicsManager__CreateProjectile`. |

## Future Proof Checklist

The first executable proof after this plan should be scoped and copied-profile only. This plan records the expected evidence shape; it does not run that proof.

| Row | Planned proof item | Required evidence | Public-safe result |
| --- | --- | --- | --- |
| 1 | Single weapon-path selection | Choose one copied-profile level/state and one WalkerPart or JetPart weapon path whose static handoff can be observed without broad combat proof. | Sanitized weapon-path label, or a deferred note if no safe candidate is selected. |
| 2 | Static-to-runtime arm points | Choose non-invasive observation anchors around `CBattleEngineWalkerPart__FireWeapon`, `CBattleEngineWalkerPart__WeaponFired`, `CBattleEngineJetPart__WeaponFired`, `CWeapon__HandleFireBurstEvent`, `ProjectileBurst__SpawnFromCurrentPreset`, or `CRound__SpawnConfiguredProjectile`. | VA/function anchor and why it is scoped. |
| 3 | Weapon-state input boundary | Record which weapon-state family is being observed, without claiming exact WalkerPart, JetPart, CWeapon, burst, or round layout until later layout proof exists. | Weapon-state family label and static role, not raw private memory dumps. |
| 4 | ProjectileBurst handoff | Observe whether the selected static path reaches percent-bucket fallback or current-preset spawn only in a later runtime slice. | Separate planned pass/fail rows for weapon path, burst dispatch, and round spawn/arming. |
| 5 | Collision/damage separation | Treat Wave1161/Wave1162 collision and terrain rows as context only; do not include collision response, terrain contact, target damage, target death, or visual projectile proof in this slice. | Explicit deferred rows for collision, terrain, damage, and visual output. |
| 6 | Stealth boundary | Keep `weapon_fire_breaks_stealth`, cloak behavior, and exact retail `CBattleEngine::WeaponFired` identity outside the slice unless a later dedicated proof plan is written. | Boundary note remains explicit. |
| 7 | Layout restraint | Keep offsets as static role labels until runtime/layout evidence proves concrete fields. | Unknown-layout table remains explicit. |
| 8 | Stop conditions | Stop on crash, non-reproducible weapon path, ambiguous weapon identity, ambiguous projectile identity, unexpected file mutation, private artifact leakage, or any need to touch the installed game. | Documented blocked/deferred status instead of widening scope. |
| 9 | Rebuild handoff | Translate proven static-only behavior into weapon-to-projectile pseudocode only after the future proof result says which rows were observed. | Static pseudocode with runtime, layout, stealth, damage, and collision gaps marked. |

## Copied-Profile Guardrails

Any later runtime/proof execution must:

- Use copied profiles or app-owned artifact roots only.
- Never mutate the installed Steam game directory or the original `BEA.exe`.
- Verify byte/specimen assumptions before any patch candidate is considered.
- Keep screenshots, frames, videos, memory dumps, debugger logs, patch outputs, and private proof assets out of public release scope unless separately sanitized.
- Keep raw CDB/debugger output and private file paths in ignored evidence.
- Use a single selected weapon/path/state target; do not broaden into collision, terrain interaction, target damage, target kill, cloak/stealth, broad Unit/BattleEngine runtime proof, broad squad AI, visual projectile proof, or full gameplay outcome proof.

## Not Claimed

This plan is a static-to-proof planning artifact only. It does not prove:

- Runtime weapon fire behavior.
- Runtime projectile behavior.
- Runtime projectile collision behavior.
- Runtime terrain interaction.
- Runtime damage behavior.
- Runtime target kill behavior.
- Runtime stealth or cloak behavior.
- Exact retail `CBattleEngine::WeaponFired` identity.
- `weapon_fire_breaks_stealth`.
- Exact source `CWeapon::Fire` identity.
- Runtime target-selection behavior beyond the previously planned Unit targeting / active-reader slice.
- Exact concrete `CBattleEngine`, `CBattleEngineWalkerPart`, `CBattleEngineJetPart`, `CWeapon`, `ProjectileBurst`, `CRound`, `CShell`, weapon-store, target-profile, burst-context, or projectile layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate For This Planning Slice

This planning slice is complete only when:

- This document and its lore-book mirror match.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `reverse-engineering/binary-analysis/_index.md`, and `reverse-engineering/RE-INDEX.md` point to this plan.
- `reverse-engineering/binary-analysis/unit-battleengine-gameplay-static-contract.md` points to this plan without changing its static claim boundary.
- `release/readiness/weapon_projectile_spawn_handoff_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/weapon_projectile_spawn_handoff_proof_plan_probe.py --check` passes.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.
