# BattleEngineDataManager.cpp Function Mappings

> Functions from BattleEngineDataManager.cpp mapped to BEA.exe binary
> Debug Path String: `C:\dev\ONSLAUGHT2\BattleEngineDataManager.cpp` at 0x00623674
> Discovered: 2025-12-16 via Ghidra xref analysis

## Overview
- **Functions Mapped:** 3
- **Status:** NAMED in Ghidra
- **Class:** CBattleEngineDataManager
- **Purpose:** Manages Battle Engine configuration data - weapon loadouts, explosion effects, cockpit meshes, and physics parameters

## Function List

| Address | Name | Size | Status |
|---------|------|------|--------|
| 0x0040f590 | CBattleEngineDataManager__Init | ~768 bytes | NAMED |
| 0x0040f890 | CBattleEngineDataManager__Clear | ~228 bytes | NAMED |
| 0x0040f980 | CBattleEngineDataManager__Load | ~1700 bytes | NAMED |

## Function Details

### CBattleEngineDataManager__Init (0x0040f590)
**Purpose:** Initializes a CBattleEngineDataManager instance with default values

**Key Operations:**
- Allocates and sets default configuration name: `"Standard"`
- Sets up default weapon loadout (via CSPtrSet):
  - `"Vulcan Cannon 1"` (twice - primary weapons)
  - `"Pulse Cannon Pod"`
  - `"Missile Pod"`
- Sets default explosion emitter: `"Animated Explosion Emitter 2"`
- Sets default cockpit mesh: `"cockpit2.msh"`
- Initializes 6 weapon slots with default ranges (float 0x447a0000 = 1000.0f)
- Sets various physics/gameplay float parameters at struct offsets 0x00-0x3C

**Struct Layout (partial, offsets in dwords):**
| Offset | Value (hex) | Value (float) | Purpose |
|--------|-------------|---------------|---------|
| 0x00 | 0x40f00000 | 7.5f | Unknown |
| 0x01 | 0x40a00000 | 5.0f | Unknown |
| 0x02 | 0x3e99999a | 0.3f | Unknown |
| 0x03 | 0x3dcccccd | 0.1f | Unknown |
| 0x04 | 0x40800000 | 4.0f | Unknown |
| 0x05 | 0x40000000 | 2.0f | Unknown |
| 0x06 | 0x3fc00000 | 1.5f | Unknown |
| 0x07 | 0x41a00000 | 20.0f | Unknown |
| 0x08 | 0x40200000 | 2.5f | Unknown |
| 0x09 | 0x42b40000 | 90.0f | Possibly angle/FOV |
| 0x0a | 0x3c23d70a | 0.01f | Small value |
| 0x0b | 0x3f800000 | 1.0f | Scale/multiplier |
| 0x0c | 0x3f666666 | 0.9f | Unknown |
| 0x0d | 0x3e19999a | 0.15f | Unknown |
| 0x0e | 0x3f800000 | 1.0f | Unknown |
| 0x0f | 0x3f800000 | 1.0f | Unknown |
| 0x18 | pointer | - | Unknown string ptr |
| 0x19 | pointer | - | Unknown string ptr |
| 0x1a | pointer | - | Explosion emitter name |
| 0x1b | pointer | - | Cockpit mesh name |
| 0x28 | 0 | - | Unknown flag |
| 0x29 | 1 | - | Unknown flag/count |
| 0x2a | pointer | - | Configuration name |

### CBattleEngineDataManager__Clear (0x0040f890)
**Purpose:** Clears/frees all allocated data in a CBattleEngineDataManager instance

**Key Operations:**
- Frees configuration name string at offset 0xA8
- Iterates and frees two linked lists (CSPtrSet) at offsets 0x40 and 0x50 (weapon lists)
- Frees string pointers at offsets 0x60, 0x64, 0x68, 0x6C
- Uses memory manager at 0x9c3df0 (OID__FreeObject = free)

### CBattleEngineDataManager__Load (0x0040f980)
**Purpose:** Loads CBattleEngineDataManager data from a binary stream with versioning support

**Key Operations:**
- Calls Clear() first to reset state
- Reads version number into local_108
- Has extensive version checking (versions 1-12+) for backward compatibility:
  - Version < 5: Reads legacy weapon names from stream
  - Version < 8: Reads legacy float params, sets defaults for newer fields
  - Version >= 5: Reads dynamic weapon lists (CSPtrSet__AddToTail)
  - Version >= 8: Reads additional parameters
  - Version >= 9: Reads string at offset 0x19
  - Version >= 10: Reads string at offset 0x18
  - Version >= 11: Reads cockpit mesh from stream (else defaults to "cockpit2.msh")
  - Version >= 12: Reads flag at offset 0x29 (else defaults to 1)

**Version Default Values (for version < 8):**
| Offset | Value (hex) | Value (float) |
|--------|-------------|---------------|
| 0x00 | 0x3f666666 | 0.9f |
| 0x01 | 0x3e99999a | 0.3f |
| 0x02 | 0x3c75c28f | 0.015f |
| 0x03 | 0x3ba3d70a | 0.005f |

## Key Observations

1. **Versioned Serialization:** The Load function supports at least 12 data format versions, demonstrating significant evolution of the data structure during development.

2. **Memory Management:** Uses centralized memory manager at 0x9c3df0 for all allocations (OID__AllocObject = alloc, OID__FreeObject = free).

3. **CSPtrSet Usage:** Weapon loadouts are stored in linked list structures (CSPtrSet) for dynamic sizing.

4. **String Storage:** All string data (names, paths) are dynamically allocated and stored as pointers in the struct.

5. **Default Weapons:** The default Battle Engine loadout is:
   - 2x Vulcan Cannon 1 (primary weapons)
   - 1x Pulse Cannon Pod
   - 1x Missile Pod

6. **No Save Function Found:** Only Init, Clear, and Load functions reference this source file. Save functionality may be in a different file or use a generic serialization mechanism.

## Related Files

- **Nearby Functions (same address range):**
  - BattleEngineConfigurations__Load (0x0040f180) - different source file
  - BattleEngineConfigurations__Skip (0x0040f260) - different source file

- **Related Classes:**
  - CBattleEngine (BattleEngine.cpp) - uses this data manager
  - CSPtrSet - linked list container for weapons

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*Debug path: 0x00623674 -> 34 xrefs to 2 unique functions*
