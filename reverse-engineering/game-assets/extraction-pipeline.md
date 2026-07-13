---
status: active
last_updated: 2026-05-07
doc_version: 1.2
---

# Asset Extraction Pipeline

## Purpose

Current pinned extractor authority:
[`reference-submodule-audit-2026-07-12.md`](../source-code/reference-submodule-audit-2026-07-12.md).
The legacy dependency chain and private corpus coverage below are useful, but a
tracked public end-to-end synthetic AYA/DDS/FBX fixture is still missing and
the component-license posture is not yet a redistribution approval.

This is the current backend extraction workflow for Battle Engine Aquila assets.

It exists so the project can:

- extract assets from a local retail install without shipping copyrighted assets,
- keep the extraction logic stable enough for WinUI/tooling integration,
- and preserve a reproducible backend surface while higher-value RE continues.

Wave904 (`texture-render-static-review-wave904`) connects this extraction surface back to the static binary texture/resource/decode/render core after queue closure `6113/6113 = 100.00%`. It records a static-coherent texture/resource/decode/render core with `1289` rows across `25` selected families, including `CDXTexture` `366`, `CFastVB` `347`, `CTexture` `233`, and `CVBufTexture` `40`; anchors include `CDXTexture__LoadTextureFromFile_Core`, `CDXTexture__DecodeMemoryToTextureObject`, `CDXTexture__ValidateJpegFrameAndComputeMcuLayout`, `CFastVB__RenderTriangleStripImmediate`, and `CVBufTexture__DrawSpriteEx`. The extraction bridge remains count-based evidence: `847/847` loose textures and `352/352` model material/texture-binding rows are covered, with verified Ghidra backup `[maintainer-local-ghidra-backup-root]\BEA_20260526-101300_post_wave904_texture_render_static_review_verified`. Runtime texture pixels, GPU upload/device behavior, native textured rendering, and in-game render correctness remain separate proof.

Source/extractor boundary: Stuart's source and AYAResourceExtractor help explain architecture and provide extraction tooling context, but the current retail Ghidra database and local installed-resource manifests are the authority for Wave904's static classification.

Wave905 (`mesh-motion-world-particle-static-review-wave905`) connects the mesh/resource extraction surface back to the static binary mesh/motion/world/particle core after queue closure `6113/6113 = 100.00%`. It records a static-coherent mesh/motion/world/particle core with `506` rows across `41` families, including `CMeshPart` `54`, `CMesh` `40`, `CWorld` `38`, `CWorldPhysicsManager` `32`, `CThing` `28`, `CParticleManager` `23`, and `CMeshCollisionVolume` `21`; anchors include `CThing__InitRenderThingFromInitMeshName`, `CMesh__LoadByNameWithStatus`, `CMeshPart__PopulatePoseCacheRecursive`, `CWorld__InitOccupancyBitplanes`, `CWorldPhysicsManager__CreateThingByType`, `CParticleManager__Update`, `CParticleSet__LoadFromArchive`, and `CParticleDescriptor__Load`. The mesh bridge remains count-based evidence: `213/213` loose meshes, `139/139` embedded meshes, and `352/352` model material/texture-binding rows are covered, with verified Ghidra backup `[maintainer-local-ghidra-backup-root]\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`. Runtime collision/physics/render/particle behavior and visual parity remain separate proof.

## Public-Safe Posture

The recommended public shape is a **bring-your-own-game-files** extractor.

- Do not distribute extracted BEA assets with the repo.
- Distribute tooling that users run against their own local install.
- Treat the backend workflow here as the implementation base for a future UI wrapper or toolkit tab.

## Current Backend Entry Point

Use [export_game_assets.py](/tools/export_game_assets.py).

The rebuild-local wrapper `npm run export:local-bea-assets` pins the current
checkout, preflights and holds the three required local DLLs and the exact
`ExtractorRoot\BoxWithTextures.fbx` consumed by the harness, and confines output
to `local-lab/rebuild-godot/`. Those mutable dependencies form a trusted-local
boundary, not cryptographic provenance. For First Flight presentation, manually
convert a selected exported FBX to self-contained GLB or bounded OBJ, place it
under `local-lab/rebuild-godot/staging/from-export/`, and assign player/terrain
roles explicitly or unambiguously. FBX is never activated in the manifest.

