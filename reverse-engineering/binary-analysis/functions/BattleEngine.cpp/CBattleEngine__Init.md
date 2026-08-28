# CBattleEngine__Init

> Address: 0x00404dd0 | Source: `references/Onslaught/BattleEngine.cpp:63`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave 309 static Ghidra signature/comment correction)
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
void __thiscall CBattleEngine__Init(void * this, void * init);
```

Source-style interpretation remains `CBattleEngine::Init(CInitThing* init)`, but the saved retail Ghidra signature stays pointer-typed until concrete retail structure types are proven.

## 2026-08-19 byte contract

Independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
93 accepted HandleLocks through HandleAutoAim — not redone. Name
and source-intent text above is not rewritten. This is an
envelope, not a 710-instruction walk. Did not mill FUN_*. Did not
implement lock sets.

Incoming-ECX `thiscall`. First insn `push -1` (SEH cookie). One
`ret 0x4` at `0x004058f7`. Body `0x00404dd0`–`0x004058f9` is
2858 bytes, SHA-256
`44f563280d5c5748d2d09490113f4a5c27fa0d6c9e7d09a9abc8da0eece7dde0`
(PE bytes; not the C1-table Ghidra digest `fc848420…`). Capstone:
710 insns, 54 `E8`, 2 `E9`, 29 unique rel32 targets. Raw `0xE8`
byte count is 59 and is not the instruction count. The two `E9`s
are intra-body (`0x0040524f`, `0x00405302`) and are not named.
Neighbour table `CCockpit__VFunc_3_00405900` starts at
`0x00405900` after six `nop`s and is not rewritten. Preceding
table `FUN_00404d00` ends at `0x00404dc2` and is not rewritten.

Pinned prologue:

1. SEH frame (`push 0x005d1120` / `fs:[0]`), then
   `sub esp, 0x484`. `ebp = ecx`. `ebx = 0`.
2. Store 0 at `[ebp+0x5b0]`, then eleven `E8`
   `CSoundManager__GetEffectByName` `0x004e1910` with
   `ecx = 0x00896988`. First string `0x00623210`
   (`BE Engines(in-flight)`); EAX of that call lands at
   `[ebp+0x59c]`. Five `E8`
   `CParticleSet__FindByNameAndTrackLinkSlot` `0x004cd7a0`
   follow (thruster / engine / afterburner / water / land
   strings). Other of the 29 targets are counted, not
   contracted.
3. `esi = [esp+0x4a0]` (this frame's init pointer).
   `[esi+0x3c0]` is copied to `[ebp+0x600]`, then `E8`
   `CBattleEngine__UpdateConfiguration` `0x0040c650` at
   `0x00404f7e`.
4. Walker: `push ebp` / `E8` `CBattleEngineWalkerPart__ctor`
   `0x00412bc0` at `0x00404faa`; EAX stored at
   `[ebp+0x578]`. Jet: `E8` `CBattleEngineJetPart__ctor`
   `0x00410210` at `0x00404ff1`; EAX stored at
   `[ebp+0x57c]`. Those are the same part slots HandleLocks
   already uses. The older `0x15e`/`0x15f` rows below are
   not PE.
5. `SetReader(0)` onto `[ebp+0x4c8]` then `[ebp+0x4cc]`
   (same pair CalcUnitOverCrossHair already pins).
6. `cmp [esi+0x3c4], ebx` at `0x004050fc`: nonzero writes
   `[ebp+0x260]=3` and `[ebp+0x100]=0`; zero writes
   `[ebp+0x260]=2` and `[ebp+0x100]=[ebp+0xfc]`. This is
   the already-closed JET=3 / WALKER=2 polarity. The older
   `mState (WALKER=3, JET=2)` row below is not PE.
7. Already-pinned tail: `E8` `CEventManager__AddEvent_AtTime`
   `0x0044b370` at `0x004058b2`, then `E8`
   `CBattleEngine__HandleAutoAim` `0x0040b6d0` at
   `0x004058ba`. `CUnit__Init` `0x004f86d0` at
   `0x004054c6` and `CCockpit__ctor` `0x004244b0` at
   `0x004055dc` are counted, not contracted. No
   `[ebp+0x294]` / `[ebp+0x2a4]` store in this body.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`d0 4d 40 00`: file `0x001d89e8` / VA `0x005d89e8` (vtable
slot 9, `+0x24` from the `CBattleEngine` vtable base
`0x005d89c4` named by HandleEvent). Neighbouring dwords are
**not** this proof.

Source architecture (not proof): `CBattleEngine::Init`
`BattleEngine.cpp:63-353`. `HandleAutoAim(NULL)` is the last
source statement; retail `ret 0x4` matches one stack arg.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00004dd0` is not `6a ff`, **or**
`0x00004dd2` is not `68 20 11 5d 00`, **or** `0x00004df0` is
not `8b e9`, **or** `0x00004e03` is not `e8 08 cb 0d 00`,
**or** `0x00005104` is not
`c7 85 60 02 00 00 03 00 00 00`, **or** `0x000058ba` is not
`e8 11 5e 00 00`, **or** `0x000058f7` is not `c2 04 00`,
**or** body SHA-256 is not `44f56328…dde0`, **or**
`tools/call_xref_scan.py` on `0x00404dd0` is not empty, **or**
`0x001d89e8` is not `d0 4d 40 00`, **or** a second encoding
of that imm exists.

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

