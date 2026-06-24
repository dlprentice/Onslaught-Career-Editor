# Asset Material Import Dry-Run Plan Readiness Note

Status: local read-only tooling proof
Date: 2026-06-16
Scope: active AppCore/AppCore.Host/C# CLI asset-material tooling

This slice adds a deterministic material-import dry-run plan that consumes the sanitized material-import manifest and emits relative model/texture operations for future rebuild/import tooling. It keeps the work in active AppCore/AppCore.Host/C# CLI lanes; it does not use Godot or archived Electron/WPF/Python GUI lanes.

Active commands:

- `OnslaughtCareerEditor.AppCore.Host plan-asset-material-import-dry-run <catalog.json-or-directory>`
- `OnslaughtCareerEditor.Cli --asset-material-import-dry-run-plan <catalog.json-or-directory> [--fail-on-unresolved-material-bindings]`

Copied-corpus smoke against `subagents\texture_mesh_asset_bridge_proof_2026-06-08`:

- schema: `appcore-asset-material-import-dry-run-plan.v1`
- model operations: `352`
- ready model operations: `352`
- blocked model operations: `0`
- texture operations: `1268`
- catalog-resolved texture operations: `1268`
- sidecar-resolved texture operations: `0`
- unresolved texture operations: `0`
- CLI unresolved gate: PASS with exit code `0`

Validation:

- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"`: PASS, `64` tests.
- `dotnet build OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo`: PASS.
- `dotnet build OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj --nologo`: PASS.
- AppCore.Host dry-run plan smoke: PASS.
- C# CLI dry-run plan gate smoke: PASS.

Boundary:

- No installed game files were mutated.
- No original `BEA.exe` bytes were read or changed.
- No private asset payloads are emitted.
- Full local paths are intentionally omitted from the dry-run payload.
- This is not asset copying, real importer execution, Godot work, native textured rendering, animation, runtime model-viewer behavior, gameplay proof, rebuild parity, or no-noticeable-difference parity.
