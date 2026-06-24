# PhysicsScript Round Rebuild Fixture Proof Plan Readiness Note

Status: complete static round value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-round-rebuild-fixture-proof-plan`

This slice materializes the static Round value-interface fixture selected after the Weapon fixture. It adds [physics-script-round-rebuild-fixture-proof-plan.md](../../reverse-engineering/binary-analysis/physics-script-round-rebuild-fixture-proof-plan.md), [physics-script-round-rebuild-fixture-proof-plan.v1.json](../../reverse-engineering/binary-analysis/physics-script-round-rebuild-fixture-proof-plan.v1.json), generator `tools/physics_script_round_rebuild_fixture_proof_plan.py`, and focused probe `tools/physics_script_round_rebuild_fixture_proof_plan_probe.py`.

Representative tokens:

- `fixtureStatus=physics-script-round-rebuild-fixture-proof-plan-complete-static-round-value-interface-fixture-not-runtime-proof`
- `selectedFixtureFamily=round`
- `selectedFixturePath=round-selected-value-id-interface-static-fixture`
- `selectedNextSlice=PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-weapon-mode-rebuild-fixture-proof-plan`
- `selectedValueInterfaceRowCount=7`
- `selectedValueIds=4/8/9/24/33/35/36`
- `unselectedObservedValueIds=1/2/3/5/6/10/11/12/13/14/15/16/17/18/19/22/23/26/27/28/29/30/31/32/37/38`
- `selectedMixedPayloadShapeValueIds=8/9`

Static evidence:

- Round statement type id: `4`.
- Round value factory id: `5`.
- Round registry global: `DAT_008553f0`.
- Round loader anchors: `CRoundStatement__LoadFromMemBuffer` and `CPhysicsRoundValueList__LoadFromMemBuffer`.
- Round create/register bridge: `CRoundStatement__CreateRoundAndRecurse`.
- Selected field anchors: `CRoundSeek__ApplyToRoundByName`, `CRoundEffect__ApplyToRoundByName`, `CRoundExplosion__ApplyToRoundByName`, `CRoundGridOfFear__ApplyToRoundByName`, `CRoundWaterEffect__ApplyToRoundByName`, `CRoundTreeCollision__ApplyToRoundByName`, and `CRoundMesh__ApplyToRoundByName`.

Accounting:

- Static Ghidra function-quality closure remains `6411/6411 = 100.00%`.
- Static debt remains `0 / 0 / 0`.
- Active current-risk re-audit remains `1179/1179 = 100.00%`.
- The copied Round corpus has `91` top-level records, `782` value nodes, `5431` raw payload bytes preserved internally, and `16167` declared payload bytes.
- Selected payload-shape counts: `scalar4_roundtrip=84`, `owned_string_ascii_nul_shape_roundtrip=161`, `two_scalar4_roundtrip=3`, and `three_scalar4_roundtrip=10`.
- Unselected observed Round value ids are preserved as boundary debt with `unselectedObservedScalar4PayloadCount=500` and `unselectedObservedRawPreservedOtherPayloadCount=24`.

What this proves:

- The selected static Round value-ID interface is materialized as a public-safe rebuild fixture.
- Selected Round rows have bounded static factory/apply/registry anchors and payload-shape evidence.
- Runtime/Godot/Ghidra/patch/product/rebuild guards remain false.
- `runtimeExecution=false`
- `godotWork=false`
- `ghidraMutation=false`
- `rebuildImplementation=false`

What remains unproven:

- Runtime PhysicsScript behavior.
- Runtime Round/projectile launch, seeking, movement, collision, effect, explosion, mesh, damage, or outcome behavior.
- Serialized PhysicsScript completeness.
- Exact PhysicsScript or Round record layouts.
- Complete value-ID semantics.
- Raw string identity or raw numeric value meaning.
- BEA patching behavior.
- Godot parity.
- Rebuild implementation, rebuild parity, or no-noticeable-difference parity.
