# PhysicsScript Semantic Value-Field Schema Ledger Proof Plan

Status: complete static semantic value-field schema ledger, not runtime proof
Last updated: 2026-06-10
Scope: `physics-script-semantic-value-field-schema-ledger-proof-plan`

Ledger token: ledgerStatus=physics-script-semantic-value-field-schema-ledger-complete-static-semantic-ledger-not-runtime-proof; runtimeExecution=false; godotWork=false; ghidraMutation=false; rebuildImplementation=false.

This proof records a public-safe static semantic ledger for the copied PhysicsScript corpus. It bridges the shallow copied-corpus parser counts to saved Ghidra loader/factory/apply evidence, without decoding raw payload contents into complete structs and without claiming runtime behavior.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |

This proof does not change the static percentages or create a new Ghidra wave. It performs no Ghidra mutation, no BEA launch, no executable patching, no runtime observation, no Godot work, and no rebuild implementation.

## Corpus Envelope

The ledger is backed by [PhysicsScript Copied-Corpus Parser Proof](physics-script-copied-corpus-parser-proof.md), [PhysicsScript Static Contract](physics-script-static-contract.md), and [CPhysicsScriptStatements.cpp](functions/CPhysicsScriptStatements.cpp.md).

| Metric | Result |
| --- | --- |
| Parsed copied corpus files | `1` |
| Parsed copied filename | `data/default physics.dat` |
| Parsed byte count | `175603` |
| Stream header | `0x12` |
| Top-level statements | `777` |
| Top-level type counts `1..9` | `160 / 139 / 145 / 91 / 38 / 118 / 39 / 43 / 4` |
| Unknown top-level ids | `0` |
| Value-list nodes | `6803` |
| Unique statement/value id pairs | `185` |
| Raw value payload bytes preserved | `73796` |
| Continuation markers | `6026` zero/continue markers and `777` terminating `-1` markers |

The saved loader shape remains the authority: `CPhysicsScript__Load` reads stream header `0x12`, loops top-level statement type ids until `-1`, creates statements through `CPhysicsScript__CreateStatement`, invokes load slot `+0xc`, and skips unknown payload bytes when creation returns null.

## Statement Family Ledger

| Type | Family | Nested factory | Top-level records | Value nodes | Unique value ids | Raw payload bytes | Declared payload bytes |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `1` | Unit | `CPhysicsScriptStatements__CreateStatementType2` | `160` | `2338` | `54` | `28840` | `50284` |
| `2` | Weapon | `CPhysicsScriptStatements__CreateStatementType3` | `139` | `286` | `14` | `4082` | `8894` |
| `3` | WeaponMode | `CPhysicsScriptStatements__CreateStatementType4` | `145` | `1934` | `32` | `15007` | `33261` |
| `4` | Round | `CPhysicsScriptStatements__CreateStatementType5` | `91` | `782` | `33` | `5431` | `16167` |
| `5` | Spawner | `CPhysicsScriptStatements__CreateStatementType6` | `38` | `244` | `10` | `1441` | `5279` |
| `6` | Explosion | `CPhysicsScriptStatements__CreateStatementType7` | `118` | `869` | `14` | `14616` | `27335` |
| `7` | Component | `CPhysicsScriptStatements__CreateStatementType10` | `39` | `225` | `20` | `2921` | `6337` |
| `8` | Feature | `CPhysicsScriptStatements__CreateStatementType8` | `43` | `113` | `5` | `1375` | `3319` |
| `9` | Hazard | `CPhysicsScriptStatements__CreateStatementType9` | `4` | `12` | `3` | `83` | `273` |

## Semantic Buckets

The ledger records semantic buckets, not complete struct layouts. A bucket is promoted only where the static Ghidra function names/comments/decompile evidence prove width, ownership, or apply behavior well enough for clean-room planning.

