# MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan Readiness

Status: complete pure helper fixture proof plan, not runtime proof
Date: 2026-06-09
Scope: `missionscript-vector-range-deterministic-helper-fixture`

Artifacts:

- `reverse-engineering/binary-analysis/missionscript-vector-range-deterministic-helper-fixture-proof-plan.md`
- `reverse-engineering/binary-analysis/missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json`
- `tools/missionscript_vector_range_deterministic_helper_fixture_proof_plan_probe.py`

Key tokens:

- `missionScriptVectorRangeDeterministicHelperFixtureProofPlanStatus=missionscript-vector-range-deterministic-helper-fixture-proof-plan-complete-pure-helper-fixture-not-runtime-proof`
- `previousSlice=Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan`
- `selectedNextSlice=MissionScript Goodie State / Save Command-Effect Fixture Proof Plan`
- `selectedFixtureFamily=vector-range-helpers`
- `selectedFixturePath=vector-range-finite-helper-math`
- `sourceProofCount=4`
- `helperFamilyCount=3`
- `descriptorIndices=56/57/58/59/60/61/104/105/108`
- `descriptorRecordCount=9`
- `handlerAnchorCount=5`
- `vectorHandlerCount=5`
- `wave581MetadataRows=5`
- `wave581TagRows=5`
- `wave581XrefRows=5`
- `wave581DecompileRows=5`
- `wave581InstructionRows=3545`
- `wave581VtableRows=24`
- `directNonCommentLooseMslRows=0`
- `plannedVectorInputCount=4`
- `plannedVectorAssertionCount=16`
- `lengthCaseCount=4`
- `componentVectorCount=4`
- `componentCaseCount=12`
- `plannedRangeCaseCount=12`
- `rangeCaseCount=12`
- `plannedHelperAssertionCount=28`
- `deterministicHelperCaseCount=28`
- `finiteOnlyCaseCount=28`
- `nonFiniteFloatCaseCount=0`
- `nonFiniteFloatBehaviorDeferred=true`
- `falseGuardCount=40`
- `zeroCounterCount=30`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`
- `runtimeExecution=false`
- `beLaunch=false`
- `sourceBaselineRead=false`
- `privateArtifactMaterialized=false`
- `copiedFileMutation=false`
- `ghidraMutation=false`
- `godotWork=false`
- `rebuildImplementation=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimeVectorRangeRows=0`
- `beProcessesAfterFixture=0`

Static anchors:

| Surface | Evidence |
| --- | --- |
| Handlers | `0x005345d0 IScript__GetVectorLength`, `0x005347b0 IScript__CheckValueInRange`, `0x00534b80 IScript__GetVectorX`, `0x00534c10 IScript__GetVectorY`, `0x00534ca0 IScript__GetVectorZ`. |
| Datatype context | vector getter slot `+0x44`, float getter slot `+0x34`, component offsets `+0/+4/+8`, `0x005e4ea4`, and `0x005e4d50`. |
| Descriptor context | Raw rows `0x0064dc50` through `0x0064e950`; exact descriptor layout and exact command arity remain deferred. |

Fixture matrix:

- Vector length formula: `sqrt(x*x+y*y+z*z)`.
- Component offsets: `+0`, `+4`, and `+8`.
- Range comparison: `(boundA <= value <= boundB) or (boundB <= value <= boundA)`.
- Finite helper matrix: `plannedVectorAssertionCount=16`, `plannedRangeCaseCount=12`, `plannedHelperAssertionCount=28`.
- Deferred numeric edge surfaces: `NaN`, `infinity`, `signed zero`, `subnormal`, `overflow`, and exact x87/CRT rounding parity.

What this proves:

- Pure deterministic vector length plus component helper math for four finite vectors.
- Pure deterministic inclusive order-insensitive range helper behavior for twelve finite cases.
- Consolidated vector/range helper source anchors without runtime, Ghidra, patch, Godot, product UI, or rebuild claims.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime vector/range behavior.
- Live loose-MSL loading or packed-resource script selection.
- Exact descriptor/datatype/vector layouts, exact helper ABI, allocator failure behavior, exact source identity, rebuild parity, or no-noticeable-difference parity.
