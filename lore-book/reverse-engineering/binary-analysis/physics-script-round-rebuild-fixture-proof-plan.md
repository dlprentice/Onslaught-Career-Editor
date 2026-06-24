# PhysicsScript Round Rebuild Fixture Proof Plan

Status: complete static round value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-round-rebuild-fixture-proof-plan`

Tracked schema:

- [physics-script-round-rebuild-fixture-proof-plan.v1.json](physics-script-round-rebuild-fixture-proof-plan.v1.json)

Selection tokens:

- `fixtureStatus=physics-script-round-rebuild-fixture-proof-plan-complete-static-round-value-interface-fixture-not-runtime-proof`
- `previousSlice=PhysicsScript Weapon Rebuild Fixture Proof Plan`
- `selectedNextSlice=PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-weapon-mode-rebuild-fixture-proof-plan`
- `selectedFixtureFamily=round`
- `selectedFixturePath=round-selected-value-id-interface-static-fixture`
- `selectedCandidateRank=7`
- `selectedValueInterfaceRowCount=7`
- `selectedValueIds=4/8/9/24/33/35/36`
- `observedValueIds=1/2/3/4/5/6/8/9/10/11/12/13/14/15/16/17/18/19/22/23/24/26/27/28/29/30/31/32/33/35/36/37/38`
- `unselectedObservedValueIds=1/2/3/5/6/10/11/12/13/14/15/16/17/18/19/22/23/26/27/28/29/30/31/32/37/38`
- `selectedMixedPayloadShapeValueIds=8/9`

Follow-up Weapon-Mode fixture result: [PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan](physics-script-weapon-mode-rebuild-fixture-proof-plan.md), backed by [physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json](physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-weapon-mode-rebuild-fixture-proof-plan-complete-static-weapon-mode-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Unit Rebuild Fixture Proof Plan and selectedNextScope=physics-script-unit-rebuild-fixture-proof-plan while preserving selectedFixtureFamily=weapon-mode, selectedFixturePath=weapon-mode-selected-value-id-interface-static-fixture, selectedValueIds=2/6/15/18/24/28/31/34/36, factoryOnlyValueIds=15/36, unselectedObservedValueIds=1/3/4/5/8/9/10/11/12/13/14/16/17/19/20/21/22/23/26/27/29/30/32/33/35, selectedMixedPayloadShapeValueIds=2/24, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. Static anchors include CWeaponModeStatement__LoadFromMemBuffer, CPhysicsWeaponModeValueList__LoadFromMemBuffer, CWeaponModeStatement__CreateWeaponModeAndRecurse, and DAT_008553ec. Active next static child lane: PhysicsScript Unit Rebuild Fixture Proof Plan.

## Static Context

The loaded Ghidra database remains at `6411/6411 = 100.00%` function-quality closure with `0 / 0 / 0` commentless, exact-undefined, and `param_N` debt. The active current-risk re-audit remains `1179/1179 = 100.00%`.

This slice does not mutate Ghidra, BEA.exe, saves, game files, Godot files, or product UI. The latest verified Ghidra backup remains the Wave1219 static review backup because this is a static proof/materialization slice over already-validated evidence.

Boundary tokens: `runtimeExecution=false`; `godotWork=false`; `ghidraMutation=false`; `rebuildImplementation=false`.

## Fixture Surface

The Round fixture covers only the selected rebuild-facing value interface from the static crosswalk. The copied corpus has `91` Round top-level records, `782` Round value nodes, `5431` raw value payload bytes preserved internally, and `16167` declared payload bytes. Those raw bytes are not published.

| Value ID | Field | Crosswalk class | Corpus status | Public-safe copied-corpus shape evidence |
| ---: | --- | --- | --- | --- |
| `4` | `seekTypeChild` | `nested_enum_child` | observed | `scalar4_roundtrip=17` |
| `8` | `effect` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=85`; `two_scalar4_roundtrip=1`; `three_scalar4_roundtrip=2` |
| `9` | `explosion` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=74`; `two_scalar4_roundtrip=2`; `three_scalar4_roundtrip=8` |
| `24` | `gridOfFear` | `rounded_scalar4` | observed | `scalar4_roundtrip=12` |
| `33` | `waterEffect` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=1` |
| `35` | `treeCollisionStateChild` | `nested_enum_child` | observed | `scalar4_roundtrip=55` |
| `36` | `mesh` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=1` |

There are no factory-only selected Round rows in this fixture.

Value ids `1`, `2`, `3`, `5`, `6`, `10`, `11`, `12`, `13`, `14`, `15`, `16`, `17`, `18`, `19`, `22`, `23`, `26`, `27`, `28`, `29`, `30`, `31`, `32`, `37`, and `38` are not hidden. They are copied-corpus-observed Round rows outside the selected rebuild-facing crosswalk, preserved as `unselectedObservedValueIds=1/2/3/5/6/10/11/12/13/14/15/16/17/18/19/22/23/26/27/28/29/30/31/32/37/38` with `unselectedObservedScalar4PayloadCount=500` and `unselectedObservedRawPreservedOtherPayloadCount=24`.

## Static Anchors

| Anchor | Static role |
| --- | --- |
| `CPhysicsScriptStatements__CreateStatementType5` | Round value factory dispatch. |
| `CRoundStatement__LoadFromMemBuffer` | Round top-level statement loader. |
| `CPhysicsRoundValueList__LoadFromMemBuffer` | Round value-list loader. |
| `CRoundStatement__CreateRoundAndRecurse` | Round create/register bridge and child recursion anchor. |
| `DAT_008553f0` | Round registry global. |
| `CRoundSeek__ApplyToRoundByName` | Selected `seekTypeChild` static apply anchor. |
| `CRoundEffect__ApplyToRoundByName` | Selected `effect` static apply anchor. |
| `CRoundExplosion__ApplyToRoundByName` | Selected `explosion` static apply anchor. |
| `CRoundGridOfFear__ApplyToRoundByName` | Selected `gridOfFear` static apply anchor. |
| `CRoundWaterEffect__ApplyToRoundByName` | Selected `waterEffect` static apply anchor. |
| `CRoundTreeCollision__ApplyToRoundByName` | Selected `treeCollisionStateChild` static apply anchor. |
| `CRoundMesh__ApplyToRoundByName` | Selected `mesh` static apply anchor. |

## Requirement Rows

| Row | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `family-fixture` | satisfied-static-with-unselected-observed-boundary | Round has `33` observed ids, `7` selected rows, zero factory-only selected rows, and `26` unselected observed ids. | Static family-selection proof only. |
| `loader-fixture` | satisfied-static | `CPhysicsScriptStatements__CreateStatementType5`, `CRoundStatement__LoadFromMemBuffer`, `CPhysicsRoundValueList__LoadFromMemBuffer`, `CRoundStatement__CreateRoundAndRecurse`, and `DAT_008553f0`. | Static loader/factory/registry bridge only. |
| `value-interface-fixture` | satisfied-static | Selected value ids `4`, `8`, `9`, `24`, `33`, `35`, and `36` with seven rebuild-facing field names. | Selected value-id interface only, not complete value semantics. |
| `unselected-observed-boundary-fixture` | satisfied-explicit-boundary | `26` copied-corpus-observed Round value ids are intentionally outside this selected rebuild-facing crosswalk. | Observed raw Round payload shapes are preserved as deferred boundary rows instead of receiving invented semantics. |
| `payload-shape-fixture` | satisfied-public-safe | Selected nested enum, owned-string, and rounded-scalar rows with mixed shape boundaries for `effect` and `explosion`. | Public-safe payload shape only; no raw strings or numeric meanings. |
| `projectile-field-fixture` | satisfied-static | `seekTypeChild`, `effect`, `explosion`, `gridOfFear`, `waterEffect`, `treeCollisionStateChild`, and `mesh` are anchored to Round apply helpers and `DAT_008553f0`. | Static Round field boundary only, not runtime projectile behavior or outcome proof. |
| `stop-fixture` | enforced | Runtime/Godot/Ghidra/patch/product/rebuild guards remain false with zero runtime rows. | Defer instead of broadening into runtime projectile launch, movement, collision, effects, damage, or rebuild implementation. |

## What This Proves

- The selected Round value-ID interface is materialized as public-safe static fixture rows.
- The selected Round rows preserve `seekTypeChild`, `effect`, `explosion`, `gridOfFear`, `waterEffect`, `treeCollisionStateChild`, and `mesh` factory/apply/registry anchors.
- The selected fixture preserves mixed payload-shape boundaries for `effect` and `explosion`.
- The large unselected observed Round value-ID set remains explicit boundary debt instead of receiving invented meanings.
- The next static child lane is `PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan`.

## What This Does Not Prove

This does not prove runtime PhysicsScript behavior, runtime round behavior, runtime projectile behavior, runtime projectile outcomes, runtime round seek behavior, runtime round effect behavior, runtime round explosion behavior, runtime round grid-of-fear behavior, runtime round tree-collision behavior, runtime round mesh behavior, serialized PhysicsScript completeness, exact PhysicsScript layouts, exact round record layout, complete value-ID semantics, raw string identity, raw numeric value meaning, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
