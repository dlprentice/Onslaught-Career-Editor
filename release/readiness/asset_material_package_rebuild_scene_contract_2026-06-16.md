# Asset Material Package Rebuild Scene Contract Readiness Note

Status: guarded app-owned scene-contract proof
Date: 2026-06-16
Scope: active AppCore/AppCore.Host/C# CLI/WinUI material package rebuild-scene contract output

This slice turns the existing package-local rebuild-preview output into deterministic scene/mesh/material contract JSON for future importer/rebuild tooling. `AssetMaterialImportPackageRebuildSceneService` requires completed `rebuild-preview/` OBJ files and binding sidecars, re-reads the staged FBX model input, parses OBJ bounds, and emits package-local `rebuild-scene/models/*.scene.json` files plus `material-package-rebuild-scene.v1.json`.

What the scene contracts record:

- Package-relative OBJ, binding-sidecar, and staged model-input paths.
- OBJ-derived vertex rows, edge rows, and bounds.
- FBX mesh format/version, geometry/model counts, vertex rows, polygon-index rows, normal rows, UV rows, vertex-color rows, material rows, material assignment rows, object/property connection rows, texture-to-material connection rows, and texture-to-material slot names.
- Package-relative texture binding rows with dimensions and readiness flags.

Focused validation:

- `dotnet build OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo`: PASS.
- `dotnet build OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj --nologo`: PASS.
- `dotnet build OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo`: PASS.
- `dotnet test OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter FullyQualifiedName~AssetCatalogServiceTests`: PASS, `89` focused AppCore asset-catalog tests.
- `npm run test:asset-material-package-materialization`: PASS.

Copied-corpus rebuild-scene proof:

- Host preflight: `352/352` scene contracts ready, `352` would-write scene rows, no `rebuild-scene/` root created.
- Host wrong-arm smoke: exits non-zero and creates no `rebuild-scene/` root.
- Host unsupported-option smoke: exits non-zero and creates no `rebuild-scene/` root.
- Host armed materialization: `352` scene JSON files and `material-package-rebuild-scene.v1.json` under ignored `subagents/` output.
- CLI preflight over existing output: `352` matching existing scene rows and `0` would-write rows.
- CLI armed materialization over existing output: idempotent, `0` written scene rows and `352` existing scene rows.
- Probe totals: `1,268` texture-binding rows, positive FBX vertex rows, positive polygon-index rows, positive UV rows, positive texture-to-material connection rows, and package inspection `extraPayloadFiles=0`.
- Generated scene JSON avoids package-root paths, catalog-source paths, and `sha256` source hash tokens.
- AppCore regression coverage rejects corrupt/stale rebuild-preview OBJ output before scene-contract rows are emitted; the scene parser also validates edge indices against the parsed vertex table as defense in depth.

Boundary:

- The copied private asset output is under ignored `subagents/`.
- No installed game files or original `BEA.exe` bytes were mutated.
- No private asset payloads are committed.
- This proves deterministic package-local scene/mesh/material contract output from copied-corpus static asset evidence.
- This is not Godot work, real importer execution, native textured rendering, animation, lighting, runtime model-viewer behavior, gameplay proof, rebuild parity, or no-noticeable-difference parity.
