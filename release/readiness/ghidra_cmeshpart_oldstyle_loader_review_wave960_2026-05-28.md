# Ghidra CMeshPart Old-Style Loader Review Wave960

Status: read-only static re-audit PASS
Date: 2026-05-28
Tag: `cmeshpart-oldstyle-loader-review-wave960`

Wave960 re-reviewed the CMeshPart old-style mesh loader pair after static export-contract closure. The wave made no Ghidra mutation: no renames, no signature changes, no comment/tag changes, no function-boundary changes, and no executable-byte changes.

## Scope

Focused Wave911 candidates re-reviewed:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x004aede0` | `CMeshPart__LoadOldStyle_VersionA` | Live name/signature/comment/tags still match Wave815: `CMesh__Load` calls this at `0x004a8f05`, the body calls `CMeshPart__RebuildPerVertexNormalsAndTangents`, and the epilogue is `RET 0x14`. |
| `0x004af110` | `CMeshPart__LoadOldStyle_VersionB_WithExtraBlock` | Live name/signature/comment/tags still match Wave815: `CMesh__Load` calls this at `0x004a8f49`, VersionB consumes the extra `+0xb8` counted block, and the epilogue is `RET 0x14`. |

Context anchors also re-read: `0x004a5b70 CMesh__Load`, `0x004adf80 CMesh__ClearField08`, `0x004ae640 CMeshPart__FreeOwnedResourcePointers`, `0x004af470 CMeshPart__LoadVerticesAndTriangles`, `0x004afbb0 CMeshPart__LoadVerticesWithBones`, `0x004b27a0 CMeshPart__LoadFromStream`, and `0x004b3180 CMeshPart__LoadMaterial`.

## Evidence

Fresh serialized Ghidra exports under `subagents/ghidra-static-reaudit/wave960-cmeshpart-oldstyle-loader-review`:

- `9` metadata rows, all `OK`.
- `9` tag rows, all `OK`.
- `15` xref rows.
- `729` around-address instruction rows.
- `7254` function-body instruction rows.
- `9` decompile-index rows, all `OK`.
- `6` direct string dumps: `[maintainer-local-source-export-root]\MeshPart.cpp`, old mesh version tokens `2.01`, `2.02`, `2.03`, `2.06`, and tag token `HORI`.

Representative anchors:

| Evidence | Anchor |
| --- | --- |
| `CMesh__Load` dispatches to VersionA | `0x004a8f05 CALL 0x004aede0`. |
| `CMesh__Load` dispatches to VersionB | `0x004a8f49 CALL 0x004af110`. |
| `CMesh__Load` dispatches to the newer non-skinned loader | `0x004a8f5c CALL 0x004af470`. |
| VersionA rebuilds normals/tangents and keeps the five-stack-argument ABI | `0x004af101 CALL 0x004b1eb0`; `0x004af10d RET 0x14`. |
| VersionB rebuilds normals/tangents and keeps the same ABI | `0x004af456 CALL 0x004b1eb0`; `0x004af462 RET 0x14`. |
| Newer non-skinned and skinned loaders provide ABI contrast | `0x004afba5 RET 0x14`; `0x004b07f0 RET 0x1c`. |

Continuity checks:

- `npm run test:ghidra-cmeshpart-wave449`: PASS.
- `npm run test:ghidra-cmesh-segment-review-wave914`: PASS.
- Historical `npm run test:ghidra-meshpart-tail-wave815` fails on stale Wave815 queue/state snapshot assertions (`6098`, `5599/6098`, and old state-token expectations), not on current live Wave960 metadata or instruction anchors. Wave960 focused validation owns the current old-style loader evidence.

Verified Ghidra backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260528-123300_post_wave960_cmeshpart_oldstyle_loader_review_verified
```

Backup summary: `19` files, `173542279` bytes, `DiffCount=0`.

Wave911 focused re-audit progress after Wave960: `305/1408 = 21.66%`.
Static export-contract function-quality closure remains `6151/6151 = 100.00%`.

Probe anchor: Wave960; cmeshpart-oldstyle-loader-review-wave960; 0x004aede0 CMeshPart__LoadOldStyle_VersionA; 0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock; 0x004a8f05; 0x004a8f49; 0x004af10d RET 0x14; 0x004af462 RET 0x14; [maintainer-local-source-export-root]\MeshPart.cpp; 2.01; 2.02; 2.03; 2.06; HORI; 305/1408 = 21.66%; 6151/6151 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-123300_post_wave960_cmeshpart_oldstyle_loader_review_verified; no mutation.

## Boundaries

This wave proves static retail Ghidra continuity for the saved old-style MeshPart loader names, signatures, comments, tags, callsites, epilogues, decompile output, and string/version anchors listed above.

It does not prove the exact old mesh-format schema, exact `CMeshPart` field names or concrete layouts, exact Stuart-source method identity, runtime mesh loading/render/collision behavior, BEA patching behavior, or rebuild parity.
