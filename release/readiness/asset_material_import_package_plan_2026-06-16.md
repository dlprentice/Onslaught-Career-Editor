# Asset Material Import Package Plan Readiness Note

Status: local AppCore/Host/CLI product proof
Date: 2026-06-16
Scope: active AppCore material-import package planning

This slice adds a read-only material-import package plan contract. It consumes the sanitized material manifest and dry-run operations, then emits package-relative file entries for ready model exports and deduplicated texture assets.

Current copied-corpus smoke:

- `352/352` model package operations ready.
- `0` blocked package model operations.
- `1268/1268` texture references resolved.
- `0` unresolved texture references.
- `352` model package files.
- `213` unique texture package files.
- `565` total package files.
- `1055` duplicate texture references deduped into the unique texture package set.

Validation:

- `npm run test:asset-material-package-plan`: PASS, `68` focused AppCore tests.
- `dotnet build OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo`: PASS after rerunning serially.
- `dotnet build OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj --nologo`: PASS after rerunning serially.
- `OnslaughtCareerEditor.AppCore.Host plan-asset-material-import-package <copied-corpus catalog>`: PASS, read-only package plan counts above.
- `OnslaughtCareerEditor.Cli --asset-material-import-package-plan <copied-corpus catalog> --fail-on-unresolved-material-bindings`: PASS, exit code `0`.

Boundary:

- The private copied-corpus catalog and extracted assets stayed under ignored `subagents/`.
- No asset bytes were copied into a new package.
- No real importer was executed.
- No installed game files or original `BEA.exe` bytes were mutated.
- No private asset payloads are committed.
- This proves deterministic package-relative planning only.
- This is not Godot work, native textured rendering, animation, runtime model-viewer behavior, gameplay proof, rebuild parity, or no-noticeable-difference parity.
