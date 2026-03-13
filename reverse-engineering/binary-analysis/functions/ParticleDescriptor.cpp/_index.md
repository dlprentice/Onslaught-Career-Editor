# ParticleDescriptor.cpp Functions

> Source File: ParticleDescriptor.cpp | Binary: BEA.exe
> Debug Path: 0x00630cd8

## Overview

Particle effect descriptor definitions. CParticleDescriptor defines the properties and behavior templates for particle effects (explosions, smoke, sparks, trails). Works closely with ParticleManager.cpp which spawns actual particle instances from these descriptors.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004c5410 | CParticleDescriptor__Update | Update particle effect state, position, transform | ~800 bytes |
| 0x004c5730 | CParticleDescriptor__Load | Load descriptor properties from data file | ~700 bytes |

## Unresolved Xrefs

Two additional xrefs to the debug path exist at addresses without defined functions:

| From Address | Context | Notes |
|--------------|---------|-------|
| 0x004c05cd | Inside undefined code region | Likely CParticle class method |
| 0x004c312d | Inside undefined code region | Likely CParticle class method |
| 0x005d4040 | Unwind@005d4040 | Exception handler for Update |

## Key Observations

- **Linked to ParticleManager** - Update calls CParticleManager__CreateEffect and CParticleManager__AllocateParticle
- **Memory allocation** - Uses OID__AllocObject for allocation with debug tracking (line 0x7e9 = 2025, line 0x83d = 2109)
- **Effect handle system** - Creates effect handles stored at offset 0x88 of particle
- **Position inheritance** - Can inherit position from parent particle at offset 0x58
- **Flag copying** - Copies flag at offset 0xB6 between particles (likely visibility/LOD flag)

## Descriptor Structure (Partial)

Based on Load function switch cases:

| Offset | Field | Case ID | Notes |
|--------|-------|---------|-------|
| 0x5c | mEffectType | 0x3f | Primary effect type |
| 0x60 | mSecondaryType | 0x1b | Secondary effect |
| 0x64 | mResource | 0x0b | Resource array |
| 0x68 | mResourceCount | 0x0d | Number of resources |
| 0x6c | mName | 0x10 | String name |
| 0x70 | mTextureName | 0x74 | Texture string |
| 0x74-0x7c | mColorStart | 0x6b | Start color (RGB?) |
| 0x7c-0x84 | mColorEnd | 0x6c | End color (RGB?) |
| 0x84-0x8c | mScaleStart | 0x6d | Start scale |
| 0x8c-0x94 | mScaleEnd | 0x6e | End scale |
| 0x94 | mLifetime | 0x6f | Effect duration |
| 0x98 | mSpawnRate | 0x70 | Particle spawn rate |
| 0x9c-0xa4 | mVelocity | 0x71 | Initial velocity |
| 0xa4-0xac | mAcceleration | 0x72 | Acceleration |
| 0xac-0xb4 | mRandomness | 0x73 | Random variation |
| 0xb4 | mGravity | 0x75 | Gravity multiplier |
| 0xb8 | mDrag | 0x76 | Air resistance |
| 0xbc-0xc4 | mRotation | 0x78 | Rotation params |
| 0xc4-0xcc | mRotationRate | 0x79 | Angular velocity |
| 0xcc-0xd4 | mSpin | 0x7a | Spin params |
| 0xd4-0xdc | mSpinRate | 0x7b | Spin velocity |
| 0xdc-0xe4 | mBlendMode | 0x77 | Blend/alpha mode |

## Update Function Analysis

The Update function (0x004c5410):
1. Copies visibility flag (0xB6) from parent to child particle
2. Calls virtual function at offset 0x30 on resource (position update?)
3. On first call (flag at 0x7E == 0), allocates effect handle
4. Iterates effect type list at offset 0x5C to create effects
5. Updates position by adding parent position to local offset
6. Copies transform matrix (12 floats) from source
7. If effect handle allocation fails, allocates fallback particle via AllocateParticle

## Related Files

- ParticleManager.cpp - Manages particle instances created from descriptors
- BattleEngine.cpp - Creates combat particle effects
- Unit.cpp - Unit destruction effects

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
