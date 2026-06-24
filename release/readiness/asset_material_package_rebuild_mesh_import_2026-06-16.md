# Asset Material Package Rebuild Mesh Import Readiness Note

Status: active-lane rebuild mesh import validation complete
Date: 2026-06-16
Scope: `asset-material-package-rebuild-mesh-import`

This slice validates that the generated package-local rebuild-mesh OBJ/MTL files are internally consumable by active importer/converter/rebuild tooling. It does not use Godot, archived Electron/WPF/Python GUI lanes, a BEA runtime launch, or a renderer.

Command surfaces:

- AppCore.Host: `materialize-asset-material-package-rebuild-mesh-import <package-output-directory> [--preflight] [--arm-private-asset-output "MATERIALIZE ASSET MATERIAL PACKAGE"]`
- C# CLI: `--asset-material-package-rebuild-mesh-import-materialize <package-output-directory> [--asset-material-package-preflight] [--arm-private-asset-output "MATERIALIZE ASSET MATERIAL PACKAGE"]`
- Focused probe: `npm run test:asset-material-package-materialization`

Validated copied-corpus import output:

| Metric | Count |
| --- | ---: |
| Import rows ready | `352 / 352` |
| OBJ files parsed | `352` |
| MTL files parsed | `352` |
| Vertex rows | `376,602` |
| Face rows | `275,514` |
| Normal rows | `826,542` |
| UV rows | `826,542` |
| Material rows | `8,448` |
| Face-material uses | `275,514` |
| Textured material rows | `1,268` |
| Texture references | `1,268` |
| Missing textures | `0` |
| Count mismatches | `0` |
| Undefined material uses | `0` |
| Unsafe paths | `0` |

Read-back evidence:

- Host preflight parses all generated OBJ/MTL rows and writes no files.
- Host wrong-arm execution is rejected before writing `material-package-rebuild-mesh-import.v1.json`.
- Armed Host materialization writes `material-package-rebuild-mesh-import.v1.json`.
- CLI preflight and armed materialization validate the same package-local outputs.
- Generated JSON avoids source paths, package-root paths, catalog-source paths, and hashes.
- Package inspection remains stable with `extraPayloadFiles=0`.
- WinUI Asset Library reports rebuild-mesh import validation after selected-model package preparation or existing package detection.

What this proves:

- The current package-local face-bearing OBJ/MTL mesh outputs parse back into deterministic consumer rows.
- OBJ vertex/face/normal/UV counts match the source rebuild-mesh manifest.
- MTL material rows and texture references resolve to staged package-local texture inputs.
- The generated mesh/material files are concrete active-lane inputs for future importer/converter/rebuild tooling.

What remains unproven:

- Real importer execution.
- Native textured rendering.
- Animation, lighting, shader behavior, or material visual parity.
- Runtime model-viewer behavior.
- Godot integration.
- BEA runtime behavior.
- Rebuild parity or no-noticeable-difference parity.
