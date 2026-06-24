# PhysicsScript Unit Rebuild Fixture Proof Plan Readiness Note

Status: complete static Unit value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-unit-rebuild-fixture-proof-plan`

This slice materializes the static Unit value-interface fixture selected after the Weapon-Mode fixture. It adds [physics-script-unit-rebuild-fixture-proof-plan.md](../../reverse-engineering/binary-analysis/physics-script-unit-rebuild-fixture-proof-plan.md), [physics-script-unit-rebuild-fixture-proof-plan.v1.json](../../reverse-engineering/binary-analysis/physics-script-unit-rebuild-fixture-proof-plan.v1.json), generator `tools/physics_script_unit_rebuild_fixture_proof_plan.py`, and focused probe `tools/physics_script_unit_rebuild_fixture_proof_plan_probe.py`.

Representative tokens:

- `fixtureStatus=physics-script-unit-rebuild-fixture-proof-plan-complete-static-unit-value-interface-fixture-not-runtime-proof`
- `selectedFixtureFamily=unit`
- `selectedFixturePath=unit-selected-value-id-interface-static-fixture`
- `selectedNextSlice=PhysicsScript Fixture Family Completion Rollup Proof Plan`
- `selectedNextScope=physics-script-fixture-family-completion-rollup-proof-plan`
- `selectedValueInterfaceRowCount=8`
- `selectedValueIds=7/8/20/21/22/25/60/61`
- `factoryOnlyValueIds=20/25`
- `unselectedObservedValueIds=1/2/3/5/6/9/10/11/12/13/14/18/23/27/28/29/30/31/32/33/36/38/39/40/41/42/43/44/45/46/47/48/50/51/52/53/54/55/56/57/58/62/63/65/66/67/68/70`
- `selectedMixedPayloadShapeValueIds=none`

Static evidence:

- Unit statement type id: `1`.
- Unit value factory id: `2`.
- Unit registry global: `DAT_008553fc`.
- Unit loader anchors: `CUnitStatement__LoadFromMemBuffer` and `CPhysicsUnitValueList__LoadFromMemBuffer`.
- Unit create/register bridge: `CUnitStatement__CreateUnitAndRecurse`.
- UnitAI registry creation anchor: `CUnitAI__CreateAndRegisterByName`.
- Selected field anchors: `CUnitUse__ApplyToUnitData`, `CUnitBehaviour__ApplyToUnitData`, `CUnitImportance__ApplyToUnitData`, `CUnitSoundMaterial__ApplyToUnitData`, `CUnitStrafeChange__ApplyToUnitData`, `CUnitNavMap__ApplyToUnitData`, `CUnitStandingLegPlacementArea__ApplyToUnitData`, and `CUnitMaxLegsLifted__ApplyToUnitData`.

Accounting:

- Static Ghidra function-quality closure remains `6411/6411 = 100.00%`.
- Static debt remains `0 / 0 / 0`.
- Active current-risk re-audit remains `1179/1179 = 100.00%`.
- The copied Unit corpus has `160` top-level records, `2338` value nodes, `28840` raw payload bytes preserved internally, and `50284` declared payload bytes.
- Selected payload-shape counts: `scalar4_roundtrip=292` and `raw_preserved_other=118`.
- Factory-only selected value ids are preserved as explicit boundary debt: `factoryOnlyValueIds=20/25`.
- Unselected observed Unit value ids are preserved as boundary debt with `unselectedObservedScalar4PayloadCount=912`, `unselectedObservedTwoScalarPayloadCount=123`, `unselectedObservedThreeScalarPayloadCount=31`, `unselectedObservedOwnedStringShapePayloadCount=511`, and `unselectedObservedRawPreservedOtherPayloadCount=351`.

What this proves:

- The selected static Unit value-ID interface is materialized as a public-safe rebuild fixture.
- Selected Unit rows have bounded static factory/apply/registry anchors and payload-shape evidence.
- `importance` and `navMap` remain explicit factory-only boundary rows.
- `use` remains a raw-preserved public-safe shape/count fixture row, not a raw string or runtime behavior claim.
- Runtime/Godot/Ghidra/patch/product/rebuild guards remain false.
- `runtimeExecution=false`
- `godotWork=false`
- `ghidraMutation=false`
- `rebuildImplementation=false`

What remains unproven:

- Runtime PhysicsScript behavior.
- Runtime Unit AI, movement, sound-material, navigation, or leg-placement behavior.
- Serialized PhysicsScript completeness.
- Exact PhysicsScript or Unit record layouts.
- Complete value-ID semantics.
- Raw string identity or raw numeric value meaning.
- BEA patching behavior.
- Godot parity.
- Rebuild implementation, rebuild parity, or no-noticeable-difference parity.
