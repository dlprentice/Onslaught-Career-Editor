# Asset Material Package Rebuild Mesh Readiness Note

Status: active-lane rebuild mesh output validated
Date: 2026-06-16
Scope: `asset-material-package-rebuild-mesh`

This slice advances the asset/rebuild tooling lane from package-local scene contracts into deterministic package-local mesh/material files. It does not use Godot, archived Electron/WPF/Python GUI lanes, a BEA runtime launch, or a renderer.

Command surfaces:

- AppCore.Host: `materialize-asset-material-package-rebuild-mesh <package-output-directory> [--preflight] [--arm-private-asset-output "MATERIALIZE ASSET MATERIAL PACKAGE"]`
- C# CLI: `--asset-material-package-rebuild-mesh-materialize <package-output-directory> [--asset-material-package-preflight] [--arm-private-asset-output "MATERIALIZE ASSET MATERIAL PACKAGE"]`
- Focused probe: `npm run test:asset-material-package-materialization`

Validated copied-corpus output:

| Metric | Count |
| --- | ---: |
| Mesh rows ready | `352 / 352` |
| OBJ mesh files | `352` |
| MTL files | `352` |
| Complete mesh payload rows | `352 / 352` |
| Vertex rows | `376,602` |
| Face rows | `275,514` |
| Normal rows | `826,542` |
| UV rows | `826,542` |
| Material rows | `8,448` |
| Texture-binding rows | `1,268` |

Read-back evidence:

- Host preflight reports no output-root creation and all mesh rows ready.
- Host wrong-arm execution is rejected before writes.
- Armed Host materialization writes deterministic `rebuild-mesh/models/*.mesh.obj`, paired `.mesh.mtl` files, and `material-package-rebuild-mesh.v1.json`.
- CLI preflight over the armed output is idempotent and sees existing matching outputs.
- Repeated CLI materialization writes no duplicate payload files and preserves the manifest.
- Generated OBJ/MTL/JSON avoids source paths, package-root paths, catalog-source paths, and hashes.
- Package inspection remains stable with `extraPayloadFiles=0`.
- WinUI Asset Library reports rebuild-mesh readiness after selected-model package preparation or existing package detection.

What this proves:

- Static asset package evidence can be converted into package-local face-bearing OBJ mesh files with paired MTL material files.
- The conversion consumes existing rebuild-scene contracts and staged FBX inputs rather than raw private source paths.
- The output is deterministic, app-owned, arm-gated, idempotent, and inspectable by Host, CLI, and WinUI.
- The generated files are concrete active-lane inputs for future importer/converter/rebuild tooling.

What remains unproven:

- Real importer execution.
- Native textured rendering.
- Animation, lighting, shader behavior, or material visual parity.
- Runtime model-viewer behavior.
- Godot integration.
- BEA runtime behavior.
- Rebuild parity or no-noticeable-difference parity.
