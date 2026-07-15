# BattleEngine Source-To-Binary Gap Probe

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`); `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe reverse-engineering evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `0eedd163`
Evidence-report commit: 43de4a6f077194b430a616e8c73e58b90a57fe4f

> **Current supersession (2026-07-12):** this report preserves the gap state as
> measured in May. A later read-only re-review now resolves selected
> BattleEngine/JetPart movement owners at high static confidence. Runtime
> behavior and measured constants remain pending; see
> `reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md`.

## Purpose

This pass adds a read-only gap probe that compares the selected BattleEngine source-anchor mechanics coverage with the existing retail-binary function mapping docs. It prevents an overclaim: source mechanics anchors are now machine-checked, and related binary function families are documented, but the individual mechanics anchors still need retail-binary/Ghidra read-back before exact Steam function identity can be claimed.

No game runtime, Ghidra mutation, executable patching, or installed-game access occurred in this pass.

## Current Status Update - 2026-05-07

This report remains the historical introduction for the BattleEngine source-to-binary gap probe. The current checked source-anchor set has since expanded beyond the original 11 anchors.

Latest source-to-binary gap baseline:

- `npm run test:battleengine-source-binary-gap`: PASS, binary families `3/3`, source anchors `17/17`.
- The current source-only pending-binary-identity count is `1`.
- `release/readiness/battleengine_remaining_source_only_name_scan_2026-05-07.md` adds direct-name triage for the remaining weapon-fired stealth anchor. It checks `5862` current Ghidra function-name rows and finds `0` strict direct-name matches; this is triage only, not absence proof.
- `release/readiness/battleengine_weapon_stealth_operand_search_2026-05-07.md` adds operand-token triage for suspected stealth-adjacent retail fields. It checks `377` operand-token rows, `64` object-offset rows, and finds `0` weapon/fire/projectile object-offset rows; this is also triage only, not absence proof.
- `release/readiness/battleengine_weapon_fired_source_callsite_2026-05-07.md` adds source-callsite triage. It checks `8` source `WeaponFired` occurrences and finds `0` unexpected direct callsites outside expected declarations/definitions and the part-delegation calls inside `CBattleEngine::WeaponFired`; this explains why exact retail identity may not appear as a live one-to-one method.
- `release/readiness/battleengine_projectile_helper_stealth_scan_2026-05-08.md` narrows the already named `0x00406560` projectile/targeting helper: the helper still carries target resolution, target filtering, tracked-set removal, forward-target selection, projectile emission, and the known `0.01` stealth-style targeting context, but no source-style writes to tracked stealth-adjacent offsets were observed. This does not identify the retail `CBattleEngine::WeaponFired` body and keeps `weapon_fire_breaks_stealth` source-only.
- `release/readiness/battleengine_addprojectile_xrefs_2026-05-09.md` narrows direct projectile-emission xrefs: the current read-only Ghidra xref export has four direct `CBattleEngine__AddProjectile` callers, all from `0x00406560`. This does not rule out indirect, virtual-dispatch, callback, inlined, or runtime-only weapon-fire paths and keeps `weapon_fire_breaks_stealth` source-only.
- `release/readiness/battleengine_weapon_construction_candidate_2026-05-09.md` adds construction/vtable triage: current weapon creation reaches `CEquipment__ctor_like_00505e00`, vtable `0x005dfc94`, and raw slot-0 code `0x00506930`, whose checked body reaches projectile creation/set-target helper calls without tracked stealth-reset tokens. This is a stronger construction-side projectile body candidate, not exact source identity, and keeps `weapon_fire_breaks_stealth` source-only.
- `release/readiness/battleengine_weapon_slot0_boundary_2026-05-09.md` tightens that construction-side raw boundary: the current slot-0 stub starts at `0x00506930`, calls inner body `0x005069f0`, and the checked inner body returns at `0x005078ab` before first post-return row `0x005078b0`. This is still raw-boundary evidence only, not exact `CWeapon::Fire` / `CBattleEngine::WeaponFired` identity, and keeps `weapon_fire_breaks_stealth` source-only.
- `release/readiness/battleengine_weapon_slot0_xrefs_2026-05-09.md` narrows direct xref/caller context: `0x00506930` has one direct `DATA` ref from vtable entry `0x005dfc94` and no direct code refs in the checked export, while `0x005069f0` is currently named `CEngine__SpawnProjectileBurstFromCurrentPreset` and is called by raw outer-stub callsite `0x005069b6` plus named caller `CGeneralVolume__SpawnBurstFromPresetWithFallback` at `0x00506010`. This still does not prove exact source identity or runtime stealth behavior, and keeps `weapon_fire_breaks_stealth` source-only.
- `release/readiness/battleengine_weapon_slot0_function_recovery_2026-05-09.md` closes the raw function-boundary part of that gap: dry-run create reported `would_create`, headless apply created and named `0x00506930` as conservative `CWeapon__VFunc_00_00506930`, and read-back verifies the saved boundary through decompile, all-functions, xrefs, and instruction ownership. This still does not prove exact source identity or runtime stealth behavior, and keeps `weapon_fire_breaks_stealth` source-only.
- `release/readiness/battleengine_weapon_event_handler_rename_2026-05-09.md` improves the saved Ghidra naming for that recovered boundary: `0x00506930` is now `CWeapon__HandleFireBurstEvent`, and the adjacent destructor-like slot `0x00505f70` is now `CWeapon__scalar_deleting_dtor`. This is behavior-backed semantic naming, not exact `CWeapon::Fire` / `CBattleEngine::WeaponFired` identity or runtime stealth proof, and keeps `weapon_fire_breaks_stealth` source-only.
- `release/readiness/battleengine_weapon_burst_comment_pass_2026-05-09.md` records a saved Ghidra comment pass for `0x00506930`, `0x00505f70`, `0x005069f0`, and `0x00506010`: dry-run/apply/read-back verified proof-boundary comments beside the current weapon/burst-cluster functions. This improves local Ghidra context but does not rename `0x005069f0` / `0x00506010`, harden signatures, prove exact source identity, or close runtime stealth behavior; `weapon_fire_breaks_stealth` remains source-only.
- `release/readiness/battleengine_weapon_burst_caller_xrefs_2026-05-09.md` narrows the caller side of `0x00506010`: the checked direct xref rows are spread across UnitAI, Sentinel, CEngine wrapper, and CGeneralVolume update/reset paths, plus two raw no-function callsites, with no obvious Weapon- or BattleEngine-named direct caller. This weakens a narrow weapon-specific interpretation for `0x00506010` and keeps `weapon_fire_breaks_stealth` source-only.
- `release/readiness/battleengine_weapon_burst_raw_callsites_2026-05-09.md` narrows the two raw callsites into `0x00506010`: bounded instruction windows around `0x0044e093` and `0x004f4bd6` contain the expected target calls, remain outside Ghidra-owned function rows, and expose no obvious Weapon- or BattleEngine-named owner. This still does not create function boundaries or prove exact source/runtime identity, and keeps `weapon_fire_breaks_stealth` source-only.
- `release/readiness/ghidra_battleengine_cloak_hud_interpolation_signature_tranche_2026-05-09.md` corrects the saved `0x0040d4d0` label to source-aligned `CBattleEngine__HandleCloak` and records adjacent lock-percentage, HUD sample, and interpolation helpers. This strengthens the static cloak source bridge, but runtime cloak activation, fire-while-cloaked behavior, exact retail `CBattleEngine::WeaponFired`, and `weapon_fire_breaks_stealth` remain open.
- `release/readiness/ghidra_battleengine_volume_augment_pickup_signature_tranche_2026-05-09.md` corrects six BattleEngine volume/augment/pickup-adjacent saved signatures, including `0x0040de40` as `CBattleEngine__AugmentWeapon`. This strengthens the augmented-weapon activation bridge, but runtime augmented-weapon behavior, concrete layout, exact source identity for every target, exact retail `CBattleEngine::WeaponFired`, and `weapon_fire_breaks_stealth` remain open.
- `release/readiness/ghidra_weapon_burst_provisional_review_2026-05-09.md` corrects the two previously provisional burst helpers to owner-neutral `ProjectileBurst__SpawnFromCurrentPreset` at `0x005069f0` and `ProjectileBurst__SpawnFromPercentBucketFallback` at `0x00506010`. This removes the stale owner-specific `CEngine` / `CGeneralVolume` implication and hardens both `burstContext` signatures; the later raw-boundary follow-up supersedes the old "two raw callers still open" status while exact `CWeapon::Fire`, exact retail `CBattleEngine::WeaponFired`, runtime stealth behavior, and `weapon_fire_breaks_stealth` remain open.
- `release/readiness/ghidra_weapon_burst_raw_boundary_recovery_2026-05-10.md` recovers the two prior raw callsites into `0x00506010` as owner-neutral saved boundaries: `ProjectileBurstCallerBoundary_0044e020` for callsite `0x0044e093` and `ProjectileBurstCallerBoundary_004f4920` for callsite `0x004f4bd6`, with vtable DATA refs from `0x005e0538` and `0x005e10e8`. This closes the raw-boundary part of that local caller gap, but exact `CWeapon::Fire`, exact retail `CBattleEngine::WeaponFired`, runtime stealth behavior, concrete layouts/tags/locals, and `weapon_fire_breaks_stealth` remain open.
- `release/readiness/ghidra_battleengine_walkerpart_source_parity_correction_2026-05-10.md` corrects a 26-target BattleEngine/JetPart/WalkerPart source-parity cluster, including `CBattleEngineWalkerPart__FireWeapon`, `CBattleEngineWalkerPart__WeaponFired`, and `CBattleEngineWalkerPart__CanWeaponFire`, plus the BattleEngine/JetPart heat-energy helper swap. This strengthens WalkerPart weapon-helper identity but still does not identify exact retail `CBattleEngine::WeaponFired`, prove runtime fire-while-cloaked behavior, or close `weapon_fire_breaks_stealth`.
- The current partial retail candidate count is `16`:
  - Four selected damage anchors have a public-safe source/read-back bridge through `CUnit__ApplyDamage`, but exact `CBattleEngine::Damage` control-flow identity remains unresolved.
  - Transform special-move rejection has public-safe transition-lockout candidate evidence through `CMonitor__UpdateFlightWalkerTransitionState`, but exact special-move method identity and runtime behavior remain unresolved.
  - Three selected Morph event/energy-gate anchors have a public-safe transition-helper bridge through `CMonitor__UpdateFlightWalkerTransitionState`, but complete `CBattleEngine::Morph()` identity remains unresolved.
  - Two selected jet energy/stall anchors have a public-safe candidate bridge through `CMonitor__Process`, but exact `BattleEngineJetPart` method identity remains unresolved.
  - Walker movement/recharge context now has a stronger public-safe saved-Ghidra bridge through `CBattleEngineWalkerPart__Move`, `CBattleEngineWalkerPart__GoingIntoWater`, and `CBattleEngineWalkerPart__Slide`, but runtime movement/recharge behavior and concrete layouts remain unresolved.
  - Cloak behavior has public-safe candidate evidence through `CBattleEngine__HandleCloak` at `0x0040d4d0` (older notes may carry the superseded `CGeneralVolume__Update4ACLatchFromHeightAndA0` label), `CMonitor__Process`, target-scaling, and render context, but runtime activation/fire behavior remains unresolved.
  - Player god-mode toggles have a public-safe source/binary/runtime-note mechanism bridge, but exact Steam `CPlayer::SetIsGod` identity and environmental-hazard boundaries remain unresolved.
  - Configuration defaults have a public-safe value-level source-to-binary-doc bridge, but exact retail function body identity remains unresolved.
  - Target-lock behavior has a public-safe source/read-back bridge through related target/projectile helper evidence, but exact `CBattleEngine::HandleLocks` control-flow identity remains unresolved.
  - Augmented-weapon activation/depletion has a stronger public-safe saved-Ghidra bridge through `CBattleEngine__AugmentWeapon` at `0x0040de40` and caller context in `0x004081c0`, but runtime behavior, concrete layout, and exact source method boundaries remain unproven.
