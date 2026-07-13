# Ghidra Physics Registry Apply Review Wave985 (2026-05-31)

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x004309e0` → `ExplosionDefinition__CreateAndRegisterByName` (was `CExplosion__CreateAndRegisterByName`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: read-only static review
Date: 2026-05-31
Branch: `main`
Tag: `physics-registry-apply-review-wave985`

## Scope

Wave985 re-reviewed the PhysicsScript statement registry/apply helper bridge after the Wave900-Wave984 recheck gate.

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00430510` | `CSpawnerData__CreateAndRegisterByName` | Reviewed; no mutation |
| `0x004309e0` | `CExplosionStatement__Create` | Reviewed; no mutation |
| `0x00430e60` | `CComponentStatement__CreateAndRegisterByName` | Reviewed; no mutation |
| `0x00431350` | `CFeatureStatement__CreateAndRegisterByName` | Reviewed; no mutation |
| `0x004317a0` | `CHazardStatement__CreateAndRegisterByName` | Reviewed; no mutation |
| `0x00439e70` | `CSpawnerBasedOn__ApplyToSpawnerByName` | Reviewed; no mutation |
| `0x0043a080` | `CSpawnerUnit__ApplyToSpawnerByName` | Reviewed; no mutation |
| `0x0043abd0` | `CExplosionBasedOn__ApplyToExplosionByName` | Reviewed; no mutation |

Exact probe anchors: `0x00430510 CSpawnerData__CreateAndRegisterByName`, `0x004309e0 CExplosionStatement__Create`, `0x00430e60 CComponentStatement__CreateAndRegisterByName`, `0x00431350 CFeatureStatement__CreateAndRegisterByName`, `0x004317a0 CHazardStatement__CreateAndRegisterByName`, `0x00439e70 CSpawnerBasedOn__ApplyToSpawnerByName`, `0x0043a080 CSpawnerUnit__ApplyToSpawnerByName`, and `0x0043abd0 CExplosionBasedOn__ApplyToExplosionByName`.

No Ghidra mutation was performed. The pass made no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, and did not launch BEA.

## Evidence

Fresh read-only artifacts are under the ignored private evidence root:

```text
subagents/ghidra-static-reaudit/wave985-physics-registry-apply-review/
```

Read-back result:

```text
metadata: 8/8 OK
tags: 8/8 OK
xrefs: 8 rows
instructions: 936 rows
decompile: 8/8 OK
queue: 6222/6222, 0 commentless, 0 undefined signatures, 0 param_N
```

Normalized progress tokens:

```text
static closure: 6222/6222 = 100.00%
Wave911 focused re-audit progress: 399/1408 = 28.34%
expanded static surface progress: 459/1478 = 31.06%
```

## Review Result

Fresh Ghidra evidence confirms the current saved names and signatures are coherent:

- The registry creation rows append default records to the global PhysicsScript registries: `DAT_008553f4` for spawners, `DAT_008553f8` for explosions, `DAT_00855400` for components, `DAT_00855404` for features, and `DAT_00855408` for hazards.
- `CSpawnerData__CreateAndRegisterByName`, `CExplosionStatement__Create`, `CComponentStatement__CreateAndRegisterByName`, `CFeatureStatement__CreateAndRegisterByName`, and `CHazardStatement__CreateAndRegisterByName` preserve the prior Wave332/Wave333 registry labels and one-argument `__cdecl` signatures.
- `CComponentStatement__CreateAndRegisterByName` still initializes the component data record with several pointer sets, calls `CUnitAI__InitDefaults`, and applies the `Fenrir Main Gun` / `Fenrir` special-case flag before appending to `DAT_00855400`; this supports the current component-registry comment without changing the owner.
- `CSpawnerBasedOn__ApplyToSpawnerByName` and `CSpawnerUnit__ApplyToSpawnerByName` remain vtable-backed spawner apply helpers via DATA refs `0x005da5c4` and `0x005da6a0`.
- `CExplosionBasedOn__ApplyToExplosionByName` remains the vtable-backed explosion apply helper via DATA ref `0x005da7e0`, copying selected owned string/scalar fields after resolving source and target explosion records through `DAT_008553f8`.

This review keeps Wave985 narrow. Nearby value/destructor rows such as `CPhysicsSpawnerValue__dtor_base`, `CRoundSeek__dtor_base`, and `CPhysicsExplosionValue__dtor_base` remain separate review candidates rather than being mixed into this registry/apply bridge.

## Backup

Verified post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260531-013725_post_wave985_physics_registry_apply_review_verified
files=19
bytes=173837191
MissingCount=0
ExtraCount=0
DiffCount=0
HashDiffCount=0
```

## Truth Boundary

This review proves static Ghidra coherence for the selected PhysicsScript registry/apply helpers only. It does not prove exact record layouts, exact source-body identity, runtime physics-script loading/application behavior, MSL asset behavior, BEA patch behavior, or rebuild parity.