Example:

```powershell
py -3 tools\export_game_assets.py --game-root game
```

The orchestrator currently runs these phases in order:

1. packed `*_res_PC.aya` inventory plus embedded `CMSH` body preparation,
2. headless texture and mesh export via [BeaAssetExportHarness](/tools/BeaAssetExportHarness), one asset lane per serial process,
3. `LANGUAGE/*.DAT` corpus export,
4. loose `.vid` manifest export,
5. cross-surface asset catalog generation.

The texture, loose-mesh, and embedded-mesh harness lanes intentionally run as separate serial processes. The legacy AYA extractor uses shared runtime/template files, and concurrent mesh export lanes can lock those files.

## Prerequisites

- .NET 10 SDK for [BeaAssetExportHarness.csproj](/tools/BeaAssetExportHarness/BeaAssetExportHarness.csproj)
- Python 3 for the `tools/*.py` extraction scripts
- Built local runtime for the AYA extractor fork:
  - `references/AYAResourceExtractor/Code/AyaResourceExtractor/bin/Debug/net6.0-windows/AYAResourceExtractor.dll`
  - `references/AYAResourceExtractor/Code/AyaResourceExtractor/bin/Debug/net6.0-windows/DDSTextureUncompress.dll`

## Output Layout

The orchestrator writes a single output root containing:

- `aya_asset_manifest.json`
- `aya_embedded_meshes/`
- `asset_export/`
- `language_export/`
- `video_manifest/`
- `asset_catalog/`
- `logs/`
- `extraction_summary.json`

## Validated Coverage (Current Private Baseline)

The current validated private baseline, refreshed against the user's local Steam install on 2026-05-07, is:

- loose textures: `847 / 847` exported to PNG
- loose meshes: `213 / 213` exported to FBX
- embedded packed mesh bodies: `139 / 139` exported to FBX
- packed refs:
  - `TEXT 601 / 601`
  - reference `MESH 209 / 209`
  - `GDIE` textures `206 / 206`
  - `GDIE` meshes `42 / 42`
- videos: `66` `.vid` files inventoried
- language rows: `2571`
- deduplicated asset/media/language catalog entries before Goodies rows: `3817`
- Goodies catalog rows: `233`
  - `232` rows come from `goodie_00_res_PC.aya` through `goodie_231_res_PC.aya`
  - slot `232` is the retail displayable cutscene-33 mapping and has no separate `goodie_232_res_PC.aya`
  - current source-backed family counts: `149` artwork, `45` model, `34` video, `5` level
- total catalog entries with Goodies rows: `4050`

The Goodies catalog is built from real PC resource evidence, not sample art:

- `GDIE` texture/mesh references from the packed resource inventory,
- loose cutscene `.vid` rows from the video manifest,
- and authored `GOODIE_TEXT_*_TITLE` rows from the extracted language corpus for names such as `BE:A Unit-01 'Pulsar'` and `BE:A Unit-04S 'Sniper'`.

## 2026-05-07 Local Install Read-Only Check

Against the local Steam install at `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila`, a read-only inventory pass saw:

- `301` PC resource archives under `data\Resources`
- `232` `goodie_*_res_PC.aya` archives
- top-level chunk totals including `TEXT 18857`, `MESH 3492`, and `GDIE 232`
- packed reference resolution:
  - `TEXT` texture refs: `601 / 601`
  - reference mesh refs: `209 / 209`
  - `GDIE` texture refs: `206 / 206`
  - `GDIE` mesh refs: `42 / 42`
- `GDIE` family counts: `149` texture-only, `45` texture+mesh, `38` metadata-only

A full private export then proved the current backend can extract the supported asset lanes from the real install:

- loose textures: `847 / 847`
- loose meshes: `213 / 213`
- embedded mesh bodies: `139 / 139`
- language corpus: `2571` merged rows across six language files
- videos: `66` Bink `.vid` files inventoried
- generated catalog rows: `4050`
- model rows with readable metadata and wireframe preview data: `352 / 352`
- model rows with readable FBX material nodes: `352 / 352`
- model rows with readable FBX texture-binding nodes: `352 / 352`
- model rows with at least one FBX texture filename resolved back to a catalog texture row: `352 / 352`
- model rows without catalog-matched FBX texture filenames: `0 / 352`
- catalog-matched FBX texture binding files: `1,268`
- model rows with all real texture refs represented by texture catalog rows after excluding template/default FBX placeholders: `352 / 352`
- model rows with one or more real texture refs not represented by texture catalog rows: `0 / 352`
- unique model texture references with local mesh-texture sidecar coverage: `213 / 213`
- unique model texture references not represented by texture catalog rows after export-name/compact matching: `0`
- model rows with readable FBX UV mapping/reference modes: `352 / 352` (`ByPolygonVertex` / `IndexToDirect`)
- model rows with readable FBX normal mapping/reference modes: `352 / 352` (`ByPolygonVertex` / `Direct`)
- model rows with readable FBX vertex-color layers in the current export corpus: `0 / 352`

Raw manifests, exported assets, logs, and paths stayed under ignored `subagents/asset-full-install-2026-05-07/`. This confirms the current counts are based on the installed PC resources and that the supported texture/model export lanes complete successfully. It still does not prove final textured or animated in-app 3D rendering.

## Current Viewer Truth

The current WinUI Asset Library is catalog-backed by real local extraction, but its rendering surface is intentionally bounded:

- texture rows and artwork Goodies show exported PNG previews,
- model rows and model Goodies show metadata plus a lightweight FBX-derived wireframe geometry preview,
- video Goodies hand off to catalog-linked Media/video rows,
- level Goodies remain unlock/status metadata rows without a known local visual preview route.

The model path is not yet a full textured or animated native 3D renderer. It now records static normal counts, normal mapping/reference modes, UV coordinate/index counts, UV mapping/reference modes, vertex-color layer metadata when present, material-layer assignment counts, material mapping/reference modes, object/property connection counts, and readable texture-to-material slot/property names from binary FBX exports. It does not claim material-to-texture correctness, normal visual correctness, skeleton, animation, lighting, or in-game camera fidelity.

`release/readiness/model_material_texture_binding_coverage_2026-05-07.md` adds static FBX material/texture-binding coverage: all 352 current model rows have readable material and texture-binding nodes. This improves renderer-readiness evidence but still stops short of proving textured native rendering.

The same report now records the first catalog-resolution bridge for model textures: the FBX reader can extract sanitized texture file names and 352 of 352 model rows have at least one binding that resolves back to a generated catalog texture row. Compact normalization handles spacing/case variants such as `DeadTree01_Bark.png` versus catalog `dead tree 01_bark`. This still is not a claim of full textured rendering because exporter `default*.png` placeholders remain present beside real matches.