- `release/readiness/battleengine_cloak_stealth_candidate_2026-05-07.md` adds bounded read-only candidate evidence for cloak latch/config checks, active energy burn, forced-decloak clearing, stealth-style interpolation, target-range scaling, and render context, but exact source-method identity, runtime behavior, render-flag identity, and weapon-fired stealth reset remain unproven.
- Additional source-only anchors added after this report cover source special-move transform rejection, cloak behavior, jet energy/stall/recharge behavior, and weapon-fired stealth reset. Selected damage anchors, transform special-move rejection, Morph event/energy-gate anchors, jet energy/stall anchors, walker recharge, cloak behavior, player god-mode toggles, configuration defaults, target-lock, and augmented-weapon charge/decay/reset have moved to partial retail candidate status, not exact identity. Weapon-fired stealth reset remains source-only.

The proof boundary is unchanged for exact identity: the gap probe intentionally prevents source-reference behavior or partial retail candidates from being presented as exact Steam retail binary identity before read-back closes that boundary.

## Command

```powershell
npm run test:battleengine-source-binary-gap
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_source_binary_gap_probe.py --check
```

Working directory:

```text
repo root
```

Result: PASS.

Important output summary:

```text
BattleEngine source-to-binary gap probe
Status: pass
Binary families: 3/3
Source anchors: 11/11
- PASS: BattleEngine.cpp: named functions 15
- PASS: BattleEngineDataManager.cpp: named functions 30
- PASS: Player.cpp: named functions 9
Source-only anchors pending binary identity: 11
```

