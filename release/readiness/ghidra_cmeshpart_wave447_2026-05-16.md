# Ghidra CMeshPart Wave447 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra signature/comment/tag hardening

## Summary

Wave447 continued the mesh/collision-adjacent queue after Wave446 by hardening nine existing `CMeshPart` functions covering vertex channel allocation, triangle polybucket search, line-triangle polybucket search, polybucket creation, part initialization, geometry allocation, and local bounds/radius computation.

No installed Steam game files were touched. This wave only saved Ghidra metadata in the working Ghidra project and records public-safe summaries, scripts, and checks. Raw decompile exports remain under ignored `subagents/` evidence.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004adff0` | `void __thiscall CMeshPart__SetVertexCount(void * this, int vertex_count)` | Clears any previous five-pointer vertex channel block, stores the new count at `+0x08`, allocates `vertex_count * 0x14`, and derives channel pointers at `+0x0c..+0x1c`. |
| `0x004ae110` | `int __thiscall CMeshPart__StartTriangleBucketSearch(void * this, int search_key0, int search_key1, void * out_triangle_vertices, void * query_context)` | Starts a polybucket triangle search through part `+0x100`, calls `CPolyBucket__StartSearch`, and writes the first triangle's mapped vertex triplet. |
| `0x004ae1a0` | `int __thiscall CMeshPart__GetNextTriangleFromBucketSearch(void * this, void * out_triangle_vertices, void * query_context)` | Advances the active polybucket triangle search with `CPolyBucket__GetNextTriangle` and maps the returned 16-bit local triangle indices into the caller output triplet. |
| `0x004ae220` | `int __thiscall CMeshPart__StartLineTriangleBucketSearch(void * this, int line_arg0, int line_arg1, void * out_triangle_vertices, void * query_context)` | Starts a line/polybucket triangle search with `CPolyBucket__StartLineSearch` and writes the first triangle's mapped vertex triplet. |
| `0x004ae2b0` | `void __fastcall CMeshPart__CreatePolyBucket(void * this)` | Lazily allocates a 0xb8-byte bucket-style object at part `+0x100` for mesh types 1 or 3, clones the part, optionally optimizes it, builds the bucket, and frees failed bucket/clone resources. |
| `0x004ae430` | `int __thiscall CMeshPart__GetNextLineTriangleFromBucketSearch(void * this, void * out_triangle_vertices, void * line_search_context, void * query_context)` | Advances line-triangle search with `CPolyBucket__GetNextLineTriangle` and maps the returned local triangle indices into the caller output triplet. |
| `0x004ae4b0` | `void * __fastcall CMeshPart__Init(void * this)` | Clears observed fields, copies the global 4x3 basis block, seeds defaults including `+0x12c = 0.5f`, allocates a 0x28-byte helper and a 0x128-byte CDXMeshVB-style object, and back-links the object to the part. |
| `0x004ae860` | `int __thiscall CMeshPart__AllocateGeometry(void * this, int dvertex_count, int pvertex_count, int triangle_count, int texcoord_count, int frame_count)` | Records geometry counts, allocates DVertex storage, per-frame PVertex pointer slots and arrays, and triangle storage, returning success only after all allocations succeed. |
| `0x004aea50` | `void __fastcall CMeshPart__ComputeLocalBoundsAndBoundingRadius(void * this)` | Scans the first per-frame vertex array, computes min/max local bounds, writes center/extents/status into the helper at `+0xfc`, stores the median extent at `+0x130`, and computes radius/magnitude fields. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyCMeshPartWave447.java` dry/apply/verify | PASS | Dry reported `updated=0`, `skipped=9`, `missing=0`, `bad=0`; apply reported `updated=9`, `skipped=0`, `missing=0`, `bad=0`; verify dry reported `skipped=9`, `missing=0`, `bad=0`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `9` metadata rows, `9` tag rows, `20` xref rows, `873` instruction rows, and `9` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_cmeshpart_wave447_probe.py tools\ghidra_cmeshpart_wave447_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmeshpart_wave447_probe_test.py` | PASS | Focused tests passed `5/5`. |
| `cmd.exe /c npm run test:ghidra-cmeshpart-wave447` | PASS | Focused probe returned `PASS` for all `9` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6057` total functions, `1921` commented functions, `4136` commentless functions, `1742` undefined signatures, and `1714` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6057`
- Commented function objects: `1921`
- Commentless function objects: `4136`
- `undefined` signatures: `1742`
- Signatures still using `param_N`: `1714`

Telemetry-only proxies are comment-backed `1921/6057 = 31.72%` and strict clean-signature `1858/6057 = 30.68%`. These are not certification and are not completion gates.

## Backup

The actual saved Ghidra project was backed up after read-back at `[maintainer-local-ghidra-backup-root]\BEA_20260516-103500_post_wave447_cmeshpart_verified`. The backup comparison reported `19` files, `156404615` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

This wave does not prove runtime mesh loading, rendering, culling, collision, or static-shadow behavior; exact source method identities; concrete `CMeshPart`, polybucket, helper-record, vertex, or triangle layouts; exact field names/types; BEA launch behavior; game patching; or source-to-retail rebuild parity.
