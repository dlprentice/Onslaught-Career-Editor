# CBattleEngine__Init

> Address: 0x00404dd0 | Source: `references/Onslaught/BattleEngine.cpp:63`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partial (decompiler matches source intent)

## Purpose

Massive initialization function (~2700 LOC in source) that sets up the CBattleEngine combat/physics system. Initializes:

- Sound effects (engine, energy, missiles, targeting, hydraulics)
- Particle effects (thruster, engine, afterburner, ground effects)
- Walker and Jet subsystems via CBattleEngineWalkerPart and CBattleEngineJetPart
- Configuration (life, energy, allegiance-based mesh selection)
- Mesh models (m_be1.msh, m_be2.msh or f_be1.msh, f_be2.msh based on faction)
- Weapon systems (leg motion controller)
- Physics parameters (acceleration, friction, zoom, augmentation)
- Collision shape and constraints
- Render target for Cockpit visibility
- Parent Unit initialization via CUnit__Init

## Signature

```c
// thiscall - ecx = CBattleEngine*
void CBattleEngine::Init(CInitThing* init);
```

## Key Observations

### Sound Effect Initialization
- Loads 11 named sound effects from SOUND manager
- Stored in member variables: mInFlightSound, mLandingSound, mTakeOffSound, mHealthLowSound, mEnergyLowSound, mStrafeSound, mTargetLockedSound, mIncomingMissileSound, mAutoAimSound, mBattleEngineOnSound, mPneumaticSound

### Particle Effects
- Thruster, engine, afterburner effects via PARTICLE_SET manager
- Water and land ground effects (static members sWaterEffect, sLandEffect)

### Faction-Based Mesh Selection
- Checks `init->mAllegiance` to select mesh:
  - Muspell faction: m_be1.msh / m_be2.msh (male variant)
  - Other factions: f_be1.msh / f_be2.msh (female variant)
- Both meshes loaded and initialized via FUN_00516580

### Leg Motion Controller
- Loads "LegMotion" animation/controller via FUN_004aa630
- Allocates large motion controller structure (0xf0 bytes) if found
- Special handling for specific levels (0xe7, 0xe8, 0x14b, 0xdd, 0xde, 0x20c, 0x20b, 0x14c)

### Weapon System Setup
- Allocates physics object for weapons (0x20 bytes)
- Initializes max life and gravity (calls float GetMaxLife() and GetGravityMod())
- Calculates squared max life and gravity modifier

### Physics and Collision
- Initializes collision shape via SetCollisionShape()
- Sets collision handling flags via MassiveHackPutUsInRightMesh()
- Initializes various physics parameters (zoom, augmentation, stealth)

### Configuration Dependent Behavior
- Checks `init->mPlaneMode` to determine initial state (JET vs WALKER)
- Jet mode: mState=BATTLE_ENGINE_STATE_JET, mShields=0
- Walker mode: mState=BATTLE_ENGINE_STATE_WALKER, mShields=mEnergy
- Multiplayer vs single-player affects collision level (ECL_APPROX_GEOMETRY_SHAPES)

### Motor Parameters
- Stores physics data (velocity, acceleration, etc.) in member array (76 ints starting at offset 0xc6)
- Copies from parent Unit data structure
- Initializes 20 additional ints to default physics value

### Weapon Slots and Locks
- Initializes lock system (6 lock slots with target/data)
- Checks if weapon is locked via (param_1 + 0x2c) & 4 flag
- Connects to weapon subsystems

### Exception Handling
- Uses Windows SEH (__try/__finally pattern)
- Multiple exception unwinding points for allocations

## Binary Offsets (from ECX)
| Offset | Purpose |
|--------|---------|
| 0x15f | mJetPart |
| 0x15e | mWalkerPart |
| 0x12a | mConfiguration |
| 0x167-0x172 | Sound effect slots (11 sounds) |
| 0x185-0x187 | Particle effect slots (3 effects) |
| 0x180 | mConfigurationId |
| 0x3e-0x3f | Life/Energy from config |
| 0x98 | mState (WALKER=3, JET=2) |
| 0x40 | mShields |
| 0x1c | Leg motion controller |
| 0xc | Mesh 1 (m_be1/f_be1) |
| 0x17b | Mesh 2 (m_be2/f_be2) |
| 0x14a | Radar/targeting system |
| 0xae | Weapon controller |
| 0x149 | Cockpit visibility flag |

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Extremely large function - indicates complex initialization routine
- Multiple subsystem allocations suggest object composition pattern
- Faction/plane mode parameters suggest multiplayer vs single-player code paths

## Related Functions
- [CBattleEngine__UpdateWeaponEffect](CBattleEngine__UpdateWeaponEffect.md) - Weapon effect updates
- [CBattleEngine__AddProjectile](CBattleEngine__AddProjectile.md) - Projectile spawning
- CUnit__Init - Parent class initialization
- CBattleEngineWalkerPart - Walker-specific subsystem
- CBattleEngineJetPart - Jet-specific subsystem
