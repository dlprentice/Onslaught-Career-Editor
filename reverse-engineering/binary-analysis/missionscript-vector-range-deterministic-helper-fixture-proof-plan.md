# MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan

Status: complete pure helper fixture proof plan, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-vector-range-deterministic-helper-fixture`

This proof completes the vector/range helper child lane selected by the [Static-To-Proof Next Safe Slice Selection Refresh Proof Plan](static-to-proof-next-safe-slice-selection-refresh.md). It turns the completed static vector/range evidence into a clean-room deterministic finite-helper fixture matrix without launching BEA, observing runtime MissionScript execution, reading private baselines, writing copied files, mutating Ghidra, patching an executable, starting Godot work, or implementing a rebuild.

Machine-checkable artifact:

- [missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json](missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json)

Proof tokens:

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

Guard tokens:

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

## Static Authority

| Surface | Evidence |
| --- | --- |
| Selected lane | The selection refresh chose this lane after the Save / Options Byte-Preservation AppCore Fixture Matrix Proof completed. |
| Handler anchors | `0x005345d0 IScript__GetVectorLength`, `0x005347b0 IScript__CheckValueInRange`, `0x00534b80 IScript__GetVectorX`, `0x00534c10 IScript__GetVectorY`, and `0x00534ca0 IScript__GetVectorZ`. |
| Descriptor context | Rows `0x0064dc50`, `0x0064dc90`, `0x0064dcd0`, `0x0064dd10`, `0x0064dd50`, `0x0064dd90`, `0x0064e850`, `0x0064e890`, and `0x0064e950` stay raw descriptor context only. |
| Datatype context | vector getter slot `+0x44`, float getter slot `+0x34`, component offsets `+0/+4/+8`, float result vtable `0x005e4ea4`, and bool result vtable context `0x005e4d50`. |
| Loose corpus context | `directNonCommentLooseMslRows=0`; this is helper/VM planning, not selected script usage. |

Descriptor rows remain raw static context because the observed row names and raw entries do not justify exact descriptor layout, exact command arity, exact argument type schema, or selected mission usage.

## Fixture Matrix

The fixture matrix is finite-only and recomputed by the focused probe:

- Vector length: `sqrt(x*x+y*y+z*z)`.
- Component extraction: offsets `+0`, `+4`, and `+8`.
- Range check: `(boundA <= value <= boundB) or (boundB <= value <= boundA)`.

Vector inputs:

| Vector | Length |
| --- | ---: |
| `(0, 0, 0)` | `0` |
| `(3, 4, 0)` | `5` |
| `(2, 3, 6)` | `7` |
| `(-3, -4, -12)` | `13` |

Each vector also has X, Y, and Z component assertions, for `plannedVectorAssertionCount=16`.

Range cases cover ascending bounds, descending bounds, equal bounds, inclusive endpoints, inside values, and outside values, for `plannedRangeCaseCount=12`.

Excluded numeric and ABI surfaces remain deferred: `NaN`, `infinity`, `signed zero`, `subnormal`, `overflow`, allocator failure behavior, exact x87/CRT rounding parity, exact result-object layout, exact helper ABI, and exact source identity.

## Claim Boundary

This proves pure deterministic vector length plus component helper math for four finite vectors, pure deterministic inclusive order-insensitive range helper behavior for twelve finite cases, and consolidated source anchors for the vector/range helper fixture.

It does not prove runtime MissionScript execution, runtime command effects, runtime vector/range behavior, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact command arity, exact argument type schema, exact datatype layout, exact vector layout, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
