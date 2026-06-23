# WinUI Model Preview Coverage Evidence - 2026-05-06

## Scope

This report records a public-safe model-preview coverage pass for the WinUI Asset Library after the bounded wireframe preview was added.

- Branch: `wip/sandbox`
- Source commit before this wave: `b47489b4`
- Evidence type: public-safe summary
- Private proof output: ignored local coverage JSON under `subagents/`
- Mutation: none

No private game assets, extracted FBX files, screenshots, absolute install paths, raw generated catalog rows, data URLs, or base64 payloads are included here.

## What Changed

- Added AppCore model-preview coverage accounting for generated asset catalogs.
- Added a read-only `OnslaughtCareerEditor.AppCore.Host inspect-asset-model-preview` command.
- Extended the FBX reader to decode bounded zlib-compressed FBX array payloads for `Vertices` and `PolygonVertexIndex`.
- Added synthetic AppCore tests for compressed FBX geometry arrays and catalog-level preview coverage.

## Private Coverage Summary

The coverage command was run against the existing ignored full-corpus split-lane catalog generated from the read-only local game install. The committed summary intentionally records counts only.

| Metric | Count |
| --- | ---: |
| Total model rows | 352 |
| Loose mesh rows | 213 |
| Embedded mesh rows | 139 |
| Existing FBX export rows | 352 |
| Metadata-readable rows | 352 |
| Wireframe-preview rows | 352 |
| Missing export rows | 0 |
| Unreadable export rows | 0 |

The first broad probe before compressed-array support found only 24/352 rows with wireframe edges. After adding bounded zlib-array support, the same catalog reported 352/352 rows with wireframe-preview data.

## Commands

| Command | Result | Notes |
| --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests\|FullyQualifiedName~FbxModelSummaryReaderTests"` | PASS | 7/7 focused AppCore tests passed. |
| `dotnet build .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo` | PASS | Host command compiled with AppCore. |
| `dotnet run --project .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --no-build -- inspect-asset-model-preview <ignored-private-catalog> --sample-limit 8` | PASS | Public-safe JSON omitted full local paths and reported 352/352 wireframe rows after the fix. |
| `node -e "<parse ignored coverage JSON and assert counts>"` | PASS after regenerating UTF-8 output without BOM | Final parse confirmed 352 total model rows, 352 wireframe rows, and 0 unreadable rows. |

## What This Proves

- The lightweight WinUI/AppCore model preview path can derive wireframe data for every generated FBX row in the current private full-corpus catalog.
- The FBX reader handles both uncompressed and zlib-compressed binary FBX array payloads for the preview fields it needs.
- The new host command can produce public-safe model coverage summaries without exposing full local paths.

## What This Does Not Prove

- Full native 3D rendering.
- Materials, textures, UV rendering, normals, animation, skeletons, camera controls, or lighting.
- Public redistribution approval for extracted game assets or generated model exports.
- Packaged-output behavior for model preview coverage.
- Coverage for future extractor output formats that are not binary FBX.

## Follow-Up

1. Keep this coverage command available for future generated-catalog regressions.
2. Decide whether the long-term model viewer should remain a native lightweight renderer or use a deliberate GLB/glTF conversion pipeline.
3. Add material/texture/UV preview only after the runtime model-format contract is intentionally chosen.
