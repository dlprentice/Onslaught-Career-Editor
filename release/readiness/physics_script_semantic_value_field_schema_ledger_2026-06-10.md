# PhysicsScript Semantic Value-Field Schema Ledger Readiness Note

Status: complete static semantic value-field schema ledger, not runtime proof
Date: 2026-06-10
Scope: `physics-script-semantic-value-field-schema-ledger-proof-plan`

Full slice title: PhysicsScript Semantic Value-Field Schema Ledger Proof Plan.
Ledger token: ledgerStatus=physics-script-semantic-value-field-schema-ledger-complete-static-semantic-ledger-not-runtime-proof; runtimeExecution=false; godotWork=false; ghidraMutation=false; rebuildImplementation=false.

This slice converts the copied PhysicsScript parser proof and saved Ghidra contract into a public-safe semantic value-field ledger for rebuild planning.

Evidence anchors:

- Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt.
- Active current-risk re-audit remains `1179/1179 = 100.00%`; remaining active focused work remains `0`.
- Copied corpus parser evidence: `1` copied `data/default physics.dat`, `175603` bytes, stream header `0x12`, `777` top-level statements, `6803` value-list nodes, `185` unique statement/value id pairs, `73796` raw value payload bytes preserved, `0` unknown top-level ids.
- Family coverage rows: Unit `160/2338/54`, Weapon `139/286/14`, WeaponMode `145/1934/32`, Round `91/782/33`, Spawner `38/244/10`, Explosion `118/869/14`, Component `39/225/20`, Feature `43/113/5`, Hazard `4/12/3`.
- Semantic bucket count: `10`.
- Semantic buckets: `scalar4`, `rounded_scalar4`, `owned_string_at_08`, `two_scalar4`, `three_scalar4`, `nested_enum_child`, `flag_from_scalar_nonzero`, `based_on_copy`, `registry_by_name_apply`, and `indexed_scalar`.
- Static anchors include `CPhysicsScript__Load`, `CPhysicsScript__CreateStatement`, `CPhysicsScriptStatements__CreateStatementType2`, `CPhysicsScriptStatements__CreateStatementType10`, `CPhysicsScriptValue__LoadScalarAt08FromMemBuffer`, `CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer`, `CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer`, `CWeaponLaunchAngle__LoadFromMemBuffer`, `CComponentIndexedScalar164__ApplyToComponentByName`, `DAT_008553e8`, `DAT_008553ec`, `DAT_008553f0`, `DAT_008553f4`, `DAT_008553f8`, `DAT_00855400`, `DAT_00855404`, `DAT_00855408`, and `DAT_008553fc`.
- Public schema: `reverse-engineering/binary-analysis/physics-script-semantic-value-field-schema-ledger.v1.json`.
- Focused probe: `tools/physics_script_semantic_value_field_schema_ledger_probe.py`.
- Selected next static child lane: PhysicsScript Scalar/String Value Decoder Fixture Proof Plan.

What this proves:

- A static, public-safe PhysicsScript semantic value-field ledger exists for all nine top-level copied-corpus families.
- High-confidence loader/apply semantics are bucketed for rebuild planning without publishing raw payloads, raw strings, raw hashes, absolute private paths, or runtime observations.

What remains unproven:

- Runtime PhysicsScript behavior.
- Runtime physics outcomes.
- Serialized PhysicsScript file-format completeness.
- Exact statement/value-list/concrete record layouts.
- Complete nested enum semantics.
- Exact source-body identity.
- Mission/resource-script outcomes.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

No Ghidra mutation, executable patching, BEA launch, screenshot capture, private-frame review, Godot work, product UI wiring, or rebuild implementation occurred in this slice.
