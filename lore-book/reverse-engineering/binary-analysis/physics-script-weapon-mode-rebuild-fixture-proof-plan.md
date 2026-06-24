# PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan

Status: complete static weapon-mode value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-weapon-mode-rebuild-fixture-proof-plan`

Tracked schema:

- [physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json](physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json)

Selection tokens:

- `fixtureStatus=physics-script-weapon-mode-rebuild-fixture-proof-plan-complete-static-weapon-mode-value-interface-fixture-not-runtime-proof`
- `previousSlice=PhysicsScript Round Rebuild Fixture Proof Plan`
- `selectedNextSlice=PhysicsScript Unit Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-unit-rebuild-fixture-proof-plan`
- `selectedFixtureFamily=weapon-mode`
- `selectedFixturePath=weapon-mode-selected-value-id-interface-static-fixture`
- `selectedCandidateRank=8`
- `selectedValueInterfaceRowCount=9`
- `selectedValueIds=2/6/15/18/24/28/31/34/36`
- `factoryOnlyValueIds=15/36`
- `observedValueIds=1/2/3/4/5/6/8/9/10/11/12/13/14/16/17/18/19/20/21/22/23/24/26/27/28/29/30/31/32/33/34/35`
- `unselectedObservedValueIds=1/3/4/5/8/9/10/11/12/13/14/16/17/19/20/21/22/23/26/27/29/30/32/33/35`
- `selectedMixedPayloadShapeValueIds=2/24`

## Static Context

The loaded Ghidra database remains at `6411/6411 = 100.00%` function-quality closure with `0 / 0 / 0` commentless, exact-undefined, and `param_N` debt. The active current-risk re-audit remains `1179/1179 = 100.00%`.

This slice does not mutate Ghidra, BEA.exe, saves, game files, Godot files, or product UI. The latest verified Ghidra backup remains the Wave1219 static review backup because this is a static proof/materialization slice over already-validated evidence.

Boundary tokens: `runtimeExecution=false`; `godotWork=false`; `ghidraMutation=false`; `rebuildImplementation=false`.

## Fixture Surface

The Weapon-Mode fixture covers only the selected rebuild-facing value interface from the static crosswalk. The copied corpus has `145` Weapon-Mode top-level records, `1934` Weapon-Mode value nodes, `15007` raw value payload bytes preserved internally, and `33261` declared payload bytes. Those raw bytes are not published.

| Value ID | Field | Crosswalk class | Corpus status | Public-safe copied-corpus shape evidence |
| ---: | --- | --- | --- | --- |
| `2` | `roundNameOrRoundRef` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=112`; `two_scalar4_roundtrip=9`; `three_scalar4_roundtrip=23` |
| `6` | `muzzleEffect` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=118` |
| `15` | `clip` | `owned_string_at_08` | factory-only | no copied-corpus payload rows |
| `18` | `preFireEffect` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=15` |
| `24` | `launchSound` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=87`; `scalar4_roundtrip=4`; `three_scalar4_roundtrip=13` |
| `28` | `volleySize` | `rounded_scalar4` | observed | `scalar4_roundtrip=39` |
| `31` | `launchAngle3` | `three_scalar4` | observed | `three_scalar4_roundtrip=40` |
| `34` | `preFireSound` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=2` |
| `36` | `postFireSound` | `owned_string_at_08` | factory-only | no copied-corpus payload rows |

Value ids `15` and `36` are factory-only selected rows in the current copied corpus. They have static factory/apply evidence, but no copied-corpus payload rows are invented.

Value ids `1`, `3`, `4`, `5`, `8`, `9`, `10`, `11`, `12`, `13`, `14`, `16`, `17`, `19`, `20`, `21`, `22`, `23`, `26`, `27`, `29`, `30`, `32`, `33`, and `35` are not hidden. They are copied-corpus-observed Weapon-Mode rows outside the selected rebuild-facing crosswalk, preserved as `unselectedObservedValueIds=1/3/4/5/8/9/10/11/12/13/14/16/17/19/20/21/22/23/26/27/29/30/32/33/35` with `unselectedObservedScalar4PayloadCount=1247` and `unselectedObservedTwoScalarPayloadCount=225`.

## Static Anchors

