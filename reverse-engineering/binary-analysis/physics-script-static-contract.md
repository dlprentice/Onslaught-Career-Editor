# PhysicsScript static contract

Status: bounded static and copied-corpus evidence; not runtime proof
Last updated: 2026-07-16

PhysicsScript defines default records for unit, weapon, weapon-mode, round,
spawner, explosion, component, feature, and hazard families. This page owns the
implementation-facing static map; function-level detail remains in
[`functions/CPhysicsScript.cpp.md`](functions/CPhysicsScript.cpp.md) and
[`functions/CPhysicsScriptStatements.cpp.md`](functions/CPhysicsScriptStatements.cpp.md).

## Manager contract

| Address | Static role |
| --- | --- |
| `0x0042e880 CPhysicsScript__Create` | Allocates and initializes the `0x10`-byte manager and stores the singleton. |
| `0x0042e8f0 CPhysicsScript__Destroy` | Deletes statement nodes, frees the manager, and clears the singleton. |
| `0x0042e950 CPhysicsScript__Load` | Recreates the manager, reads header token `0x12`, creates known statements, invokes their load slot, and skips unknown payloads. |
| `0x0042ea60 CPhysicsScript__Update` | Iterates statements and calls update slot `+0x4`; null-singleton caller behavior is not proven. |
| `0x0042eb90 CPhysicsScript__CreateStatement` | Dispatches observed top-level type ids `1..9`; unknown ids return null. |

The singleton is stored at `0x0066e99c`.

## Statement families

| Type | Family | Vtable |
| ---: | --- | --- |
| 1 | `CUnitStatement` | `0x005d9878` |
| 2 | `CWeaponStatement` | `0x005d9850` |
| 3 | `CWeaponModeStatement` | `0x005d9864` |
| 4 | `CRoundStatement` | `0x005d983c` |
| 5 | `CSpawnerStatement` | `0x005d9828` |
| 6 | `CExplosionStatement` | `0x005d9814` |
| 7 | `CComponentStatement` | `0x005d9800` |
| 8 | `CFeatureStatement` | `0x005d97ec` |
| 9 | `CHazardStatement` | `0x005d97d8` |

Each observed top-level object is allocated as `0x110` bytes and initializes
the common type, flags, and child/list fields. That allocation size is evidence
for this specimen, not a complete class layout.

## Load and recurse shape

Each family has a vtable-backed statement loader paired with a value-list
loader. The statement loaders read names and list payloads from
`CDXMemBuffer`; value-list allocations use `CDXMemoryManager__Alloc`; unknown
payloads are skipped through `CFlexArray__SkipBytesFromMemBuffer`.

Create/recurse methods register a named default record and then invoke child
statements. Relevant registry lists include:

| Global | Static role |
| --- | --- |
| `DAT_008553f4` | Spawner defaults |
| `DAT_008553f8` | Explosion defaults |
| `DAT_008553fc` | UnitAI records |
| `DAT_00855400` | Component defaults |
| `DAT_00855404` | Feature defaults |
| `DAT_00855408` | Hazard defaults |

Key apply anchors are `CSpawnerBasedOn__ApplyToSpawnerByName` at `0x00439e70`,
`CSpawnerUnit__ApplyToSpawnerByName` at `0x0043a080`, and
`CExplosionBasedOn__ApplyToExplosionByName` at `0x0043abd0`.

## Retained evidence

- [`physics-script-copied-corpus-parser-proof.md`](physics-script-copied-corpus-parser-proof.md)
  records a public-safe aggregate parse of a copied `default physics.dat`.

Generated proof-plan crosswalks and rollups are not independent authorities;
the function notes and this contract retain the supported facts directly.

## Claim boundary

This contract proves a coherent static manager/factory/load/apply map and a
bounded copied-corpus framing result. It does not prove runtime PhysicsScript
behavior, complete serialization semantics, exact statement/value/concrete
record layouts, source-body identity, gameplay outcomes, patch behavior, or
rebuild parity.
