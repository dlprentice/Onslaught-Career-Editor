# Ghidra Wave900+ Through Wave1099 Recheck Note

Status: aggregate validation passed
Date: 2026-06-04
Scope: `wave900-plus-through-wave1099-recheck`

This note extends the post-Wave900 recheck chain through Wave1099. The intended local validation gate is:

```powershell
npm run test:ghidra-wave900-plus-through-wave1099-recheck
```

Wave1099 (`cmesh-resource-registry-review-wave1099`) re-read eighteen saved CEngine/CMesh resource registry, load, deserialize, cache, texture-binding, optimization, and release rows with no Ghidra mutation. The focused readiness note is [`ghidra_cmesh_resource_registry_review_wave1099_2026-06-04.md`](ghidra_cmesh_resource_registry_review_wave1099_2026-06-04.md).

Coverage anchors:

- Static function-quality closure remains `6410/6410 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress remains `1560/1560 = 100.00%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Representative rows include `0x00449dc0 CEngine__LoadAllNamedMeshes`, `0x004a5020 CMesh__Init`, `0x004a50b0 CMesh__FreeResourcesAndUnlink`, `0x004a5200 CMesh__InitStatic`, `0x004a52d0 CMesh__ClearOut`, `0x004a5430 CMesh__FreeUnusedAndReportLeaks`, `0x004a5970 CMesh__LoadByNameWithStatus`, `0x004a5b70 CMesh__Load`, `0x004aa6e0 CMesh__FindOrCreate`, `0x004aab90 CMesh__Deserialize`, and `0x004adf90 CMesh__ReleaseEmbeddedResources`.
- Fresh read-only exports verified `18` metadata rows, `18` tag rows, `63` xref rows, `6524` instruction rows, and `18` decompile rows.
- Caller/context evidence ties the row group to world named-mesh loading, engine/frontend/DX/RT mesh cache callers, CMesh file-backed load and chunk/AYA deserialize paths, global list `DAT_00704ad8`, default resource `DAT_00704adc`, leak/report counter `DAT_00704ae0`, archive flag `DAT_00704ae4`, part optimization counters `DAT_00704af0` / `DAT_00704af4`, `data\Meshes\`, and `data\resources\meshes\m_%s.aya`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-193549_post_wave1099_cmesh_resource_registry_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime mesh/resource/texture/VBuf/render behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Validation result:

- `npm run test:ghidra-cmesh-resource-registry-review-wave1099`: PASS.
- `npm run test:ghidra-wave900-plus-through-wave1099-recheck`: PASS.
- Aggregate PASS summary: `202` readiness notes, `200` covered waves, `198` package probe scripts, `198` evidence bases, `200` backup references, and `73` apply scripts.
- Wave982-Wave1099 direct probe sweep: `118` results, `1` current focused PASS, `117` historical rollover failures classified as expected current-state/doc/queue drift, and `0` disallowed evidence/unclassified failures.
- Current queue check inside the aggregate gate: `6410` total functions, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.

Probe token anchor: Wave1099; cmesh-resource-registry-review-wave1099; 0x00449dc0 CEngine__LoadAllNamedMeshes; 0x004a5020 CMesh__Init; 0x004a50b0 CMesh__FreeResourcesAndUnlink; 0x004a5200 CMesh__InitStatic; 0x004a52d0 CMesh__ClearOut; 0x004a5430 CMesh__FreeUnusedAndReportLeaks; 0x004a5970 CMesh__LoadByNameWithStatus; 0x004a5b70 CMesh__Load; 0x004aa6e0 CMesh__FindOrCreate; 0x004aab90 CMesh__Deserialize; 0x004adf90 CMesh__ReleaseEmbeddedResources; DAT_00704ad8; DAT_00704adc; data\Meshes; data\resources\meshes\m_%s.aya; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-193549_post_wave1099_cmesh_resource_registry_review_verified; read-only review.