The 2026-08-19 PE contract above supersedes the `mJetPart` /
`mWalkerPart` slots (retail `this+0x57c` / `+0x578`) and the
`mState` polarity (retail `+0x260` 3=jet / 2=walker). The
`0x15e`/`0x15f` and `WALKER=3` rows are historical Ghidra-index
text, not PE.

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
- Wave 309 read-back hardened the saved signature to `void __thiscall CBattleEngine__Init(void * this, void * init)` and recorded the `ret 0x4` CBattleEngineInitThing-like argument, walker/jet construction, and stealth-adjacent zeroing at `+0x5d4/+0x5d8/+0x5dc`.
- This does not identify exact retail `CBattleEngine::WeaponFired`, close `weapon_fire_breaks_stealth`, prove runtime cloak/fire behavior, or prove concrete retail structure layouts.

## Related Functions
- [CBattleEngine__UpdateWeaponEffect](CBattleEngine__UpdateWeaponEffect.md) - current saved-name path for the recovered `SetCollisionShape` helper
- [CBattleEngine__AddProjectile](CBattleEngine__AddProjectile.md) - Projectile spawning
- CUnit__Init - Parent class initialization
- CBattleEngineWalkerPart - Walker-specific subsystem
- CBattleEngineJetPart - Jet-specific subsystem

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `44f56328…dde0`. `call_xref_scan` still empty.
File `0x001d89e8` still `d0 4d 40 00`. Did not open Ghidra. Did
not edit `rebuild/**`. Did not walk all 54 callees.

Retail entity: `CBattleEngine` vtable slot-9 constructor-time
init, including the HandleAutoAim(NULL) tail already pinned.
Stuart architecture (not proof): `BattleEngine.cpp:63-353`.

Nearest reconstruction owner: **none**. Core has no BattleEngine
object init and no `+0x578`/`+0x57c` part pair.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement this from this mapping
until that lane names the arm.

Siblings: `CBattleEngine__HandleAutoAim` /
`CBattleEngine__HandleLocks` in this folder. Next named:
`CBattleEngine__Move` `0x004081c0` (existing note; no
2026-08-19 PE envelope; HandleLocks' unique inbound).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00404dd0` | `CBattleEngine__Init` | `6aff 6820115d00 … 8be9 … e808cb0d00 … c7856002000003000000 … e8115e0000 … c20400` (2858 B) | incoming-ECX thiscall; SEH; ret 0x4 ×1; 2858 B; 54 E8 / 2 E9 / 29 targets; 0 inbound; unique vtable slot 9 at `0x005d89e8`. HIGH on ABI, `+0x578`/`+0x57c` part stores, `+0x260` 3/2 polarity, HandleAutoAim tail. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on source field names, lock-set init, or rebuild parity. |
