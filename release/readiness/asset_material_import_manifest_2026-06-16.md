# Asset Material Import Manifest Readiness Note

Status: local read-only tooling proof
Date: 2026-06-16
Scope: active AppCore/AppCore.Host/C# CLI asset-material tooling

This slice turns the existing material import readiness counts into a reusable sanitized manifest for active tooling. `AssetMaterialImportManifestService` emits per-model rows and per-texture-binding resolution rows with resolution kind `catalog`, `sidecar`, or `unresolved`.

Active commands:

- `OnslaughtCareerEditor.AppCore.Host export-asset-material-import-manifest <catalog.json-or-directory>`
- `OnslaughtCareerEditor.Cli --asset-material-import-manifest <catalog.json-or-directory> [--fail-on-unresolved-material-bindings]`

Copied-corpus smoke against `subagents\texture_mesh_asset_bridge_proof_2026-06-08`:

- schema: `appcore-asset-material-import-manifest.v1`
- model rows: `352`
- import-ready model rows: `352`
- texture binding rows: `1268`
- catalog-resolved texture binding rows: `1268`
- sidecar-resolved texture binding rows: `0`
- unresolved texture binding rows: `0`
- CLI unresolved gate: PASS with exit code `0`

Validation:

- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"`: PASS, `61` tests.
- `dotnet build OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo`: PASS.
- `dotnet build OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj --nologo`: PASS.
- AppCore.Host manifest smoke: PASS.
- C# CLI manifest gate smoke: PASS.

Boundary:

- No installed game files were mutated.
- No original `BEA.exe` bytes were read or changed.
- No private asset payloads are emitted.
- Full local paths are intentionally omitted from the manifest payload.
- This is not real importer execution, native textured rendering, animation, runtime model-viewer behavior, gameplay proof, rebuild parity, or no-noticeable-difference parity.
