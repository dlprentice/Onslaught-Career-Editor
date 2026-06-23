# WinUI Asset Catalog Readability Evidence - 2026-05-06

Status: GREEN

Evidence-report commit: b5b890a2bf284f2bc095d88ace1c9720a6d05dce

## Purpose

This report records a public-safe full-corpus Asset Library readability pass for the current generated asset catalog. It closes the gap between focused WinUI visual proof and broad source/export coverage: the app can now machine-check that generated texture exports and model exports are present and minimally readable before a maintainer relies on the Asset Library catalog.

The private generated catalog, extracted PNG files, exported FBX files, raw proof JSON, screenshots, local install paths, and generated asset payloads remain under ignored local evidence storage. This public report intentionally records counts and command results only.

## Source Boundary

- Source material: read-only local Battle Engine Aquila install.
- Generated outputs: ignored local full-corpus asset export under `subagents/`.
- Mutation: none.
- Runtime launch: none.
- Public release claim: no private asset payloads are included or redistributed.

## Implementation

- Added `AssetCatalogReadabilityService` in AppCore.
- Added AppCore tests for public-safe texture/model readability summaries.
- Added `OnslaughtCareerEditor.AppCore.Host inspect-asset-catalog-readability`.
- The host command omits full local paths and private payload hashes from its new readability payload.

## Full-Corpus Readability Summary

The command was run against the ignored full-corpus split-lane asset catalog generated from the read-only local game install.

| Surface | Result |
| --- | ---: |
| Texture catalog rows | 828 |
| Texture exports present | 828 |
| Readable PNG headers | 828 |
| Missing texture exports | 0 |
| Unreadable texture exports | 0 |
| Model rows | 352 |
| Model exports present | 352 |
| Model metadata readable | 352 |
| Model wireframe data available | 352 |
| Missing model exports | 0 |
| Unreadable model exports | 0 |

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"` | PASS | 5/5 focused AssetCatalogService tests passed. |
| `dotnet build .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo` | PASS | AppCore.Host built successfully. |
| `dotnet run --project .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --no-build -- inspect-asset-catalog-readability <ignored-private-catalog> --sample-limit 8` | PASS | Reported 828/828 readable PNG texture exports and 352/352 readable model exports with wireframe data. |

## Proven

- The current generated full-corpus asset catalog resolves every texture export row to a present PNG file with a readable PNG header.
- The current generated full-corpus asset catalog resolves every loose/embedded model row to a present FBX export with readable metadata and bounded wireframe preview data.
- AppCore can produce a public-safe readability summary without exposing private absolute paths or private asset payloads.

## Not Proven

- Row-by-row native UI preview for every texture and model row.
- Full native 3D/material/animation rendering.
- Rebuildability of the full game from extracted assets.
- Public redistribution rights for extracted game assets.
- Packaged-output behavior for this Asset Library catalog workflow.

## Verdict

GREEN for catalog-wide generated asset export readability.

The remaining Asset Library gap is no longer basic full-corpus export readability. The remaining product gap is broader native UI row-by-row preview/render interaction and richer model rendering beyond the current bounded wireframe.
