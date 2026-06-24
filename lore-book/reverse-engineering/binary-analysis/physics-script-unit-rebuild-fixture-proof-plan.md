# PhysicsScript Unit Rebuild Fixture Proof Plan

Status: complete static Unit value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-unit-rebuild-fixture-proof-plan`

Tracked schema:

- [physics-script-unit-rebuild-fixture-proof-plan.v1.json](physics-script-unit-rebuild-fixture-proof-plan.v1.json)

Selection tokens:

- `fixtureStatus=physics-script-unit-rebuild-fixture-proof-plan-complete-static-unit-value-interface-fixture-not-runtime-proof`
- `previousSlice=PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan`
- `selectedNextSlice=PhysicsScript Fixture Family Completion Rollup Proof Plan`
- `selectedNextScope=physics-script-fixture-family-completion-rollup-proof-plan`
- `selectedFixtureFamily=unit`
- `selectedFixturePath=unit-selected-value-id-interface-static-fixture`
- `selectedCandidateRank=9`
- `selectedValueInterfaceRowCount=8`
- `selectedValueIds=7/8/20/21/22/25/60/61`
- `factoryOnlyValueIds=20/25`
- `observedValueIds=1/2/3/5/6/7/8/9/10/11/12/13/14/18/21/22/23/27/28/29/30/31/32/33/36/38/39/40/41/42/43/44/45/46/47/48/50/51/52/53/54/55/56/57/58/60/61/62/63/65/66/67/68/70`
- `unselectedObservedValueIds=1/2/3/5/6/9/10/11/12/13/14/18/23/27/28/29/30/31/32/33/36/38/39/40/41/42/43/44/45/46/47/48/50/51/52/53/54/55/56/57/58/62/63/65/66/67/68/70`
- `selectedMixedPayloadShapeValueIds=none`

## Static Context

The loaded Ghidra database remains at `6411/6411 = 100.00%` function-quality closure with `0 / 0 / 0` commentless, exact-undefined, and `param_N` debt. The active current-risk re-audit remains `1179/1179 = 100.00%`.

This slice does not mutate Ghidra, BEA.exe, saves, game files, Godot files, or product UI. The latest verified Ghidra backup remains the Wave1219 static review backup because this is a static proof/materialization slice over already-validated evidence.

Boundary tokens: `runtimeExecution=false`; `godotWork=false`; `ghidraMutation=false`; `rebuildImplementation=false`.

## Fixture Surface

The Unit fixture covers only the selected rebuild-facing Unit value interface from the static crosswalk. The copied corpus has `160` Unit top-level records, `2338` Unit value nodes, `28840` raw value payload bytes preserved internally, and `50284` declared payload bytes. Those raw bytes are not published.

| Value ID | Field | Crosswalk class | Corpus status | Public-safe copied-corpus shape evidence |
| ---: | --- | --- | --- | --- |
| `7` | `use` | `compound_owned_string_shape` | observed | `raw_preserved_other=118` |
| `8` | `behaviour` | `nested_enum_child` | observed | `scalar4_roundtrip=160` |
| `20` | `importance` | `scalar4` | factory-only | no copied-corpus payload rows |
| `21` | `soundMaterial` | `rounded_scalar4` | observed | `scalar4_roundtrip=123` |
| `22` | `strafeChange` | `scalar4` | observed | `scalar4_roundtrip=2` |
| `25` | `navMap` | `nested_enum_child` | factory-only | no copied-corpus payload rows |
| `60` | `standingLegPlacementArea` | `scalar4` | observed | `scalar4_roundtrip=3` |
| `61` | `maxLegsLifted` | `rounded_scalar4` | observed | `scalar4_roundtrip=4` |

Value ids `20` and `25` are factory-only selected rows in the current copied corpus. They have static factory/apply evidence, but no copied-corpus payload rows are invented.

Value id `7` is selected but remains `raw_preserved_other` in the public fixture. The fixture preserves count and shape evidence only; raw strings, raw bytes, and runtime `use` behavior are not published or inferred.

Value ids `1`, `2`, `3`, `5`, `6`, `9`, `10`, `11`, `12`, `13`, `14`, `18`, `23`, `27`, `28`, `29`, `30`, `31`, `32`, `33`, `36`, `38`, `39`, `40`, `41`, `42`, `43`, `44`, `45`, `46`, `47`, `48`, `50`, `51`, `52`, `53`, `54`, `55`, `56`, `57`, `58`, `62`, `63`, `65`, `66`, `67`, `68`, and `70` are not hidden. They are copied-corpus-observed Unit rows outside the selected rebuild-facing crosswalk, preserved as `unselectedObservedValueIds=1/2/3/5/6/9/10/11/12/13/14/18/23/27/28/29/30/31/32/33/36/38/39/40/41/42/43/44/45/46/47/48/50/51/52/53/54/55/56/57/58/62/63/65/66/67/68/70` with `unselectedObservedScalar4PayloadCount=912`, `unselectedObservedTwoScalarPayloadCount=123`, `unselectedObservedThreeScalarPayloadCount=31`, `unselectedObservedOwnedStringShapePayloadCount=511`, and `unselectedObservedRawPreservedOtherPayloadCount=351`.

## Static Anchors

| Anchor | Static role |
| --- | --- |
| `CPhysicsScriptStatements__CreateStatementType2` | Unit value factory dispatch. |
| `CUnitStatement__LoadFromMemBuffer` | Unit top-level statement loader. |
| `CPhysicsUnitValueList__LoadFromMemBuffer` | Unit value-list loader. |
| `CUnitStatement__CreateUnitAndRecurse` | Unit create/register bridge and child recursion anchor. |
| `CUnitAI__CreateAndRegisterByName` | UnitAI registry creation anchor. |
| `DAT_008553fc` | UnitAI registry global. |
| `CUnitUse__ApplyToUnitData` | Selected `use` static apply anchor. |
| `CUnitBehaviour__ApplyToUnitData` | Selected `behaviour` static apply anchor. |
| `CUnitImportance__ApplyToUnitData` | Selected `importance` static apply anchor. |
| `CUnitSoundMaterial__ApplyToUnitData` | Selected `soundMaterial` static apply anchor. |
| `CUnitStrafeChange__ApplyToUnitData` | Selected `strafeChange` static apply anchor. |
| `CUnitNavMap__ApplyToUnitData` | Selected `navMap` static apply anchor. |
| `CUnitStandingLegPlacementArea__ApplyToUnitData` | Selected `standingLegPlacementArea` static apply anchor. |
| `CUnitMaxLegsLifted__ApplyToUnitData` | Selected `maxLegsLifted` static apply anchor. |

## Requirement Rows

| Row | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `family-fixture` | satisfied-static-with-factory-only-and-unselected-observed-boundaries | Unit has `54` observed ids, `8` selected rows, `6` observed selected rows, `2` factory-only selected rows, and `48` unselected observed ids. | Static family-selection proof only. |
| `loader-fixture` | satisfied-static | `CPhysicsScriptStatements__CreateStatementType2`, `CUnitStatement__LoadFromMemBuffer`, `CPhysicsUnitValueList__LoadFromMemBuffer`, `CUnitStatement__CreateUnitAndRecurse`, and `DAT_008553fc`. | Static loader/factory/registry bridge only. |
| `value-interface-fixture` | satisfied-static | Selected value ids `7`, `8`, `20`, `21`, `22`, `25`, `60`, and `61` with eight rebuild-facing field names. | Selected value-id interface only, not complete value semantics. |
| `factory-only-boundary-fixture` | satisfied-explicit-boundary | Value ids `20` and `25` are factory-only selected rows in this copied-corpus aggregate. | Static factory/apply evidence only; no copied-corpus payload values are invented. |
| `unselected-observed-boundary-fixture` | satisfied-explicit-boundary | `48` copied-corpus-observed Unit value ids are intentionally outside this selected rebuild-facing crosswalk. | Observed raw Unit payload shapes are preserved as deferred boundary rows instead of receiving invented semantics. |
| `payload-shape-fixture` | satisfied-public-safe | Selected raw-preserved compound `use`, nested-enum, scalar, and rounded-scalar rows. | Public-safe payload shape only; no raw strings or numeric meanings. |
| `unit-field-fixture` | satisfied-static | `use`, `behaviour`, `importance`, `soundMaterial`, `strafeChange`, `navMap`, `standingLegPlacementArea`, and `maxLegsLifted` are anchored to Unit apply helpers and `DAT_008553fc`. | Static Unit field boundary only, not runtime AI, movement, sound-material, navigation, or leg-placement behavior. |
| `stop-fixture` | enforced | Runtime/Godot/Ghidra/patch/product/rebuild guards remain false with zero runtime rows. | Defer instead of broadening into runtime Unit AI, movement, navigation, sound-material, leg placement, or rebuild implementation. |

## What This Proves

- The selected Unit value-ID interface is materialized as public-safe static fixture rows.
- The selected Unit rows preserve behavior, sound-material, movement, navigation, and leg-placement factory/apply/registry anchors.
- The selected fixture preserves explicit factory-only boundaries for `importance` and `navMap`.
- The selected fixture preserves the raw-preserved compound boundary for `use` without publishing raw strings or raw bytes.
- The large unselected observed Unit value-ID set remains explicit boundary debt instead of receiving invented meanings.
- All nine selected PhysicsScript fixture families now have a static child fixture path prepared for a completion rollup.
- The next static child lane is `PhysicsScript Fixture Family Completion Rollup Proof Plan`.

## What This Does Not Prove

This does not prove runtime PhysicsScript behavior, runtime Unit behavior, runtime Unit AI behavior, runtime Unit movement behavior, runtime Unit sound-material behavior, runtime Unit navigation behavior, runtime Unit leg-placement behavior, serialized PhysicsScript completeness, exact PhysicsScript layouts, exact Unit record layout, complete value-ID semantics, raw string identity, raw numeric value meaning, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