## What This Proves

- The repo has a repeatable read-only check that the current binary docs include named function families for `BattleEngine.cpp`, `BattleEngineDataManager.cpp`, and `Player.cpp`.
- The probe reuses the BattleEngine source-anchor coverage baseline and confirms the selected 11 source anchors are still present.
- The probe records 11 selected mechanics anchors as `SOURCE_ONLY_PENDING_BINARY_IDENTITY` so docs and future agents do not accidentally present source evidence as Steam retail binary identity.
- The generated JSON report is ignored/private under `subagents/` and contains repo-relative docs, public-safe function names/addresses already present in tracked docs, and gap labels only.

## What This Does Not Prove

- Exact Steam retail binary identity for each individual damage, shield, transform, energy, configuration, or god-mode source anchor.
- Ghidra rename-map mutation or read-back for these anchors.
- Runtime gameplay-state interpretation.
- Continuous frame streaming.
- Rebuildable open-source gameplay implementation.

## Privacy / Release Safety

The committed evidence is public-safe. It does not include binaries, private absolute paths, source excerpts, runtime captures, screenshots, private assets, or Ghidra mutation logs.

The raw JSON report remains ignored local evidence under
`local-lab/battleengine-source-binary-gap/`.

## Recommended Next Step

Use this gap probe as the handoff for a later read-only Ghidra/source-to-binary identity pass. That future pass should identify exact retail functions for one mechanics anchor at a time, read back the current names/decompile evidence, and record uncertainty without mutating Ghidra or the installed game.