| Anchor | Static role |
| --- | --- |
| `CPhysicsScriptStatements__CreateStatementType4` | Weapon-Mode value factory dispatch. |
| `CWeaponModeStatement__LoadFromMemBuffer` | Weapon-Mode top-level statement loader. |
| `CPhysicsWeaponModeValueList__LoadFromMemBuffer` | Weapon-Mode value-list loader. |
| `CWeaponModeStatement__CreateWeaponModeAndRecurse` | Weapon-Mode create/register bridge and child recursion anchor. |
| `DAT_008553ec` | Weapon-Mode registry global. |
| `CWeaponRound__ApplyToWeaponModeByName` | Selected `roundNameOrRoundRef` static apply anchor. |
| `CWeaponMuzzleEffect__ApplyToWeaponModeByName` | Selected `muzzleEffect` static apply anchor. |
| `CWeaponClip__ApplyToWeaponModeByName` | Selected `clip` static apply anchor. |
| `CWeaponPreFireEffect__ApplyToWeaponModeByName` | Selected `preFireEffect` static apply anchor. |
| `CWeaponLaunchSound__ApplyToWeaponModeByName` | Selected `launchSound` static apply anchor. |
| `CWeaponVolleySize__ApplyToWeaponModeByName` | Selected `volleySize` static apply anchor. |
| `CWeaponLaunchAngle__LoadFromMemBuffer` | Selected `launchAngle3` three-scalar loader anchor. |
| `CWeaponPreFireSound__ApplyToWeaponModeByName` | Selected `preFireSound` static apply anchor. |
| `CWeaponPostFireSound__ApplyToWeaponModeByName` | Selected `postFireSound` static apply anchor. |

## Requirement Rows

| Row | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `family-fixture` | satisfied-static-with-factory-only-and-unselected-observed-boundaries | Weapon-Mode has `32` observed ids, `9` selected rows, `7` observed selected rows, `2` factory-only selected rows, and `25` unselected observed ids. | Static family-selection proof only. |
| `loader-fixture` | satisfied-static | `CPhysicsScriptStatements__CreateStatementType4`, `CWeaponModeStatement__LoadFromMemBuffer`, `CPhysicsWeaponModeValueList__LoadFromMemBuffer`, `CWeaponModeStatement__CreateWeaponModeAndRecurse`, and `DAT_008553ec`. | Static loader/factory/registry bridge only. |
| `value-interface-fixture` | satisfied-static | Selected value ids `2`, `6`, `15`, `18`, `24`, `28`, `31`, `34`, and `36` with nine rebuild-facing field names. | Selected value-id interface only, not complete value semantics. |
| `factory-only-boundary-fixture` | satisfied-explicit-boundary | Value ids `15` and `36` are factory-only selected rows in this copied-corpus aggregate. | Static factory/apply evidence only; no copied-corpus payload values are invented. |
| `unselected-observed-boundary-fixture` | satisfied-explicit-boundary | `25` copied-corpus-observed Weapon-Mode value ids are intentionally outside this selected rebuild-facing crosswalk. | Observed raw Weapon-Mode payload shapes are preserved as deferred boundary rows instead of receiving invented semantics. |
| `payload-shape-fixture` | satisfied-public-safe | Selected owned-string, rounded-scalar, and three-scalar rows with mixed shape boundaries for `roundNameOrRoundRef` and `launchSound`. | Public-safe payload shape only; no raw strings or numeric meanings. |
| `weapon-mode-field-fixture` | satisfied-static | `roundNameOrRoundRef`, `muzzleEffect`, `clip`, `preFireEffect`, `launchSound`, `volleySize`, `launchAngle3`, `preFireSound`, and `postFireSound` are anchored to Weapon-Mode apply/load helpers and `DAT_008553ec`. | Static Weapon-Mode field boundary only, not runtime firing cadence, projectile spawn, launch-angle, effect, or audio behavior. |
| `stop-fixture` | enforced | Runtime/Godot/Ghidra/patch/product/rebuild guards remain false with zero runtime rows. | Defer instead of broadening into runtime Weapon-Mode firing, projectile launch, effects, audio, or rebuild implementation. |

## What This Proves

- The selected Weapon-Mode value-ID interface is materialized as public-safe static fixture rows.
- The selected Weapon-Mode rows preserve round/effect/sound/volley/launch-angle factory/apply/registry anchors.
- The selected fixture preserves mixed payload-shape boundaries for `roundNameOrRoundRef` and `launchSound`.
- Factory-only selected rows `clip` and `postFireSound` remain explicit boundary debt instead of receiving invented corpus evidence.
- The large unselected observed Weapon-Mode value-ID set remains explicit boundary debt instead of receiving invented meanings.
- The next static child lane is `PhysicsScript Unit Rebuild Fixture Proof Plan`.

## What This Does Not Prove

This does not prove runtime PhysicsScript behavior, runtime Weapon-Mode behavior, runtime Weapon-Mode round selection, runtime Weapon-Mode effect behavior, runtime Weapon-Mode audio behavior, runtime Weapon-Mode volley behavior, runtime Weapon-Mode launch-angle behavior, runtime weapon firing cadence, runtime projectile spawn, runtime projectile outcomes, serialized PhysicsScript completeness, exact PhysicsScript layouts, exact Weapon-Mode record layout, complete value-ID semantics, raw string identity, raw numeric value meaning, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