`release/readiness/model_texture_linkage_probe_2026-05-08.md` adds the mesh-sidecar bridge: all 213 unique checked real model texture references resolve to local mesh-texture sidecar files and texture catalog rows after excluding template/default FBX placeholders and matching catalog export filenames/compact variants. `release/readiness/winui_model_texture_catalog_coverage_2026-05-08.md` adds the AppCore coverage split that WinUI can use to keep direct-catalog rows separate from sidecar-needed rows; `release/readiness/winui_model_texture_placeholder_filter_2026-05-08.md` updates the current full-install result to `352/352` model rows with all real refs catalog-mapped and `0` sidecar-needed rows. `release/readiness/winui_model_uv_mapping_metadata_2026-05-08.md` records that AppCore and WinUI now surface binary FBX UV coordinate/index counts as static metadata. `release/readiness/winui_model_uv_mapping_modes_2026-05-08.md` records texture-coordinate assignment semantics for the current full-install export corpus: `352/352` rows report UV mapping mode `ByPolygonVertex` and reference mode `IndexToDirect`. `release/readiness/winui_model_normal_mapping_modes_2026-05-08.md` records normal assignment semantics for the same corpus: `352/352` rows report normal mapping mode `ByPolygonVertex`, reference mode `Direct`, and no normal-index arrays. `release/readiness/winui_model_vertex_color_metadata_2026-05-08.md` records that AppCore now exposes FBX vertex-color layers when present and that the current full-install export corpus reports `0/352` rows with vertex colors. `release/readiness/winui_model_material_assignment_metadata_2026-05-08.md` records binary FBX material-layer and material-assignment index counts. `release/readiness/winui_model_connection_metadata_2026-05-08.md` records binary FBX object/property connection counts and texture-to-material connection counts. `release/readiness/winui_model_connection_slot_metadata_2026-05-08.md` records readable texture-to-material slot/property names from FBX OP connections. `release/readiness/winui_model_slot_coverage_summary_2026-05-08.md` records aggregate material-slot coverage in AppCore/WinUI and a private full-install UIA breadth smoke asserting `352/352 model rows report material slots`; `release/readiness/winui_model_slot_host_diagnostic_2026-05-08.md` adds the read-only AppCore host diagnostic proof for the same full-install result with slot name `DiffuseColor`. `release/readiness/winui_model_material_mapping_modes_2026-05-08.md` records static material assignment semantics for the current full-install export corpus: `352/352` rows report mapping mode `ByPolygon` and reference mode `IndexToDirect`. `release/readiness/winui_model_sidecar_texture_visual_smoke_2026-05-08.md` proves the sidecar fallback path through a generated fixture catalog, not because the current full-install catalog lacks direct matches. This is still static extracted-texture and model metadata proof, not native textured 3D rendering or runtime model-viewer proof.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportPlanService.cs` now converts the same catalog, FBX metadata, direct catalog texture links, and local mesh-texture sidecar resolution into a typed material import readiness plan for active WinUI/AppCore tooling. The WinUI Asset Library coverage summary consumes the aggregate plan counts for readable texture binding files, catalog-resolved bindings, sidecar-resolved catalog misses, and unresolved material-import bindings. `OnslaughtCareerEditor.AppCore.Host inspect-asset-material-import-plan <catalog.json-or-directory>` exposes the same plan as a read-only, public-safe JSON diagnostic for agents and tooling.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportManifestService.cs` adds the next active-lane handoff format: a sanitized per-model/per-texture-binding manifest with resolution kind `catalog`, `sidecar`, or `unresolved`. `OnslaughtCareerEditor.AppCore.Host export-asset-material-import-manifest <catalog.json-or-directory>` and `OnslaughtCareerEditor.Cli --asset-material-import-manifest <catalog.json-or-directory> [--fail-on-unresolved-material-bindings]` expose the manifest without full local paths or private asset payloads. Current copied-corpus smoke reports `352 / 352` model rows ready, `1,268 / 1,268` texture bindings catalog-resolved, `0` sidecar-resolved, and `0` unresolved. This advances rebuild/tooling consumption of the static asset contracts; it is not real importer execution, textured native rendering, animation, lighting, runtime model-viewer behavior, or parity proof.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportDryRunPlanService.cs` consumes that manifest into deterministic relative model/texture operations for active AppCore/AppCore.Host/C# CLI tooling. `OnslaughtCareerEditor.AppCore.Host plan-asset-material-import-dry-run <catalog.json-or-directory>` and `OnslaughtCareerEditor.Cli --asset-material-import-dry-run-plan <catalog.json-or-directory> [--fail-on-unresolved-material-bindings]` expose the same read-only dry-run contract. The WinUI Asset Library coverage summary now displays the same dry-run readiness counts after catalog load. Current copied-corpus smoke reports `352 / 352` model operations ready, `1,268 / 1,268` texture operations catalog-resolved, `0` sidecar-resolved, `0` unresolved, and CLI unresolved gate PASS; focused native UIA proof validates the summary text while cycling representative texture, loose-mesh, embedded-mesh, and Goodie rows. This proves the catalog/FBX texture-binding evidence can be consumed into a rebuild/import package plan with relative destinations only and surfaced in the active Windows product; it is not asset copying, real importer execution, Godot work, native textured rendering, animation, lighting, runtime model-viewer behavior, rebuild parity, or no-noticeable-difference parity.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportPackagePlanService.cs` adds the next read-only active-lane consumer: a package plan with package-relative model and texture file entries, deduplicated texture references, and blocked-model reasons for missing exports, missing metadata, or unresolved texture bindings. `OnslaughtCareerEditor.AppCore.Host plan-asset-material-import-package <catalog.json-or-directory>` and `OnslaughtCareerEditor.Cli --asset-material-import-package-plan <catalog.json-or-directory> [--fail-on-unresolved-material-bindings]` expose the package plan. Current copied-corpus smoke reports `352 / 352` model package operations ready, `1,268 / 1,268` texture references resolved, `0` unresolved texture references, `352` model package files, `213` unique texture package files, `565` total package files, and CLI gate PASS. This proves deterministic package-relative planning only; it is not asset copying, real importer execution, Godot work, native textured rendering, animation, lighting, runtime model-viewer behavior, rebuild parity, or no-noticeable-difference parity.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageMaterializationService.cs` adds the guarded app-owned output step. `Preflight` checks the same package-relative destinations and internal source resolution without creating the output root. `Materialize` copies only ready model/texture package files into the caller-supplied output root, writes public-safe relative `material-package-manifest.v1.json` package metadata plus model-to-texture graph rows, a `material-package-work-order.v1.json` importer/rebuild task sidecar, and a `material-package-importer-dry-run.v1.json` adapter sidecar, omits raw source paths from JSON, and refuses casual copy execution through AppCore.Host/C# CLI unless `--arm-private-asset-output "MATERIALIZE ASSET MATERIAL PACKAGE"` is supplied. `OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageInspectionService.cs`, AppCore.Host `inspect-asset-material-package <package-output-directory>`, and C# CLI `--asset-material-package-inspect <package-output-directory>` validate the materialized package manifest, package-relative payload files, and graph-row path safety without mutating anything. `OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageWorkOrderService.cs`, AppCore.Host `build-asset-material-package-work-order <package-output-directory>`, and C# CLI `--asset-material-package-work-order <package-output-directory>` convert the validated manifest graph into package-relative importer/rebuild task rows; the same service also exposes sidecar validation through AppCore.Host `validate-asset-material-package-work-order-sidecar <package-output-directory>` and C# CLI `--asset-material-package-work-order-sidecar-validate <package-output-directory>`, which reads the saved work-order sidecar and rejects stale or path-leaking sidecars by comparing against a fresh package-relative work-order build. `OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageImporterDryRunService.cs` now exposes saved dry-run sidecar validation through AppCore.Host `validate-asset-material-package-importer-dry-run-sidecar <package-output-directory>` and C# CLI `--asset-material-package-importer-dry-run-sidecar-validate <package-output-directory>`, which rejects stale or path-leaking adapter sidecars by comparing `material-package-importer-dry-run.v1.json` against a fresh package-relative dry-run build. Current copied-corpus smoke preflights `565` package files with no output root created, then armed Host copy writes `565` payload files plus manifest, work-order, and importer dry-run sidecars under ignored `subagents/` output (`352` model files and `213` texture files); CLI preflight plans `565` files, wrong-arm copy exits non-zero without creating output, Host/CLI read-only package inspection reports manifest/payload status `ok` with `352` model graph rows and `1,268` texture-reference rows, Host/CLI read-only package work-order output reports `352` ready model tasks plus `1,268` ready texture-reference tasks, Host/CLI read-only work-order sidecar validation proves the materialized sidecar matches a fresh package-relative work-order build, Host/CLI read-only importer dry-run output reports `1,620` ready adapter rows, and Host/CLI read-only importer dry-run sidecar validation proves the materialized adapter sidecar matches a fresh package-relative adapter build. This proves app-owned material package file output, manifest-consumer validation, package-relative work-order derivation, durable work-order/importer-dry-run sidecar emission, and stale-sidecar rejection from the copied-corpus catalog; it is not Godot work, real importer execution, native textured rendering, animation, lighting, runtime model-viewer behavior, rebuild parity, or no-noticeable-difference parity.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageImporterBatchService.cs` and `OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageImporterDryRunService.cs` are the next active-lane consumer contracts. The batch service refuses to emit importer batch rows unless `material-package-work-order.v1.json` validates against the current package manifest/payloads, then flattens the package-relative work order into model and texture task rows for future importer/rebuild tooling. The dry-run service consumes the validated batch into adapter rows with stable package-relative source and adapter paths, and its saved-sidecar validator refuses stale or path-leaking `material-package-importer-dry-run.v1.json` payloads before downstream importer/rebuild tooling can trust them. AppCore.Host `build-asset-material-package-importer-batch <package-output-directory>` / `build-asset-material-package-importer-dry-run <package-output-directory>` / `validate-asset-material-package-importer-dry-run-sidecar <package-output-directory>` and C# CLI `--asset-material-package-importer-batch <package-output-directory>` / `--asset-material-package-importer-dry-run <package-output-directory>` / `--asset-material-package-importer-dry-run-sidecar-validate <package-output-directory>` expose the same read-only batch, dry-run, and saved-sidecar validation contracts. Current copied-corpus smoke reports `1,620 / 1,620` ready flat task rows (`352` model tasks and `1,268` texture tasks), `1,620 / 1,620` ready adapter rows, and dry-run sidecar validation with `dryRunMatchesFreshBuild=true`, with no package-root or catalog-source path leaks. This advances the handoff from static asset evidence to active importer/rebuild tooling input; it is not real importer execution, generated runtime assets, native textured rendering, Godot work, rebuild parity, or no-noticeable-difference parity.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageImporterInputService.cs` is the first active-lane file-staging consumer after dry-run validation. It requires `material-package-importer-dry-run.v1.json` to validate against a fresh package-relative adapter build, then preflights or stages package-local `importer-input/` files and writes `material-package-importer-input.v1.json` without source paths or hashes. AppCore.Host `materialize-asset-material-package-importer-input <package-output-directory> [--preflight] [--arm-private-asset-output "MATERIALIZE ASSET MATERIAL PACKAGE"]` and C# CLI `--asset-material-package-importer-input-materialize <package-output-directory> [--asset-material-package-preflight] [--arm-private-asset-output "MATERIALIZE ASSET MATERIAL PACKAGE"]` expose the same guarded contract. Current copied-corpus smoke reports `565` unique staged files for `1,620` adapter rows, `1,055` duplicate rows resolved as planned/existing copies, `0` missing source files, `0` unsafe paths, `0` existing hash mismatches, stable post-stage package inspection with `extraPayloadFiles=0`, Host wrong-arm rejection, and idempotent CLI copy over the already staged input tree. This converts static package evidence into app-owned importer input files for future importer/rebuild tooling; it is not Godot work, real importer execution, generated runtime assets, native textured rendering, animation, lighting, rebuild parity, or no-noticeable-difference parity.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageImporterInputPlanService.cs` is the first read-only consumer of the staged `importer-input/` tree. It reads `material-package-importer-input.v1.json`, revalidates the source dry-run sidecar, checks package-relative staged paths, parses staged FBX files through the AppCore FBX summary reader, checks staged PNG headers through the shared PNG header reader, and emits concrete `import-model` and `bind-texture` consumer jobs without source paths, hashes, shell commands, runtime launch, renderer work, Godot, or real importer execution. AppCore.Host `build-asset-material-package-importer-input-plan <package-output-directory>` and C# CLI `--asset-material-package-importer-input-plan <package-output-directory>` expose the plan. Current copied-corpus smoke reports `1,620 / 1,620` ready consumer jobs (`352` model imports and `1,268` texture binds), `565` existing unique staged files, `352` readable FBX model rows with geometry, `1,268` readable PNG binding rows over `213` unique texture files, `0` missing staged files, `0` unsafe input paths, and no package-root/source-path/hash leaks. This advances the handoff from static asset evidence into active importer/rebuild job planning while still remaining short of real importer execution, native textured rendering, runtime model-viewer behavior, rebuild parity, or no-noticeable-difference parity.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageRebuildPreviewService.cs` is the first guarded adapter-output consumer after the staged-input plan. It consumes the completed importer-input plan, re-reads staged FBX preview geometry, and writes app-owned `rebuild-preview/` OBJ wireframe files plus per-model binding sidecars and `material-package-rebuild-preview.v1.json` when armed through AppCore.Host, the C# CLI, or the WinUI package action. Current copied-corpus smoke reports `352 / 352` model preview rows ready, `352` OBJ wireframes, `352` binding sidecars, and `1,268` texture-binding rows, with package inspection still reporting `extraPayloadFiles=0` because generated adapter outputs are tracked separately from original package payloads. This is deterministic rebuild-preview artifact output for clean-room tooling; it is not full mesh conversion, textured native rendering, animation, lighting, Godot work, runtime model-viewer behavior, rebuild parity, or no-noticeable-difference parity.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageRebuildSceneService.cs` is the next active-lane scene-contract consumer after rebuild-preview output. It requires completed package-local `rebuild-preview/` OBJ files and binding sidecars, re-reads the staged FBX model input, parses the OBJ bounds, and writes package-local `rebuild-scene/models/*.scene.json` contracts plus `material-package-rebuild-scene.v1.json` when armed through AppCore.Host, the C# CLI, or the WinUI package action. Each scene contract records package-relative OBJ, binding-sidecar, and model-input paths; OBJ-derived vertex/edge/bounds rows; FBX mesh format/version, vertex, polygon-index, normal, UV, vertex-color, material, connection, and texture-to-material slot facts; and package-relative texture binding rows. Current copied-corpus smoke reports `352 / 352` scene contracts ready, `352` scene JSON files, `1,268` texture-binding rows, positive FBX vertex/polygon-index/UV/normal counts, positive texture-to-material connection rows, default/preflight no-write behavior, wrong-arm rejection, idempotent CLI materialization, no package-root/catalog-source/hash leaks, and package inspection still stable with `extraPayloadFiles=0`. This is package-local scene/mesh/material contract output for future importer/rebuild tooling; it is not Godot work, real importer execution, native textured rendering, animation, lighting, runtime model-viewer behavior, rebuild parity, or no-noticeable-difference parity.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageRebuildMeshService.cs` is the next guarded mesh/material artifact consumer after rebuild-scene output. It requires completed package-local `rebuild-scene/models/*.scene.json` contracts, revalidates the scene contract and staged FBX model input, extracts face-bearing mesh payload arrays from the FBX summary reader, and writes deterministic package-local `rebuild-mesh/models/*.mesh.obj` plus paired `.mesh.mtl` files and `material-package-rebuild-mesh.v1.json` when armed through AppCore.Host, the C# CLI, or the WinUI package action. Current copied-corpus smoke reports `352 / 352` mesh rows ready, `352` OBJ mesh files, `352` MTL files, `376,602` vertices, `275,514` faces, `826,542` normals, `826,542` UV rows, `8,448` material rows, `1,268` texture-binding rows, complete mesh payload rows `352 / 352`, default/preflight no-write behavior, wrong-arm rejection, idempotent CLI materialization, no package-root/catalog-source/hash leaks, and package inspection still stable with `extraPayloadFiles=0`. This advances the asset lane from static scene contracts into concrete package-local mesh/material files for active importer/converter/rebuild tooling; it is not Godot work, real importer execution, native textured rendering, animation, lighting, runtime model-viewer behavior, rebuild parity, or no-noticeable-difference parity.

