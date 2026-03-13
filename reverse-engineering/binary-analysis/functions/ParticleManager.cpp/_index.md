# ParticleManager.cpp Functions

> Source File: ParticleManager.cpp | Binary: BEA.exe
> Debug Path: 0x00630e60

## Overview

Particle/effects system implementation. CParticleManager handles visual effects like explosions, smoke, and trails with LOD-based culling for performance.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004caed0 | CParticleManager__SetParticleResource (TODO) | Set effect resource | ~100 bytes |
| 0x004cb0e0 | CParticleManager__Init (TODO) | Initialize particle pool | ~200 bytes |
| 0x004cb3d0 | CParticleManager__CreateEffect (TODO) | Create new effect | ~300 bytes |
| 0x004cb5c0 | CParticleManager__AllocateParticle (TODO) | Allocate with LOD | ~400 bytes |

## Related Functions (No Debug Ref)

| Address | Name | Purpose |
|---------|------|---------|
| 0x004cae50 | CParticle__Destroy | Recycle particle |
| 0x004caf30 | CParticleManager__ClearParticleOwnerBacklinks | Clears per-handle owner activity/backlink fields |
| 0x004cb050 | CParticleManager__RemoveFromGlobalList | Remove from list |
| 0x004cb080 | CParticleManager__PruneDeadOwnerLinks | Nulls dead owner links from manager chain |
| 0x004cb1b0 | CParticleManager__Shutdown | Destructor |
| 0x004cb210 | CParticleManager__Update | Main update loop |
| 0x004cb300 | CParticleManager__InterpolatePositions | Smooth rendering |
| 0x004cb920 | CParticleManager__UpdateParticleAndRecycleIfDead | Per-particle update + recycle path |
| 0x004cbca0 | CParticleManager__UpdateParticles | Physics update |
| 0x004cbc60 | CParticleManager__UpdateRenderNodesAndResetState | Render-node update pass + render-state restore |
| 0x004cbe30 | CParticleManager__PruneDeadParticles | Remove dead |
| 0x004cbff0 | CParticleManager__DestroyParticleList | List-destruction helper used by shutdown/release paths |
| 0x004caf60 | CParticleManager__CleanupHandles | Clean orphans |

## Headless Semantic Wave120 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x004caf30 | CParticleManager__ClearParticleOwnerBacklinks | Iterates effect-handle chain and clears owner activity/backlink fields (`+0xa4/+0xa8`). |
| 0x004cb080 | CParticleManager__PruneDeadOwnerLinks | Walks manager list and nulls owner pointers whose linked activity flag has cleared. |
| 0x004cbc60 | CParticleManager__UpdateRenderNodesAndResetState | Runs render-node update callback on type `0xb` entries and restores render-state slot `0xf`. |
| 0x004cbff0 | CParticleManager__DestroyParticleList | Owner-corrected helper that repeatedly destroys head list nodes until empty. |
| 0x004cb920 | CParticleManager__UpdateParticleAndRecycleIfDead | Updates one particle, refreshes owner backlinks, and recycles into free-list when death state is set. |

## Headless Semantic Wave121 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x004cba30 | CParticleManager__ProjectPointToTerrainWithRadiusClamp | Projects a point to terrain/shadow height and writes clamped output position when inside radius threshold. |
| 0x004cba90 | CParticleManager__ComputeMinCameraDistanceSqForParticle | Returns minimum camera-distance-squared metric for a particle (including attachment offset), with large fallback when cameras are unavailable. |

## Key Observations

- **512 particles per pool** - Each 216 bytes (0xD8)
- **Pool size** - 110,596 bytes (0x1B004)
- **LOD system** - Based on particle load:
  - Type 1,11: Skip if load > 700
  - Type 2: Skip if load > 900
  - Type 8,13: Skip if load > 800
- **47 callers** - CreateEffect is most-used function
- **High priority bypass** - LOD culling can be bypassed

## LOD Thresholds

| Effect Type | Skip Threshold | Probabilistic Range |
|-------------|----------------|---------------------|
| 1, 11 | > 700 | 400-700 |
| 2 | > 900 | 800-900 |
| 8, 13 | > 800 | 600-800 |

## Particle Structure (216 bytes / 0xD8)

| Offset | Field | Notes |
|--------|-------|-------|
| 0x00 | mPrev | Linked list |
| 0x04 | mNext | Linked list |
| 0x08-0x34 | mTransform | 4x3 matrix |
| 0x38-0x44 | mPosition | x,y,z,w |
| 0x48-0x50 | mVelocity | x,y,z |
| 0x58 | mHandle | Effect handle |
| 0x5c | mType | Particle type |
| 0x60 | mLifetime | Float (default 100.0) |
| 0x64 | mDeathFlag | Should die |
| 0x88 | mResource | Resource pointer |

## Effect Handle Structure (184 bytes / 0xB8)

| Offset | Field | Notes |
|--------|-------|-------|
| 0x00-0x0F | mPosition | Current position |
| 0x10-0x4F | mTransform | Transform matrix |
| 0x48 | mScale | Default 10000.0 |
| 0xA4 | mActivityFlag | Active flag |
| 0xA8 | mParticle | Owning particle |
| 0xAC | mLooping | -1.0 or 0 |
| 0xB0 | mNextHandle | Linked list |
| 0xB4 | mState | 1, 2, or 3 |

## Global Variables

| Address | Name | Notes |
|---------|------|-------|
| 0x0082b3e4 | g_EffectHandleList | Handle list head |
| 0x0082b3e8 | g_ParticleManagerList | Manager list head |
| 0x0082b3ec | g_ParticleManagerCount | Active managers |
| 0x0089ce58 | g_ParticlesDisabled | System disable flag |

## Related Files

- BattleEngine.cpp - Creates combat effects
- Unit.cpp - Unit destruction effects

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