| Bucket | Static evidence | Rebuild-facing meaning | Boundary |
| --- | --- | --- | --- |
| `scalar4` | `CPhysicsScriptValue__LoadScalarAt08FromMemBuffer`, `CPhysicsScriptValue__GetScalarSerializedSize4` | Four-byte scalar payload loaded into value object field `this+0x8`. | Scalar type and runtime units remain unproven unless a specific apply row names the field. |
| `rounded_scalar4` | `CUnitSoundMaterial__ApplyToUnitData`, `CUnitMaxLegsLifted__ApplyToUnitData`, `CWeaponVolleySize__ApplyToWeaponModeByName`, `CRoundGridOfFear__ApplyToRoundByName` | Four-byte scalar rounded before writing selected integer-like record fields. | Rounding behavior is static apply evidence only, not runtime balance proof. |
| `owned_string_at_08` | `CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer`, `CPhysicsScriptValue__GetOwnedStringAt08SerializedSize` | Owned string payload stored at value object field `this+0x8`, used by weapon icon/effect/sound, round mesh/effect/explosion, hazard, and component resource strings. | Raw strings are not published; exact string lifetime and allocator details remain separate. |
| `two_scalar4` | `CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer` | Two four-byte scalar fields at `this+0x8` and `this+0xc`. | Exact field names remain helper-specific unless apply evidence proves them. |
| `three_scalar4` | `CWeaponLaunchAngle__LoadFromMemBuffer` | Three four-byte fields at `this+0x8`, `this+0xc`, and `this+0x10`. | Launch-angle runtime interpretation remains unproven. |
| `nested_enum_child` | `CPhysicsScriptStatements__CreateStatementType11` through `CreateStatementType15` plus nested apply rows | Nested value-list children for seek, behaviour, alligence, navmap, and state-style subfamilies. | Complete nested enum semantics are not claimed. |
| `flag_from_scalar_nonzero` | Feature/component flag apply rows and component zero-constant path `0x005d856c` | Scalar payload is compared with zero and written as a boolean-style record field. | Runtime meaning of each flag remains helper-specific static evidence. |
| `based_on_copy` | `CWeaponBasedOn__ApplyToWeaponByName`, `CSpawnerBasedOn__ApplyToSpawnerByName`, `CExplosionBasedOn__ApplyToExplosionByName`, component based-on rows | Name-resolved base/default record copy into the target record. | Source record identity and runtime inheritance behavior remain static-only. |
| `registry_by_name_apply` | `DAT_008553e8`, `DAT_008553ec`, `DAT_008553f0`, `DAT_008553f4`, `DAT_008553f8`, `DAT_00855400`, `DAT_00855404`, `DAT_00855408`, `DAT_008553fc` | By-name list lookup for weapon, weapon-mode, round, spawner, explosion, component, feature, hazard, and UnitAI/default records. | Exact list container layout and runtime lookup failure behavior remain separate proof. |
| `indexed_scalar` | `CComponentIndexedScalar164__ApplyToComponentByName` | Writes a scalar through component record field `+0x164` using index from `this+0xc`. | The indexed array shape and bounds behavior are not fully proven. |

## Value Coverage

The public schema [physics-script-semantic-value-field-schema-ledger.v1.json](physics-script-semantic-value-field-schema-ledger.v1.json) records the full value-id count map by family from the copied-corpus parser. The markdown keeps only the family-level summary to avoid turning raw payload counts into a false complete semantic enum.

## What This Proves

- The copied PhysicsScript corpus has a static family/value-id coverage ledger tied to saved Ghidra evidence.
- All nine top-level statement families are represented in the ledger.
- The public schema carries the value-id count map by family without publishing raw payload bytes, raw strings, raw hashes, absolute paths, private artifacts, or runtime observations.
- Ten high-confidence semantic buckets are recorded as rebuild-facing static vocabulary.

## Not Claimed

This does not prove runtime PhysicsScript behavior, runtime physics outcomes, serialized PhysicsScript file-format completeness, exact statement/value-list/concrete record layouts, complete nested enum semantics, exact source-body identity, mission/resource-script outcomes, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.

## Next Slice

Selected next static child lane: PhysicsScript Scalar/String Value Decoder Fixture Proof Plan.

The next slice should remain static-only and public-safe. It can build deterministic scalar/string decoder fixtures for copied-corpus payload widths and preservation, while keeping runtime behavior and complete semantic enum claims deferred.