`OnslaughtCareerEditor.AppCore/AssetMaterialImportPackageRebuildMeshImportService.cs` is the active consumer-validation layer after rebuild-mesh output. It reads `material-package-rebuild-mesh.v1.json`, parses each generated package-local `.mesh.obj` and paired `.mesh.mtl`, validates OBJ vertex/face/normal/UV counts against the source mesh manifest, validates MTL material counts and texture paths, rejects undefined material uses, unsafe paths, missing staged textures, and count mismatches, and writes `material-package-rebuild-mesh-import.v1.json` when armed through AppCore.Host, the C# CLI, or the WinUI package action. Current copied-corpus smoke reports `352 / 352` import rows ready, `352` OBJ files parsed, `352` MTL files parsed, `376,602` vertices, `275,514` faces, `826,542` normals, `826,542` UV rows, `8,448` material rows, `275,514` face-material uses, `1,268` textured material rows, `1,268` texture references, `0` missing textures, `0` count mismatches, `0` undefined material uses, `0` unsafe paths, default/preflight no-write behavior, wrong-arm rejection, no package-root/catalog-source/hash leaks, and package inspection still stable with `extraPayloadFiles=0`. This proves the generated package-local OBJ/MTL mesh output is internally consumable by active importer/converter/rebuild tooling; it is not Godot work, real importer execution, native textured rendering, animation, lighting, runtime model-viewer behavior, rebuild parity, or no-noticeable-difference parity.

