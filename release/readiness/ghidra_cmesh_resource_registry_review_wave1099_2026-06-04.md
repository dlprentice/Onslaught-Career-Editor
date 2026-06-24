# Ghidra CMesh Resource Registry Review Wave1099 Readiness Note

Status: complete read-only static review
Date: 2026-06-04
Scope: `cmesh-resource-registry-review-wave1099`

Wave1099 re-read eighteen saved CEngine/CMesh resource registry, load, deserialize, cache, texture-binding, optimization, and release rows as a focused post-100 static system review. The pass was read-only: no Ghidra names, signatures, comments, tags, function boundaries, or executable bytes were changed; BEA was not launched; no installed-game/runtime file was mutated.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00449dc0 CEngine__LoadAllNamedMeshes` | `CWorld__LoadWorld` caller reads named mesh entries, updates the global named-mesh table, and dispatches new entries through `CMesh__FindOrCreate`; source reference `references/Onslaught/engine.cpp` contains `CEngine::LoadAllNamedMeshes`. |
| `0x004a5020 CMesh__Init` | Initializes the 0x174-byte mesh object, allocates the resource buffer, and links the object through global mesh list `DAT_00704ad8`. |
| `0x004a50b0 CMesh__FreeResourcesAndUnlink` | Unlinks from `DAT_00704ad8`, releases material/resource records through `CMesh__ReleaseEmbeddedResources`, frees parts, emitters, index/texture arrays, and decrements chained mesh refcount field `+0x170`. |
| `0x004a5200 CMesh__InitStatic` | Initializes the default embedded mesh/texture resource in `DAT_00704adc`, including `meshtex\default.tga`. |
| `0x004a52b0 CMesh__ClearAllUsageMarkers` | Clears usage/ref marker `+0x170` across `DAT_00704ad8` and then calls `CMesh__ClearOut`. |
| `0x004a52d0 CMesh__ClearOut` | Releases `DAT_00704adc`, then repeatedly frees global mesh-list entries with zero usage/ref marker; emits mesh leak/no-leak debug strings. |
| `0x004a53f0 CMesh__StatusLoadingMeshResources` | Sends `Loading mesh resources` status through global console/status object `DAT_00663498`; reached by frontend and game resource load paths. |
| `0x004a5430 CMesh__FreeUnusedAndReportLeaks` | End-of-level free/leak-report path called from frontend release and `CGame__Shutdown`, using `DAT_00704ae0` and `DAT_00704ad8`. |
| `0x004a5970 CMesh__LoadByNameWithStatus` | Builds `data\Meshes\` file path, opens a file mem-buffer, and calls `CMesh__Load(this, mem_buffer, load_context)`. |
| `0x004a5b70 CMesh__Load` | Main mesh stream loader; validates mesh stream/version tokens, loads material/part tables, texture records, old/new part bodies, chained meshes, and optimization/link/cache refresh paths. |
| `0x004aa410 CMesh__FindTextureByNameSuffixHint` | Mesh texture-record lookup helper that chooses texture find mode by observed name suffix/prefix hints. |
| `0x004aa6b0 CMesh__GetNameOrUnknown` | Scans `DAT_00704ad8` by next-link `+0x158`, returns mesh name `+0x24`, or returns `unknown mesh name`. |
| `0x004aa6e0 CMesh__FindOrCreate` | Global mesh cache helper used by engine/frontend/DX/RT callers; scans by name, increments `+0x170` on hit, or allocates/loads/frees on miss/failure. |
| `0x004aab90 CMesh__Deserialize` | Chunk/resource deserialize path used by resource accumulator and FE goodies, with optional `data\resources\meshes\m_%s.aya` archive path and chained mesh recursion. |
| `0x004ab330 CMesh__FindByRuntimeId` | Scans `DAT_00704ad8` by runtime id field `+0x154`. |
| `0x004ab360 CMesh__OptimizeParts` | Mesh-part optimization pass updates total/removed part globals `DAT_00704af0` and `DAT_00704af4`. |
| `0x004adf90 CMesh__ReleaseEmbeddedResources` | Releases 0x24-byte mesh material/texture resource records and decrements HUD/DX resource counters. |
| `0x004ae0d0 CMesh__InitPartVBufTextureFormats` | Resolves `CVBufTexture__GetOrCreate` and applies observed VB/IB format constants for mesh material/part records. |

Read-back evidence:

- Fresh read-only exports verified `18` metadata rows, `18` tag rows, `63` xref rows, `6524` instruction rows, and `18` decompile rows.
- Export logs reported `targets=18 found=18 missing=0`, `rows=18 missing=0`, `Wrote 63 rows`, `Wrote 6524 function-body instruction rows`, and `targets=18 dumped=18 missing=0 failed=0`.
- Static function-quality closure remains `6410/6410 = 100.00%`, expanded static surface remains `1560/1560 = 100.00%`, Wave911 focused progress remains `812/1408 = 57.67%`, and Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-193549_post_wave1099_cmesh_resource_registry_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

What this proves:

- The eighteen target function rows exist in the saved Ghidra project with saved names, signatures, comments, and tags.
- Fresh xrefs/decompile tie engine named-mesh loading, global mesh cache, file-backed mesh load, AYA/chunk deserialize, default resource setup, usage markers, leak cleanup, texture binding, VBuf texture setup, part optimization, and embedded-resource release into one coherent static CMesh resource registry/load-system map.
- This wave connects older Wave443/Wave444/Wave445/Wave813/Wave814/Wave905/Wave1093 evidence without changing the saved Ghidra database.

What remains unproven:

- Runtime mesh loading, resource-cache behavior, leak reporting, texture binding, VBuf resource behavior, or render outcomes.
- Exact CMesh, CMeshPart, material/resource-record, load-context, chunk-reader, texture-record, VBuf texture, and global-list layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1099; cmesh-resource-registry-review-wave1099; 0x00449dc0 CEngine__LoadAllNamedMeshes; 0x004a5020 CMesh__Init; 0x004a50b0 CMesh__FreeResourcesAndUnlink; 0x004a5200 CMesh__InitStatic; 0x004a52d0 CMesh__ClearOut; 0x004a5430 CMesh__FreeUnusedAndReportLeaks; 0x004a5970 CMesh__LoadByNameWithStatus; 0x004a5b70 CMesh__Load; 0x004aa6e0 CMesh__FindOrCreate; 0x004aab90 CMesh__Deserialize; 0x004adf90 CMesh__ReleaseEmbeddedResources; DAT_00704ad8; DAT_00704adc; data\Meshes; data\resources\meshes\m_%s.aya; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-193549_post_wave1099_cmesh_resource_registry_review_verified; read-only review.
