# FEPBEConfig.cpp Functions

> Source File: FEPBEConfig.cpp | Binary: BEA.exe
> Debug Path: 0x00628fac (`C:\dev\ONSLAUGHT2\FEPBEConfig.cpp`)
> RTTI: `.?AVCFEPBEConfig@@` at 0x00629c58

## Overview

Frontend Page for Battle Engine Configuration. This class (`CFEPBEConfig`) handles the BE (Battle Engine) weapon loadout and configuration UI in the frontend menu system. It manages weapon selection, squad configurations, and provides access to weapon properties like sounds and stats.

The "BE" in the name stands for "Battle Engine" - the player's mech unit. This page allows players to configure their Battle Engine's weapon loadout before missions.

## Functions

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x0044f030 | CFEPBEConfig__GetWeaponProperty | ~720 bytes | Get weapon property (returns offset 0x10/0x11/0x12 based on param_3) |
| 0x0044f300 | CFEPBEConfig__GetWeaponPropertyAlt | ~560 bytes | Alternative weapon property getter (similar lookup pattern) |
| 0x0044f530 | CFEPBEConfig__PlayWeaponSound | ~768 bytes | Play weapon selection sound (calls FUN_004f2580) |
| 0x0044f830 | CFEPBEConfig__PlayWeaponSoundAlt | ~368 bytes | Alternative weapon sound player |
| 0x0044fa93 | (Unrecognized - Init) | ~781 bytes | Init function with debug traces (beconf::init() 0-5) |
| 0x0044fda0 | CFEPBEConfig__Cleanup | ~80 bytes | Cleanup/destructor helper (frees resources) |
| 0x0044fdf0 | CFEPBEConfig__CleanupSquads | ~128 bytes | Cleanup squad data with SEH |
| 0x0044fe70 | CFEPBEConfig__Load | ~400 bytes | Load BE config from file (uses CRelaxedSquad) |

**Total: 8 functions (~3,805 bytes)**

### Signature Snapshot (2026-02-24)

- `int CFEPBEConfig__GetWeaponProperty(void * config, int weapon_index, int property_index)`
- `int CFEPBEConfig__GetWeaponPropertyAlt(void * config, int weapon_index, int property_index)`
- `void CFEPBEConfig__PlayWeaponSound(void * config, int weapon_index)`
- `void CFEPBEConfig__PlayWeaponSoundAlt(void * config, int weapon_index)`
- `void CFEPBEConfig__Load(void * this, void * stream)`

## Unrecognized Code Region

**Address Range: 0x0044fa93 - 0x0044fd9f**

This ~781-byte region contains the `CFEPBEConfig::Init()` function but is not recognized as a function by Ghidra's auto-analysis (no incoming xrefs detected). It contains 6 sequential debug trace calls:

| String Address | Debug Message | Code Address |
|----------------|---------------|--------------|
| 0x00628fd0 | "beconf::init() 0\n" | 0x0044fab0 |
| 0x00628f50 | "beconf::init() 1\n" | 0x0044fc03 |
| 0x00628f24 | "beconf::init() 2\n" | 0x0044fc4b |
| 0x00628f64 | "beconf::init() 3\n" | 0x0044fbd9 |
| 0x00628f10 | "beconf::init() 4\n" | 0x0044fc7e |
| 0x00628ef0 | "beconf::init() 5\n" | 0x0044fcc8 |

This function likely initializes the BE configuration page, loading available weapons, setting up UI elements, and preparing squad configurations. The function may only be called via vtable/indirect call.

## Key Observations

### Weapon Lookup Pattern
All weapon functions use a common lookup pattern:
1. Iterate through global weapon list (DAT_0089da34 / DAT_0089da3c)
2. Compare weapon ID with target (DAT_0089d94c)
3. Traverse linked list structure (CSPtrSet__First / CSPtrSet__Next)
4. String comparison for weapon name matching
5. Access weapon properties at offsets (0x10, 0x11, 0x12 for different stats)

### Key Global Variables
- `DAT_0089da34` / `DAT_0089da3c` - Weapon list head/current pointers
- `DAT_0089d94c` - Current/target weapon ID
- `DAT_006602a0` / `DAT_006602a8` - Secondary weapon list
- `DAT_008553e8` - Weapon configuration array

### Error Handling
When weapon lookup fails, functions call `FUN_004f7bf0(s_Unknown_Weapon_00628ec0)` with string "Unknown Weapon" (0x00628ec0). This is a debug/warning output function.

### Squad System Integration
The Load function uses `CSPtrSet__Init` (0x004e5840) to initialize squad data. Squads are stored in pointer sets via `CSPtrSet__AddToTail` (0x004e5b20).

### File I/O
`CFEPBEConfig__Load` uses:
- `OID__AllocObject` - Memory allocation with debug tracking
- `DXMemBuffer__ReadBytes` (`0x00548570`) - File read (calls ReadFile, uncompress)
- Configuration files appear to be compressed

### Weapon Property Indices (param_3)
- `0` - Returns `puVar3[0x10]` (primary stat, e.g., damage)
- `1` - Returns `puVar3[0x11]` (secondary stat, e.g., range)
- `2` - Returns `puVar3[0x12]` (tertiary stat, e.g., fire rate)

## Related Classes

- `CRelaxedSquad` - Squad data structure initialized during config load
- `CSPtrSet` - Smart pointer set for managing weapon/squad collections
- Weapon data structures at offsets 0x40-0x60, 0x50-0x58 within config objects

## Debug Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x00628ec0 | "Unknown Weapon" | Error when weapon lookup fails |
| 0x00628ef0 | "beconf::init() 5\n" | Init trace stage 5 |
| 0x00628f10 | "beconf::init() 4\n" | Init trace stage 4 |
| 0x00628f24 | "beconf::init() 2\n" | Init trace stage 2 |
| 0x00628f50 | "beconf::init() 1\n" | Init trace stage 1 |
| 0x00628f64 | "beconf::init() 3\n" | Init trace stage 3 |
| 0x00628fac | "C:\\dev\\ONSLAUGHT2\\FEPBEConfig.cpp" | Source file path |
| 0x00628fd0 | "beconf::init() 0\n" | Init trace stage 0 |

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*8 functions identified, 1 unrecognized code region*
