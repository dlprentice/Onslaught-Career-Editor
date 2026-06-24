# Ghidra Mesh / Motion / World / Particle Static Review Wave905 Readiness Note

Status: complete static review evidence
Date: 2026-05-26
Scope: `mesh-motion-world-particle-static-review-wave905`

Wave905 is a read-only post-100 system review. It makes no Ghidra metadata mutation, no executable-byte change, no save mutation, and no BEA launch. The wave records a `static-coherent mesh/motion/world/particle core` after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`.

Authority boundary: Stuart's source and AYAResourceExtractor are helpful references, not proof for the Steam retail binary or original PC resource corpus. The evidence below is grounded in the loaded Ghidra database and current local retail extraction manifests.

Evidence summary:

- Selected function rows: `506` rows across `41` families, all commented and clean-signature.
- Large family anchors: `CMeshPart` `54`, `CMesh` `40`, `CWorld` `38`, `CWorldPhysicsManager` `32`, `CThing` `28`, `CParticleManager` `23`, `CMeshCollisionVolume` `21`.
- Representative functions: `CThing__InitRenderThingFromInitMeshName`, `CMesh__LoadByNameWithStatus`, `CMeshPart__PopulatePoseCacheRecursive`, `CWorld__InitOccupancyBitplanes`, `CWorldPhysicsManager__CreateThingByType`, `CParticleManager__Update`, `CParticleSet__LoadFromArchive`, and `CParticleDescriptor__Load`.
- Mesh/resource bridge: `213/213` loose meshes, `139/139` embedded packed mesh bodies, `352/352` model rows with readable material/texture-binding metadata, and `213/213` model texture sidecar refs covered.
- Verified read-only Ghidra backup: `G:\GhidraBackups\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`, `19` files, `173247367` bytes, `DiffCount=0`.

What this proves:

- The selected mesh/motion/world/particle owner-family rows are closed under the current function-quality proxy.
- The public docs now review thing/render initialization, mesh load/lifetime, mesh-part geometry/material/pose-cache paths, mesh collision, world occupancy, physics-manager factory/list resolution, particle descriptor/set/manager paths, and mesh asset-count evidence as one static system slice.
- The claim is static coherence, not runtime behavior or visual parity.

What remains unproven:

- Exact object layouts.
- Runtime collision, physics, animation, render, particle, and world-occupancy behavior.
- Runtime mesh/particle visual parity.
- BEA patch behavior.
- Clean-room rebuild parity.
