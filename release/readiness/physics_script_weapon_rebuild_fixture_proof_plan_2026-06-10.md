# PhysicsScript Weapon Rebuild Fixture Proof Plan Readiness Note

Status: complete static weapon value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-weapon-rebuild-fixture-proof-plan`

This slice materializes the static Weapon value-interface fixture selected after the Component fixture. It adds [physics-script-weapon-rebuild-fixture-proof-plan.md](../../reverse-engineering/binary-analysis/physics-script-weapon-rebuild-fixture-proof-plan.md), [physics-script-weapon-rebuild-fixture-proof-plan.v1.json](../../reverse-engineering/binary-analysis/physics-script-weapon-rebuild-fixture-proof-plan.v1.json), generator `tools/physics_script_weapon_rebuild_fixture_proof_plan.py`, and the focused probe `tools/physics_script_weapon_rebuild_fixture_proof_plan_probe.py`.

Representative tokens:

- `fixtureStatus=physics-script-weapon-rebuild-fixture-proof-plan-complete-static-weapon-value-interface-fixture-not-runtime-proof`
- `selectedFixtureFamily=weapon`
- `selectedFixturePath=weapon-selected-value-id-interface-static-fixture`
- `selectedNextSlice=PhysicsScript Round Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-round-rebuild-fixture-proof-plan`
- `selectedValueInterfaceRowCount=4`
- `selectedValueIds=1/4/5/14`
- `unselectedObservedValueIds=2/3/6/7/8/9/10/11/12/13`
- `selectedMixedPayloadShapeValueIds=1`

Static evidence:

- Weapon statement type id: `2`.
- Weapon value factory id: `3`.
- Weapon registry global: `DAT_008553e8`.
- Weapon loader anchors: `CWeaponStatement__LoadFromMemBuffer` and `CPhysicsWeaponValueList__LoadFromMemBuffer`.
- Weapon create/register bridge: `CWeaponStatement__CreateWeaponAndRecurse`.
- Selected field anchors: `CWeaponChargeLevel__LoadFromMemBuffer`, `CWeaponConsumption__ApplyToWeaponByName`, `CWeaponIconName__ApplyToWeaponByName`, and `CWeaponVersusAir__ApplyToWeaponByName`.

Accounting:

- Static Ghidra function-quality closure remains `6411/6411 = 100.00%`.
- Static debt remains `0 / 0 / 0`.
- Active current-risk re-audit remains `1179/1179 = 100.00%`.
- The copied Weapon corpus has `139` top-level records, `286` value nodes, `4082` raw payload bytes preserved internally, and `8894` declared payload bytes.
- Selected payload-shape counts: `raw_preserved_other=141`, `three_scalar4_roundtrip=1`, `scalar4_roundtrip=27`, and `owned_string_ascii_nul_shape_roundtrip=15`.
- Unselected observed Weapon value ids are preserved as boundary debt with `unselectedObservedScalar4PayloadCount=102`.

What this proves:

- The selected static Weapon value-ID interface is materialized as a public-safe rebuild fixture.
- Selected Weapon rows have bounded static factory/apply/registry anchors and payload-shape evidence.
- Runtime/Godot/Ghidra/patch/product/rebuild guards remain false.
- `runtimeExecution=false`
- `godotWork=false`
- `ghidraMutation=false`
- `rebuildImplementation=false`

What remains unproven:

- Runtime PhysicsScript behavior.
- Runtime weapon charge, firing, damage, cadence, audio, or visual behavior.
- Serialized PhysicsScript completeness.
- Exact PhysicsScript or weapon record layouts.
- Complete value-ID semantics.
- Raw string identity or raw numeric value meaning.
- BEA patching behavior.
- Godot parity.
- Rebuild implementation, rebuild parity, or no-noticeable-difference parity.
