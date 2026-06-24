# PhysicsScript Value-ID Semantic Crosswalk Readiness Note

Status: complete bounded static value-id crosswalk, not runtime proof
Date: 2026-06-10
Scope: `physics-script-value-id-semantic-crosswalk-proof-plan`

Crosswalk token: crosswalkStatus=physics-script-value-id-semantic-crosswalk-complete-bounded-static-crosswalk-not-runtime-proof; runtimeExecution=false; godotWork=false; ghidraMutation=false; rebuildImplementation=false; rawCopiedStringsEmitted=false; rawNumericValuesEmitted=false; completeValueIdSemanticsProven=false; all185PairsSemanticallyNamed=false.

This slice adds a generated public-safe PhysicsScript value-id crosswalk schema, proof note, focused probe, front-door documentation, and mirrors. It performs no Ghidra mutation and therefore does not create a new Ghidra backup; the latest verified Ghidra backup remains the Wave1219 static backup recorded in the measurement register.

Canonical proof: PhysicsScript Value-ID Semantic Crosswalk Proof Plan (`physics-script-value-id-semantic-crosswalk-proof-plan.md`), backed by `physics-script-value-id-semantic-crosswalk.v1.json`.

Measured static context:

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |

Crosswalk evidence:

| Metric | Result |
| --- | ---: |
| Copied corpus byte count | `175603` |
| Stream header | `0x12` |
| Top-level PhysicsScript statements | `777` |
| Value-list nodes | `6803` |
| Unique copied statement/value-id pairs | `185` |
| Bounded selected crosswalk rows | `87` |
| Selected rows observed in copied corpus | `72` |
| Selected factory-only rows not observed in copied corpus | `15` |

Representative static anchors: `CPhysicsScriptStatements__CreateStatementType6`, `CPhysicsScriptStatements__CreateStatementType10`, `CSpawnerUnit__ApplyToSpawnerByName`, `CExplosionBasedOn__ApplyToExplosionByName`, `CComponentIndexedScalar164__ApplyToComponentByName`, `CRoundGridOfFear__ApplyToRoundByName`, `CWeaponVolleySize__ApplyToWeaponModeByName`, and `CUnitBehaviour__ApplyToUnitData`.

What this proves:

- The selected rows have bounded static factory/apply/load evidence.
- The copied-corpus value-id accounting remains tied to the prior `185` statement/value-id pair ledger.
- The crosswalk exposes selected rebuild-facing field names while preserving unselected observed ids and factory-only rows separately.

What remains unproven:

- Runtime PhysicsScript behavior.
- Runtime physics outcomes.
- Serialized PhysicsScript completeness.
- Exact concrete record layouts.
- Complete value-id semantics for all observed pairs.
- Complete nested enum semantics.
- Raw string identity or raw numeric value meaning.
- BEA patching behavior.
- Godot parity.
- Rebuild implementation, rebuild parity, or no-noticeable-difference parity.

Selected next static child lane: PhysicsScript Rebuild Interface Rollup Proof Plan.
