# Battle Engine System

> Analysis from BattleEngine.cpp/h, BattleEngineConfigurations.cpp/h, BattleEngineDataManager.cpp/h, BattleEngineJetPart.cpp/h, and BattleEngineWalkerPart.cpp/h - December 2025

## Overview

The Battle Engine system implements the player-controlled mech, representing the titular Battle Engine in the game. This system includes dual-mode (walker/jet) mechanics, transformation, combat systems, and god mode implementation.

---

## BattleEngine Core Class (BattleEngine.cpp/h)

The `CBattleEngine` class is the core player-controlled mech implementation.

### Class Inheritance Hierarchy

```
CThing
  └── CComplexThing
        └── CActor
              └── CUnit
                    └── CBattleEngine
```

The deep inheritance chain reflects the game's object-oriented design, with each level adding capabilities:
- `CThing` - Base game object
- `CComplexThing` - Multi-part objects
- `CActor` - Animated entities
- `CUnit` - Combat units (health, damage, AI)
- `CBattleEngine` - Player mech specifics

### Composition Pattern

The Battle Engine uses composition for its dual-mode (walker/jet) mechanics:

```cpp
CBattleEngineWalkerPart mWalkerPart;  // Ground movement component
CBattleEngineJetPart    mJetPart;      // Flight physics component
CActiveReader<CPlayer>  mPlayer;       // Player association
```

This allows mode-specific code to be cleanly separated while sharing the core CBattleEngine state.

### Key Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `kBattleEngineStores` | 6 | Number of weapon ammo stores |
| `kMaxConfigurations` | 20 | Maximum mech configurations |
| `MAX_AUG_VALUE` | 10.0 | Weapon augmentation threshold |
| `BATTLE_ENGINE_COFGHEIGHT` | 1.9f | Center of gravity height |
| `BATTLE_ENGINE_TRANSFORM_TIME` | 0.5 | Transformation duration (seconds) |
| `AUG_DECREASE_RATE` | 0.01 | Augmentation drain per frame |

### Transformation System

The Battle Engine has four states for walker/jet mode transitions:

| State | Description |
|-------|-------------|
| `BATTLE_ENGINE_STATE_WALKER` | Ground mode active |
| `BATTLE_ENGINE_STATE_JET` | Flight mode active |
| `BATTLE_ENGINE_STATE_MORPHING_TO_JET` | Walker → Jet transition |
| `BATTLE_ENGINE_STATE_MORPHING_TO_WALKER` | Jet → Walker transition |

**Transformation Requirements:**
- Walker → Jet requires `mMinTransformEnergy` (sufficient energy reserve)
- Transformation takes 0.5 seconds (`BATTLE_ENGINE_TRANSFORM_TIME`)
- **"MASSIVE HACK"** comment in code: mesh swapping between `f_be1.msh` (walker) and `f_be2.msh` (jet)

### God Mode Implementation Details

Two independent flags control invincibility:

| Flag | Effect |
|------|--------|
| `mVulnerable` | When FALSE, immune to damage |
| `mInfinateEnergy` | When TRUE, unlimited energy |

**SetVulnerable(FALSE) Behavior:**
- Makes BE immune to damage
- Visual damage effects still play (sparks, sounds)
- At line 2234 in `Damage()`: if `mVulnerable==FALSE`, life/shields/energy are restored after damage calculation

**SetInfinateEnergy(TRUE) Behavior:**
- Refills energy to maximum when enabled
- Prevents energy drain during gameplay

**CRITICAL: Water Death Exception (Line 1261)**

Water kills require BOTH flags to survive:
```cpp
// Conceptual logic from BattleEngine.cpp line 1261
if (mVulnerable == FALSE && mDeveloperMode) {
    // Survive water contact
} else {
    // Die instantly
}
```

This means even god mode doesn't save you from water unless developer mode is also active!

### Damage System

The `Damage()` function (around line 2234) implements the following flow:

1. Apply incoming damage to shields first
2. Shield damage multiplied by `mShieldEfficiency`
3. Overflow damage applied to health
4. Report to player stats: `PS_DAMAGETAKEN` uses `*256` multiplier (fixed-point)
5. **God mode check at end**: if `mVulnerable==FALSE`, restore all values

This means damage is fully calculated and reported for statistics even in god mode - only the final restoration prevents actual harm.

### Weapon Augmentation System

The augmentation system powers up weapons based on absorbed shield damage:

```cpp
mAugValue += shieldDamageAbsorbed;
if (mAugValue >= MAX_AUG_VALUE) {  // >= 10.0
    // Primary weapon becomes augmented (more powerful)
}
// Augmentation drains at AUG_DECREASE_RATE (0.01/frame)
```

Augmentation provides a reward loop: taking shield damage charges your weapon for more powerful attacks.

### Debug Features

| Feature | Access Method |
|---------|---------------|
| `cg_battleenginevisible` | Console variable - toggle BE visibility |
| Developer mode water bypass | Requires `mDeveloperMode` flag |

### Disabled Features Discovered

Remnants of cut features found in the source code:

- **Afterburner**: `BUTTON_MECH_JET_AFTERBURNER` handler is commented out
- **Cloak**: `BUTTON_MECH_CLOAK` exists and calls `mBattleEngine->HandleCloak()`

These were apparently cut from the final game but the button mappings and hooks remain in the code.

### Hardcoded Level Hacks

These levels have special handling for carrier-based leg animation (when the BE starts on a ship):

```
Levels: 231, 232, 331, 221, 222, 524, 523, 332
```

These correspond to "Special Pan Camera Levels" - levels where the player starts on a moving platform.

---

## Battle Engine Configurations (BattleEngineConfigurations.cpp/h)

Defines the mech configuration system for stats and weapons.

### Key Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `kMaxConfigurations` | 20 | Maximum mech configurations |
| `kCurrentBattleEngineDataFormat` | 12 | Current data format version |
| `kBattleEngineStores` | 6 | Number of weapon stores |

### CBattleEngineData Class

```cpp
class CBattleEngineData {
    float mMaxAirVelocity;       // Jet mode max speed
    float mLife;                  // Health points
    float mEnergy;                // Energy capacity
    float mShieldEfficiency;      // Shield effectiveness
    // ... weapon lists
};
```

### Default Weapons

- Walker mode: "Vulcan Cannon 1", "Pulse Cannon Pod"
- Jet mode: "Vulcan Cannon 1", "Missile Pod"

### Format Version History

12 versions with backwards compatibility for loading older saves.

---

## Battle Engine Data Manager (BattleEngineDataManager.cpp/h)

Static manager class for mech configurations.

### Class Structure

```cpp
class UBattleEngineDataManager {
    static void LoadConfigurations();
    static CBattleEngineData* GetConfiguration(const char* name);
    // Version 1-12 field additions
};
```

**Default Configuration Name:** "Standard"

---

## Battle Engine Jet Part (BattleEngineJetPart.cpp/h)

Jet mode flight physics and controls.

### Aerobatics System

| Maneuver | Activation | Duration |
|----------|------------|----------|
| Barrel Roll | Double-tap left/right within 0.2s | 26 frames |
| Loop | Double-tap forward/back within 0.2s | Variable |

### Stall Detection

- Auto-morph to walker mode if velocity < 0.15 for 2.5 seconds
- Prevents players from hovering in jet mode

### Water Skimming

- Damage applied when altitude < 0.5 units
- Encourages high-altitude flight over water

**Typo Preserved:** "barrell roll" (line 441) - should be "barrel roll"

---

## Battle Engine Walker Part (BattleEngineWalkerPart.cpp/h)

Walker mode movement and ground combat.

### Dash System

| Parameter | Value |
|-----------|-------|
| Activation | Double-tap direction |
| `mDashVelocity` | 25.0 |
| `mDashLength` | 15 frames |

Walk cycle animation is tied to movement velocity for realistic locomotion.

---

## Typos Preserved in Source

| Typo | Location | Should Be |
|------|----------|-----------|
| `barrell roll` | BattleEngineJetPart.cpp:441 | barrel roll |
| `GetCurrentAccleration` | Method name | GetCurrentAcceleration |
| `sepecial` | Comment | special |
| `mInfinateEnergy` | Member variable | mInfiniteEnergy |

---

## Relevance to Save Editing

**INDIRECT** - Battle Engine state is runtime-only and NOT saved to .bes files.

However, understanding the Battle Engine system explains:

1. **God mode persistence**: The internal build has a per-player `mIsGod[]` array in CCareer, but the Steam build does **not** appear to persist per-player invincibility flags in the save (those offsets are used for invert-Y settings). Runtime invincibility remains cheat-gated via `IsCheatActive(3)` (PC port uses `Maladim`, no visible effect so far)
2. **Water death exception**: Why god mode doesn't prevent water death (requires `mDeveloperMode` flag)
3. **Kill tracking**: Battle Engine damage reports feed into kill counters saved at CCareer `+0x23F4` (file `0x23F6`, true view)
4. **Configuration system**: Mech stats are loaded from config files, not save files

---

## Files Analyzed

| File | Purpose |
|------|---------|
| `BattleEngine.cpp` | Core mech implementation, god mode, damage, transformation |
| `BattleEngine.h` | CBattleEngine class definition, constants |
| `BattleEngineConfigurations.cpp` | Mech configuration data structures |
| `BattleEngineConfigurations.h` | CBattleEngineData class, format versions |
| `BattleEngineDataManager.cpp` | Static configuration manager |
| `BattleEngineDataManager.h` | Manager class definition |
| `BattleEngineJetPart.cpp` | Flight physics, aerobatics |
| `BattleEngineJetPart.h` | Jet part class definition |
| `BattleEngineWalkerPart.cpp` | Ground movement, dash system |
| `BattleEngineWalkerPart.h` | Walker part class definition |

---

## See Also

- [../core/actor-system.md](../core/actor-system.md) - Base movement and physics
- [../../game-mechanics/god-mode.md](../../game-mechanics/god-mode.md) - God mode investigation
- [../../save-file/save-format.md](../../save-file/save-format.md) - God mode offsets in save files

---

*Last updated: December 2025*