The WinUI Asset Library selected-model detail panel now surfaces that package plan beside model metadata and texture-link evidence. Focused real-catalog UIA proof validates that representative loose and embedded model selections show `Material package plan: ready`, `model destination models/`, resolved texture-reference text, and sample package-relative `textures/catalog/` destinations. The same panel now exposes a package-output action that materializes the AppCore package to a deterministic LocalAppData app-owned folder, runs read-only manifest graph inspection, work-order derivation, validated importer-batch generation, importer dry-run generation, saved importer dry-run sidecar validation, importer-input staging, importer-input planning, rebuild-preview materialization, rebuild-scene contract materialization, rebuild-mesh OBJ/MTL materialization, and rebuild-mesh import validation after the write, reports graph-row status, ready model/texture-reference task counts, flat importer-batch readiness counts, importer dry-run readiness counts, saved dry-run sidecar validation status, sidecar write status, importer-input readiness, importer-input-plan readiness, rebuild-preview readiness, rebuild-scene contract readiness, rebuild-mesh readiness, and rebuild-mesh import readiness in the selected-model detail panel, and offers open/copy-path controls. Existing package folders are also re-inspected for importer-batch, importer dry-run, dry-run sidecar validation, importer-input, importer-input-plan, rebuild-preview, rebuild-scene, rebuild-mesh, and rebuild-mesh import readiness when the catalog reloads. This makes the package/rebuild-mesh output inspectable and locally usable in the primary Windows product without claiming real importer execution, native textured rendering, runtime model-viewer behavior, rebuild parity, or no-noticeable-difference parity.

