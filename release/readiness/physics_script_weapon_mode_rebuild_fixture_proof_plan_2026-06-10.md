# PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan Readiness Note

Status: complete static weapon-mode value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-weapon-mode-rebuild-fixture-proof-plan`

This slice materializes the static Weapon-Mode value-interface fixture selected after the Round fixture. It adds [physics-script-weapon-mode-rebuild-fixture-proof-plan.md](../../reverse-engineering/binary-analysis/physics-script-weapon-mode-rebuild-fixture-proof-plan.md), [physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json](../../reverse-engineering/binary-analysis/physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json), generator `tools/physics_script_weapon_mode_rebuild_fixture_proof_plan.py`, and focused probe `tools/physics_script_weapon_mode_rebuild_fixture_proof_plan_probe.py`.

Representative tokens:

- `fixtureStatus=physics-script-weapon-mode-rebuild-fixture-proof-plan-complete-static-weapon-mode-value-interface-fixture-not-runtime-proof`
- `selectedFixtureFamily=weapon-mode`
- `selectedFixturePath=weapon-mode-selected-value-id-interface-static-fixture`
- `selectedNextSlice=PhysicsScript Unit Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-unit-rebuild-fixture-proof-plan`
- `selectedValueInterfaceRowCount=9`
- `selectedValueIds=2/6/15/18/24/28/31/34/36`
- `factoryOnlyValueIds=15/36`
- `unselectedObservedValueIds=1/3/4/5/8/9/10/11/12/13/14/16/17/19/20/21/22/23/26/27/29/30/32/33/35`
- `selectedMixedPayloadShapeValueIds=2/24`

Static evidence:

- Weapon-Mode statement type id: `3`.
- Weapon-Mode value factory id: `4`.
- Weapon-Mode registry global: `DAT_008553ec`.
- Weapon-Mode loader anchors: `CWeaponModeStatement__LoadFromMemBuffer` and `CPhysicsWeaponModeValueList__LoadFromMemBuffer`.
- Weapon-Mode create/register bridge: `CWeaponModeStatement__CreateWeaponModeAndRecurse`.
- Selected field anchors: `CWeaponRound__ApplyToWeaponModeByName`, `CWeaponMuzzleEffect__ApplyToWeaponModeByName`, `CWeaponClip__ApplyToWeaponModeByName`, `CWeaponPreFireEffect__ApplyToWeaponModeByName`, `CWeaponLaunchSound__ApplyToWeaponModeByName`, `CWeaponVolleySize__ApplyToWeaponModeByName`, `CWeaponLaunchAngle__LoadFromMemBuffer`, `CWeaponPreFireSound__ApplyToWeaponModeByName`, and `CWeaponPostFireSound__ApplyToWeaponModeByName`.

Accounting:

- Static Ghidra function-quality closure remains `6411/6411 = 100.00%`.
- Static debt remains `0 / 0 / 0`.
- Active current-risk re-audit remains `1179/1179 = 100.00%`.
- The copied Weapon-Mode corpus has `145` top-level records, `1934` value nodes, `15007` raw payload bytes preserved internally, and `33261` declared payload bytes.
- Selected payload-shape counts: `scalar4_roundtrip=43`, `owned_string_ascii_nul_shape_roundtrip=334`, `two_scalar4_roundtrip=9`, and `three_scalar4_roundtrip=76`.
- Factory-only selected value ids are preserved as explicit boundary debt: `factoryOnlyValueIds=15/36`.
- Unselected observed Weapon-Mode value ids are preserved as boundary debt with `unselectedObservedScalar4PayloadCount=1247` and `unselectedObservedTwoScalarPayloadCount=225`.

What this proves:

- The selected static Weapon-Mode value-ID interface is materialized as a public-safe rebuild fixture.
- Selected Weapon-Mode rows have bounded static factory/apply/registry anchors and payload-shape evidence.
- Runtime/Godot/Ghidra/patch/product/rebuild guards remain false.
- `runtimeExecution=false`
- `godotWork=false`
- `ghidraMutation=false`
- `rebuildImplementation=false`

What remains unproven:

- Runtime PhysicsScript behavior.
- Runtime Weapon-Mode firing cadence, round selection, projectile spawn, effect, audio, volley, or launch-angle behavior.
- Runtime projectile outcomes.
- Serialized PhysicsScript completeness.
- Exact PhysicsScript or Weapon-Mode record layouts.
- Complete value-ID semantics.
- Raw string identity or raw numeric value meaning.
- BEA patching behavior.
- Godot parity.
- Rebuild implementation, rebuild parity, or no-noticeable-difference parity.
