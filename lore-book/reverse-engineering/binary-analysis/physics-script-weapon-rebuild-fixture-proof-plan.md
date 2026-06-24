# PhysicsScript Weapon Rebuild Fixture Proof Plan

Status: complete static weapon value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-weapon-rebuild-fixture-proof-plan`

Tracked schema:

- [physics-script-weapon-rebuild-fixture-proof-plan.v1.json](physics-script-weapon-rebuild-fixture-proof-plan.v1.json)

Follow-up Round fixture result: [PhysicsScript Round Rebuild Fixture Proof Plan](physics-script-round-rebuild-fixture-proof-plan.md), backed by [physics-script-round-rebuild-fixture-proof-plan.v1.json](physics-script-round-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-round-rebuild-fixture-proof-plan-complete-static-round-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan and selectedNextScope=physics-script-weapon-mode-rebuild-fixture-proof-plan while preserving selectedFixtureFamily=round, selectedFixturePath=round-selected-value-id-interface-static-fixture, selectedValueIds=4/8/9/24/33/35/36, unselectedObservedValueIds=1/2/3/5/6/10/11/12/13/14/15/16/17/18/19/22/23/26/27/28/29/30/31/32/37/38, selectedMixedPayloadShapeValueIds=8/9, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. Static anchors include CRoundStatement__LoadFromMemBuffer, CPhysicsRoundValueList__LoadFromMemBuffer, CRoundStatement__CreateRoundAndRecurse, and DAT_008553f0. Active next static child lane: PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan.

Selection tokens:

- `fixtureStatus=physics-script-weapon-rebuild-fixture-proof-plan-complete-static-weapon-value-interface-fixture-not-runtime-proof`
- `previousSlice=PhysicsScript Component Rebuild Fixture Proof Plan`
- `selectedNextSlice=PhysicsScript Round Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-round-rebuild-fixture-proof-plan`
- `selectedFixtureFamily=weapon`
- `selectedFixturePath=weapon-selected-value-id-interface-static-fixture`
- `selectedCandidateRank=6`
- `selectedValueInterfaceRowCount=4`
- `selectedValueIds=1/4/5/14`
- `observedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/14`
- `unselectedObservedValueIds=2/3/6/7/8/9/10/11/12/13`
- `selectedMixedPayloadShapeValueIds=1`

## Static Context

The loaded Ghidra database remains at `6411/6411 = 100.00%` function-quality closure with `0 / 0 / 0` commentless, exact-undefined, and `param_N` debt. The active current-risk re-audit remains `1179/1179 = 100.00%`.

This slice does not mutate Ghidra, BEA.exe, saves, game files, Godot files, or product UI. The latest verified Ghidra backup remains the Wave1219 static review backup because this is a static proof/materialization slice over already-validated evidence.

Boundary tokens: `runtimeExecution=false`; `godotWork=false`; `ghidraMutation=false`; `rebuildImplementation=false`.

## Fixture Surface

The Weapon fixture deliberately covers only the selected rebuild-facing value interface from the static crosswalk. The copied corpus has `139` Weapon top-level records, `286` Weapon value nodes, `4082` raw value payload bytes preserved internally, and `8894` declared payload bytes. Those raw bytes are not published.

| Value ID | Field | Crosswalk class | Corpus status | Public-safe copied-corpus shape evidence |
| ---: | --- | --- | --- | --- |
| `1` | `chargeLevel` | `owned_string_and_scalar_shape` | observed | `raw_preserved_other=141`; `three_scalar4_roundtrip=1` |
| `4` | `consumption` | `scalar4` | observed | `scalar4_roundtrip=15` |
| `5` | `iconName` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=15` |
| `14` | `versusAir` | `scalar4` | observed | `scalar4_roundtrip=12` |

There are no factory-only selected Weapon rows in this fixture.

Value ids `2`, `3`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, and `13` are not hidden. They are copied-corpus-observed Weapon rows outside the selected rebuild-facing crosswalk, preserved as `unselectedObservedValueIds=2/3/6/7/8/9/10/11/12/13` with `unselectedObservedScalar4PayloadCount=102`.

## Static Anchors

| Anchor | Static role |
| --- | --- |
| `CPhysicsScriptStatements__CreateStatementType3` | Weapon value factory dispatch. |
| `CWeaponStatement__LoadFromMemBuffer` | Weapon top-level statement loader. |
| `CPhysicsWeaponValueList__LoadFromMemBuffer` | Weapon value-list loader. |
| `CWeaponStatement__CreateWeaponAndRecurse` | Weapon create/register bridge and child recursion anchor. |
| `DAT_008553e8` | Weapon registry global. |
| `CWeaponChargeLevel__LoadFromMemBuffer` | Selected `chargeLevel` static load anchor. |
| `CWeaponConsumption__ApplyToWeaponByName` | Selected `consumption` static apply anchor. |
| `CWeaponIconName__ApplyToWeaponByName` | Selected `iconName` static apply anchor. |
| `CWeaponVersusAir__ApplyToWeaponByName` | Selected `versusAir` static apply anchor. |

## Requirement Rows

| Row | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `family-fixture` | satisfied-static-with-unselected-observed-boundary | Weapon has `14` observed ids, `4` selected rows, zero factory-only selected rows, and `10` unselected observed ids. | Static family-selection proof only. |
| `loader-fixture` | satisfied-static | `CPhysicsScriptStatements__CreateStatementType3`, `CWeaponStatement__LoadFromMemBuffer`, `CPhysicsWeaponValueList__LoadFromMemBuffer`, `CWeaponStatement__CreateWeaponAndRecurse`, and `DAT_008553e8`. | Static loader/factory/registry bridge only. |
| `value-interface-fixture` | satisfied-static | Selected value ids `1`, `4`, `5`, and `14` with four rebuild-facing field names. | Selected value-id interface only, not complete value semantics. |
| `payload-shape-fixture` | satisfied-public-safe | `chargeLevel` mixed shape, `consumption` scalar4, `iconName` owned string, `versusAir` scalar4, and explicit unselected observed scalar boundary. | Public-safe payload shape only; no raw strings or numeric meanings. |
| `stop-fixture` | enforced | Runtime/Godot/Ghidra/patch/product/rebuild guards remain false with zero runtime rows. | Defer instead of broadening into runtime firing, damage, cadence, visuals, audio, or rebuild implementation. |

## What This Proves

- The selected Weapon value-ID interface is materialized as public-safe static fixture rows.
- The selected Weapon rows preserve `chargeLevel`, `consumption`, `iconName`, and `versusAir` factory/apply/registry anchors.
- The selected fixture preserves the `chargeLevel` mixed payload-shape boundary and unselected observed Weapon value-ID debt.
- The next static child lane is `PhysicsScript Round Rebuild Fixture Proof Plan`.

## What This Does Not Prove

This does not prove runtime PhysicsScript behavior, runtime weapon behavior, runtime weapon charge behavior, runtime weapon firing behavior, runtime weapon damage behavior, serialized PhysicsScript completeness, exact PhysicsScript layouts, exact weapon record layout, complete value-ID semantics, raw string identity, raw numeric value meaning, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
