# Asset Material Package Rebuild Preview Readiness Note

Status: guarded app-owned rebuild-preview artifact proof
Date: 2026-06-16
Scope: active AppCore/AppCore.Host/C# CLI/WinUI material package rebuild-preview output

This slice adds the first deterministic adapter-output consumer after staged importer input. `AssetMaterialImportPackageRebuildPreviewService` consumes a completed `material-package-importer-input.v1.json` plan, re-reads staged FBX preview geometry, and emits package-local `rebuild-preview/` OBJ wireframe files plus per-model binding sidecars and `material-package-rebuild-preview.v1.json`.

Validation:

- `dotnet build OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo`: PASS after rerunning serially.
- `dotnet build OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj --nologo`: PASS.
- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter FullyQualifiedName~AssetCatalogServiceTests`: PASS, `87` focused tests.
- `dotnet build OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo`: PASS.
- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser`: PASS.
- `npm run test:asset-material-package-materialization`: PASS.

Copied-corpus rebuild-preview proof:

- Host preflight: `352/352` model previews ready, `352` would-write preview rows, no `rebuild-preview/` root created.
- Host wrong-arm smoke: exits non-zero and creates no `rebuild-preview/` root.
- Host armed materialization: `352` OBJ wireframes, `352` binding sidecars, and `1,268` texture-binding rows under ignored `subagents/` output.
- CLI preflight over existing output: `352` matching existing preview rows and `0` would-write rows.
- CLI armed materialization over existing output: idempotent, `0` written preview rows and `352` existing preview rows.
- Package inspection after rebuild-preview output still reports `extraPayloadFiles=0`.
- Generated rebuild-preview JSON avoids package-root paths, catalog-source paths, and `sha256` source hash tokens.
- AppCore regression coverage asserts generated OBJ, binding-sidecar, and manifest files are UTF-8 without BOM for Python/tooling compatibility.

Boundary:

- The copied private asset output is under ignored `subagents/`.
- No installed game files or original `BEA.exe` bytes were mutated.
- No private asset payloads are committed.
- This proves deterministic rebuild-preview OBJ/binding artifact output from the copied-corpus static asset contracts.
- This is not full mesh conversion, Godot work, native textured rendering, animation, lighting, runtime model-viewer behavior, gameplay proof, rebuild parity, or no-noticeable-difference parity.
