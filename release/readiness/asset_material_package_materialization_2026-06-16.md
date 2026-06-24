# Asset Material Package Materialization Readiness Note

Status: guarded app-owned private-output proof
Date: 2026-06-16
Scope: active AppCore/AppCore.Host/C# CLI material package output

This slice turns the deterministic material package plan into guarded app-owned output. `AssetMaterialImportPackageMaterializationService` supports preflight/no-copy mode and armed copy mode. AppCore.Host and the C# CLI default to preflight behavior unless the exact arm phrase `MATERIALIZE ASSET MATERIAL PACKAGE` is supplied through `--arm-private-asset-output`.

Validation:

- `npm run test:asset-material-package-plan`: PASS, `70` focused AppCore tests.
- `dotnet build OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo`: PASS.
- `dotnet build OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj --nologo`: PASS.
- `npm run test:asset-material-package-materialization`: PASS.

Copied-corpus materialization proof:

- Host preflight: `565` package files planned, `565` would-copy files, no output root created.
- Host armed copy: `565` files copied under ignored `subagents/` output, including `352` model files and `213` texture files.
- CLI preflight: `565` package files planned, no output root created.
- CLI wrong-arm smoke: exits non-zero and creates no output root.

Boundary:

- The copied private asset output is under ignored `subagents/`.
- No installed game files or original `BEA.exe` bytes were mutated.
- No private asset payloads are committed.
- JSON output omits raw source paths and reports package-relative destinations/counts only.
- This proves app-owned material package file output from the copied-corpus catalog.
- This is not Godot work, native textured rendering, animation, runtime model-viewer behavior, gameplay proof, rebuild parity, or no-noticeable-difference parity.
