# Ghidra Physics Value Base Destructor Review Wave986 (2026-05-31)

Status: read-only static review
Date: 2026-05-31
Branch: `main`
Tag: `physics-value-base-dtor-review-wave986`

## Scope

Wave986 re-reviewed seven PhysicsScript value-family base destructor bodies after Wave985's registry/apply bridge review.

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00432cc0` | `CPhysicsUnitValue__dtor_base` | Reviewed; no mutation |
| `0x004347a0` | `CPhysicsWeaponValue__dtor_base` | Reviewed; no mutation |
| `0x0043a040` | `CPhysicsSpawnerValue__dtor_base` | Reviewed; no mutation |
| `0x0043af80` | `CPhysicsExplosionValue__dtor_base` | Reviewed; no mutation |
| `0x0043be00` | `CPhysicsFeatureValue__dtor_base` | Reviewed; no mutation |
| `0x0043c310` | `CPhysicsHazardValue__dtor_base` | Reviewed; no mutation |
| `0x0043dcc0` | `CPhysicsComponentValue__dtor_base` | Reviewed; no mutation |

Exact probe anchors: `0x00432cc0 CPhysicsUnitValue__dtor_base`, `0x004347a0 CPhysicsWeaponValue__dtor_base`, `0x0043a040 CPhysicsSpawnerValue__dtor_base`, `0x0043af80 CPhysicsExplosionValue__dtor_base`, `0x0043be00 CPhysicsFeatureValue__dtor_base`, `0x0043c310 CPhysicsHazardValue__dtor_base`, and `0x0043dcc0 CPhysicsComponentValue__dtor_base`.

No Ghidra mutation was performed. The pass made no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, and did not launch BEA.

## Evidence

Fresh read-only artifacts are under the ignored private evidence root:

```text
subagents/ghidra-static-reaudit/wave986-physics-value-base-dtor-review/
```

Read-back result:

```text
metadata: 7/7 OK
tags: 7/7 OK
xrefs: 10 rows
instructions: 14 rows
decompile: 7/7 OK
queue: 6222/6222, 0 commentless, 0 undefined signatures, 0 param_N
```

Normalized progress tokens:

```text
static closure: 6222/6222 = 100.00%
Wave911 focused re-audit progress: 406/1408 = 28.84%
expanded static surface progress: 466/1478 = 31.53%
```

## Review Result

Fresh Ghidra evidence confirms the current saved names and signatures are coherent:

- Each target body is a two-instruction base destructor shape: `MOV dword ptr [ECX], <base-vtable>` followed by `RET`.
- `CPhysicsUnitValue__dtor_base` restores vtable `0x005d9e54` and is reached from three unwind cleanup callbacks plus `CPhysicsUnitValue__scalar_deleting_dtor`.
- `CPhysicsWeaponValue__dtor_base` restores vtable `0x005d9f80` and is reached from `CPhysicsWeaponValue__scalar_deleting_dtor`.
- `CPhysicsSpawnerValue__dtor_base`, `CPhysicsExplosionValue__dtor_base`, `CPhysicsFeatureValue__dtor_base`, `CPhysicsHazardValue__dtor_base`, and `CPhysicsComponentValue__dtor_base` restore vtables `0x005da6b0`, `0x005da7f0`, `0x005da890`, `0x005da8f4`, and `0x005daae8` respectively, and are reached from their shared leaf scalar-deleting destructor wrappers.
- The current saved comments and tags already describe base destructor/vtable-restore evidence without overclaiming exact class layouts or runtime behavior.

This review keeps Wave986 narrow. Weapon-mode value load/destructor rows and round value owned-string/apply/destructor rows remain separate candidates rather than being mixed into this base-destructor tranche.

## Backup

Verified post-wave backup:

```text
G:\GhidraBackups\BEA_20260531-015646_post_wave986_physics_value_base_dtor_review_verified
files=19
bytes=173837191
MissingCount=0
ExtraCount=0
DiffCount=0
HashDiffCount=0
```

## Truth Boundary

This review proves static Ghidra coherence for the seven selected PhysicsScript `*Value__dtor_base` bodies only. It does not prove exact PhysicsScript class layouts, exact source-body identity, runtime physics-script load/apply/lifetime behavior, MSL asset behavior, BEA patch behavior, or rebuild parity.
