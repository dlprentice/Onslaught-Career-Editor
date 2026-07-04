# Ghidra Static Shadows Wave511 Readiness Note

Date: 2026-05-17

## Summary

Wave511 saved static Ghidra names, signatures, comments, and tags for 13 static-shadows and adjacent render helpers. The tranche includes 4 renames: `CStaticShadows__Initialise`, `CStaticShadows__ShadowMapEntryDestructor`, `CStaticShadows__ShadowMapEntryDeletingDestructor`, and `CPolyBucket__ScalarDeletingDestructor`.

This is static retail Ghidra evidence only. It does not prove exact CStaticShadows, shadow-entry, render-mesh, terrain/heightfield, chunk-resource, CPolyBucket, or render-state layouts. It also does not prove runtime shadow behavior, runtime rebuild behavior, BEA launch behavior, game patching, or rebuild parity.

## Targets

| Address | Saved signature |
| --- | --- |
| `0x004eba30` | `void __stdcall CEngine__SetVertexShaderPathEnabled(int enable_vertex_shader_path)` |
| `0x004ebbc0` | `void __fastcall CStaticShadows__Initialise(void * this)` |
| `0x004ebd10` | `void __fastcall CStaticShadows__ClearAllShadowEntries(void * this)` |
| `0x004ebdf0` | `void __fastcall CStaticShadows__ShadowMapEntryDestructor(void * this)` |
| `0x004ebe40` | `void __fastcall CStaticShadows__UpdateLightVectorAndRebuild(void * this)` |
| `0x004ebfb0` | `void __stdcall CStaticShadows__UpdateVisibility(void * thing, int force_update)` |
| `0x004ec250` | `void * __thiscall CStaticShadows__ShadowMapEntryDeletingDestructor(void * this, byte flags)` |
| `0x004ec2f0` | `void __fastcall CStaticShadows__BuildShadowMaps(void * shadow_entry)` |
| `0x004ee0d0` | `void * __thiscall CPolyBucket__ScalarDeletingDestructor(void * this, byte flags)` |
| `0x004ee0f0` | `void __thiscall CStaticShadows__ApplyShadowsToGrid(void * this, int start_x, int start_y, int width, int height)` |
| `0x004ee410` | `bool __cdecl CStaticShadows__RayTriangleIntersect(float * triangle_a, float * triangle_b, float * triangle_c, float segment_start_x, float segment_start_y, float segment_start_z, int segment_padding_or_w, float segment_end_x, float segment_end_y, float segment_end_z)` |
| `0x004ee8a0` | `void __stdcall CStaticShadows__LoadAll(void * chunk_reader)` |
| `0x004ee8f0` | `void __cdecl CStaticShadows__Load(void * chunk_reader)` |

## Evidence

- `CStaticShadows__Initialise` corrects a stale CGame-owner label. `CGame::Init` calls it with `ECX=0x009c8010`, matching the source-level `STATICSHADOWS.Initialise()` call, and the body registers `BuildStaticShadows`, clears the 64x64 global grid, and initializes list/tail fields.
- `CStaticShadows__ClearAllShadowEntries`, `CStaticShadows__UpdateLightVectorAndRebuild`, `CStaticShadows__UpdateVisibility`, `CStaticShadows__BuildShadowMaps`, and `CStaticShadows__ApplyShadowsToGrid` now carry bounded comments/signatures tied to list cleanup, light-vector rebuild, visibility invalidation, shadow-map building, and grid bitmap application.
- `CStaticShadows__ShadowMapEntryDestructor` and `CStaticShadows__ShadowMapEntryDeletingDestructor` correct stale manager/destroy-node wording. The read-back shows per-entry 0x200-byte bitmap cleanup, 0x1c-byte vector helper use, and flag-driven deleting-destructor behavior.
- `CPolyBucket__ScalarDeletingDestructor` corrects the stale static-shadow cleanup-owner label. The body is a CPolyBucket scalar-deleting destructor reached during static-shadow build cleanup.
- `CStaticShadows__RayTriangleIntersect` is documented as a cdecl ray/segment versus triangle predicate with an unused seventh stack slot and angle-sum inside-triangle test.
- `CStaticShadows__LoadAll` and `CStaticShadows__Load` harden the static-shadow chunk-reader deserialization path for linked shadow entries and optional 0x200-byte bitmap cells.

Artifacts are under `subagents/ghidra-static-reaudit/wave511-static-shadows-004eba30/`.

## Verification

- `ApplyStaticShadowsWave511.java` dry: `updated=0 skipped=13 renamed=0 would_rename=4 missing=0 bad=0`.
- `ApplyStaticShadowsWave511.java` apply: `updated=13 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`.
- `ApplyStaticShadowsWave511.java` receiver fix apply: `updated=1 skipped=12 renamed=0 would_rename=0 missing=0 bad=0`.
- `ApplyStaticShadowsWave511.java` verify dry: `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`.
- All four mutation passes reported `REPORT: Save succeeded`.
- Post-readback exports verified `13` metadata rows, `13` tag rows, `25` xref rows, `3133` instruction rows, and `13` decompile exports.
- `py -3 tools\ghidra_static_shadows_wave511_probe.py --check` passed.
- `cmd.exe /c npm run test:ghidra-static-shadows-wave511` passed.
- Queue refresh passed and reports `6078` functions, `2383` commented, `3695` commentless, `1620` exact-undefined signatures, and `1439` `param_N` signatures.
- Current telemetry proxies are comment-backed `2383/6078 = 39.21%` and strict comment-plus-clean-signature `2329/6078 = 38.32%`; these are progress telemetry only, not completion certification.
- Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260517-183811_post_wave511_static_shadows_verified` with `19` files, `158370695` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

- Runtime shadow behavior or runtime rebuild behavior.
- Exact source-body identity for the checked helpers.
- Concrete CStaticShadows/shadow-entry/render-mesh/terrain/chunk/CPolyBucket/render-state layouts.
- BEA launch behavior, game patching behavior, or rebuild parity.