Representative static renderer-spike targets from the current full-export probe include `arachnid.msh` and `be_trans.msh` as all-catalog-mapped rows with local sidecar texture coverage. These names are sanitized catalog labels, not private export paths.

Goodies model-viewer alignment evidence in `release/readiness/goodies_model_viewer_alignment_2026-05-08.md` proves the source `GT_MESH` Goodie set, installed `GDAT` kind-1 archive set, and generated catalog Model Goodie set all contain the same 45 indices. Goodies model-viewer read-back evidence in `release/readiness/goodies_model_viewer_readback_2026-05-08.md` adds a source-to-retail decompile guard for mesh deserialization and mesh interaction/update branches. Mesh renderer read-back evidence in `release/readiness/mesh_renderer_readback_2026-05-08.md` adds a retail `CMeshRenderer__RenderMesh` dispatch guard for normal render-core, particle attachment, debug render, and default texture fallback context. Dynamic unit render read-back evidence in `release/readiness/dynamic_unit_render_readback_2026-05-08.md` adds unit-list traversal, collision-map owner traversal, projected-sprite, render-queue insertion, and distance/LOD gate coverage. This strengthens model Goodies provenance without claiming runtime model-viewer behavior or final textured WinUI rendering.

## Immediate Next Use

This backend is the right base for:

- the current WinUI Asset Library Goodies tab and future save-aware Goodies browser,
- a separate public-safe extractor release,
- or continued private RE without changing the command surface again.
