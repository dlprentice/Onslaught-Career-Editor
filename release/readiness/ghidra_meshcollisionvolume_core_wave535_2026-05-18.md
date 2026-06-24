# Ghidra MeshCollisionVolume Core Wave535 Readiness

Date: 2026-05-18
Scope: Static Ghidra signature/comment/tag hardening for five adjacent MeshCollisionVolume core collision helpers.

## Targets

| Address | Saved state |
| --- | --- |
| `0x004abe50` | `int __thiscall CMeshCollisionVolume__VFunc_02_004abe50(void * this, void * query_arg0, void * query_arg1, void * source_sphere_record, void * contact_record)` |
| `0x004ac000` | `void __cdecl CMeshCollisionVolume__InitDirectionLookupTable(void)` |
| `0x004ac140` | `int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstBounds(void * part_context, void * bounds_record, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)` |
| `0x004ac4a0` | `int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstMeshPart(void * part_context, void * mesh_part, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)` |
| `0x004acf30` | `int __stdcall CMeshCollisionVolume__ResolveContactNormalAndPlane(float * contact_record, float hit_x, float hit_y, float hit_z, float hit_w, float normal_x, float normal_y, float normal_z, float normal_w, float unused_source_w, float * out_contact_point, float * out_contact_normal)` |

## Evidence

- Read-only pre-export covered metadata, tags, xrefs, full entry-neighborhood instructions, and decompiles under `subagents/ghidra-static-reaudit/wave535-meshcollisionvolume-core-004abe50/`.
- `ApplyMeshCollisionVolumeCoreWave535.java` dry-run: `updated=0 skipped=5 missing=0 bad=0`.
- Apply: `updated=5 skipped=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final verify dry-run: `updated=0 skipped=5 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post read-back verified `5` metadata rows, `5` tag rows, `5` target xref rows, `4605` instruction rows, and `5` target decompile exports.
- Focused probe passed: `py -3 tools\ghidra_meshcollisionvolume_core_wave535_probe.py --check`.
- NPM wrapper passed: `cmd.exe /c npm run test:ghidra-meshcollisionvolume-core-wave535`.
- Static re-audit queue passed: `cmd.exe /c npm run test:ghidra-static-reaudit-queue`.

## Queue Snapshot

- Total functions: `6083`
- Commented functions: `2603`
- Commentless functions: `3480`
- Exact-undefined signatures: `1550`
- `param_N` signatures: `1316`
- Comment-backed proxy: `2603/6083 = 42.79%`
- Strict comment-plus-clean-signature proxy: `2546/6083 = 41.85%`

These percentages are telemetry only, not completion or correctness certification.

## Backup

Verified saved-project backup:

```text
G:\GhidraBackups\BEA_20260518-062025_post_wave535_meshcollisionvolume_core_verified
```

Backup verification: `19` files, `159189895` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Not Proven

Wave535 is static retail Ghidra metadata evidence only. It does not prove runtime collision behavior, concrete mesh/contact/AABB layouts, exact source-body identity, BEA launch behavior, executable patching, or rebuild parity. The existing `0x004acde0` contact-output tail remains intentionally signature-deferred because its observed convention depends on register state rather than a clean callable boundary.
