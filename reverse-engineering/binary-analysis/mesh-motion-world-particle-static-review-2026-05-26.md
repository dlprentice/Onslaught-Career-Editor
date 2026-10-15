# Mesh / Motion / World / Particle Static Review

Status: static-coherent system slice
Date: 2026-05-26
Scope: `mesh-motion-world-particle-static-review-wave905`

MissionScript object references connect to this world/thing evidence through
`missionscript-iscript-static-contract.md` and the Unit/BattleEngine spawn
anchors. These static links do not establish runtime world loading, object
identity, spawn behavior, visual output, or rebuild parity.

Wave905 reviews the mesh, motion, world, collision, and particle connector surface after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`. It ties object/render initialization, CMesh/CMeshPart geometry and pose-cache rows, world occupancy and physics-manager lists, mesh collision, particle manager/set/descriptor rows, and mesh asset bridge counts into one system classification.

Classification: `static-coherent mesh/motion/world/particle core`.

Source/extractor boundary: Stuart's source and AYAResourceExtractor remain useful architecture/tooling references, but the authority for this review is the Steam retail binary as loaded in Ghidra plus the current local retail resource/extraction evidence.

## Function-Family Surface

The Wave905 evidence snapshot covers `506` function rows across `41` selected owner families. Every selected row has a non-empty comment and a clean signature with no exact-`undefined` return and no `param_N` placeholders.

Representative family counts:

| Family | Rows |
| --- | ---: |
| `CMeshPart` | 54 |
| `CMesh` | 40 |
| `CWorld` | 38 |
| `CWorldPhysicsManager` | 32 |
| `CThing` | 28 |
| `CBattleEngineWalkerPart` | 27 |
| `CDXLandscape` | 27 |
| `CParticleManager` | 23 |
| `CBattleEngineJetPart` | 23 |
| `CMeshCollisionVolume` | 21 |

Representative anchors include `CThing__InitRenderThingFromInitMeshName`, `CThing__Render`, `CComplexThing__Init`, `CActor__GetRenderPos`, `CMesh__LoadByNameWithStatus`, `CMeshPart__PopulatePoseCacheRecursive`, `CMeshCollisionVolume__TestSweptSphereAgainstMeshPart`, `CMeshRenderer__RenderMesh`, `CDXMeshVB__BuildSkeletalVB`, `CWorld__InitOccupancyBitplanes`, `CWorldPhysicsManager__CreateThingByType`, `CParticleManager__Update`, `CParticleSet__LoadFromArchive`, `CParticleDescriptor__Load`, `DXParticleTexture__Render`, `CBattleEngineWalkerPart__Move`, and `CBattleEngineJetPart__Thrust`.

## Asset Bridge

Mesh/resource bridge counts remain public-safe count evidence:

| Metric | Value |
| --- | ---: |
| PC resource archives | 301 |
| `goodie_*_res_PC.aya` archives | 232 |
| Loose meshes exported | `213/213` |
| Embedded packed mesh bodies exported | `139/139` |
| Mesh refs resolved | `209/209` |
| Goodie mesh refs resolved | `42/42` |
| Model rows | 352 |
| Model rows with readable material metadata | `352/352` |
| Model rows with texture-binding metadata | `352/352` |
| Model rows with catalog-resolved texture binding | `352/352` |
| Model texture sidecar refs | `213/213` |

## Static Classification

- The selected mesh/motion/world/particle owner families have no remaining function-quality queue debt.
- The current static documentation connects thing/render initialization, mesh load/lifetime, mesh-part material/geometry/pose-cache paths, skeletal/static VB build paths, world occupancy bitplanes, physics-manager factory/list resolution, collision scans, particle resource/update/render-node paths, and mesh asset bridge counts.
- The verified read-only Ghidra backup for this review is `[maintainer-local-ghidra-backup-root]\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`.

## What Remains Separate

- Exact `CThing`, `CActor`, `CMesh`, `CMeshPart`, `CWorld`, `CWorldPhysicsManager`, and particle object layouts.
- Runtime collision, physics, animation, render, particle, and world-occupancy behavior.
- Runtime mesh/particle visual parity.
- BEA patch behavior.
- Rebuild parity.
