# WinUI Asset Library Row Breadth Evidence - 2026-05-06

Status: GREEN

Evidence-report commit: 1daaa04bfbf2203502a0bf91725da53201bc9f30

## Purpose

This report records a focused native WinUI Asset Library row-breadth smoke. The prior evidence proves catalog-wide exported asset readability; this pass proves the native Asset Library can repeatedly search and select representative real generated rows without losing preview/export state.

Private generated catalogs, exported textures/models, screenshots, raw UI proof JSON, local install paths, and generated asset payloads remain under ignored local evidence storage.

## Source Boundary

- Source material: read-only local Battle Engine Aquila install.
- Generated outputs: ignored local full-corpus asset export under `subagents/`.
- UI target: native WinUI 3 desktop app.
- Mutation: none.
- Runtime launch: none.
- Public release claim: no private asset payloads are included or redistributed.

## Representative Rows

The smoke cycles these catalog families through the native Asset Library:

- Textures: cloud, boss-goodie Warspite, trooper, and lit weapon-light samples.
- Loose meshes: arachnid, boss Warspite, Gill head, and battle tank samples.
- Embedded meshes: one body payload sample.

The committed report intentionally records sample families, not private export paths.

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | WinUI app built successfully. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided"` | FAIL then PASS | First run used an ambiguous `warspite` search that selected a different sorted texture row. After changing the sample to `ca_boss_warspite`, the focused smoke passed 1/1. |

## Proven

- The native Asset Library can load the current generated full-corpus catalog.
- The native search/select path works repeatedly across representative texture rows.
- Texture selections keep the selected title, export availability, and export action state live.
- The native search/select path works repeatedly across representative loose model rows.
- Model selections keep wireframe status, model facts, and export action state live.
- One embedded model row also reaches the same model preview/export state.

## Not Proven

- Row-by-row native UI preview for all 828 textures and all 352 model rows.
- Full native 3D/material/animation rendering.
- Public redistribution rights for extracted game assets.
- Packaged-output behavior for the Asset Library catalog workflow.

## Verdict

GREEN for representative native WinUI Asset Library row-breadth interaction.

The remaining Asset Library breadth gap is exhaustive row-by-row native UI preview/render coverage, not representative native search/select behavior or catalog-wide exported-file readability.
