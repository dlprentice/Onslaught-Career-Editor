# FEPWingmen.cpp

Front End Page for wingmen/ally selection screen. Handles the UI for selecting wingmen before missions.

**Debug Path:** `C:\dev\ONSLAUGHT2\FEPWingmen.cpp`
**String Address:** `0x0063fd4c`

## Functions Found

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x00521650 | CFEPWingmen__GetWingmenCount | ~100 | Returns count of available wingmen for current level |
| 0x00521a60 | CFEPWingmen__Destroy | ~128 | Destructor - frees wingmen data and name strings |
| 0x00521ae0 | CFEPWingmen__Load | ~432 | Loads wingmen data from file, initializes CRelaxedSquad |
| 0x00521c80 | CFEPWingmen__Update | ~160 | Per-frame update with animation timing |

**Total: 4 functions identified (3 with FEPWingmen.cpp xrefs confirmed)**

## Undefined Function Region

There is a large undefined function in the range **0x005216c0 - 0x00521a5f** that contains 3 xrefs to FEPWingmen.cpp:
- 0x00521708 - PUSH 0x63fd4c (line 0x37 = 55)
- 0x005217cb - PUSH 0x63fd4c (line 0xe7 = 231)
- 0x0052188e - PUSH 0x63fd4c (line 0xeb = 235)

This function could not be auto-created by Ghidra but clearly contains FEPWingmen code. Manual function creation at 0x005216c0 is needed in Ghidra GUI.

## Function Details

### CFEPWingmen__GetWingmenCount (0x00521650)

Returns the count of wingmen available for the current mission/level.

```c
char CFEPWingmen__GetWingmenCount(void)
{
    // Iterates through wingmen list (DAT_0089da6c)
    // Finds wingmen matching current level (DAT_0089d94c)
    // Counts how many wingmen slots are filled (checks offsets +4, +8, +12)
    // Returns count 0-3
}
```

**Globals Used:**
- `DAT_0089da6c` - Wingmen list head
- `DAT_0089da74` - Current wingmen iterator
- `DAT_0089d94c` - Current level ID

### CFEPWingmen__Destroy (0x00521a60)

Destructor that frees all allocated wingmen data.

```c
void __thiscall CFEPWingmen__Destroy(CFEPWingmen *this)
{
    // Frees wingmen at offsets +8, +0xC, +0x10
    // Iterates through name string list at +0x28
    // Calls FUN_0046ba90() before each free (likely reference counting)
    // Calls OID__FreeObject() to deallocate memory
}
```

**Calls:**
- `FUN_0046ba90` - Pre-free handler (ref counting?)
- `OID__FreeObject` - Memory deallocation
- `CSPtrSet__Remove` - Remove entry from internal list (returns list node to pool)
- `FUN_0044fdf0` - Unknown cleanup

### CFEPWingmen__Load (0x00521ae0)

Loads wingmen data from a file stream. This is a serialization function.

```c
void __thiscall CFEPWingmen__Load(CFEPWingmen *this, CFileStream *stream)
	{
	    // Allocates 0x24 bytes for wingmen struct
	    // Calls CSPtrSet__Init() to initialize internal pointer-set (empty list)
	    // Reads version info, wingmen count, names
	    // For each wingman: reads name length, allocates string, reads name
	    // Stores names in CSPtrSet linked list
	    // Handles version differences (version < 2, version < 3)
	}
```

**Memory Allocation:**
- Line 0xd3 (211): Allocates 0x24 (36) bytes for main structure
- Line 0xe7 (231): Allocates variable-sized string buffers
- Line 0xeb (235): Allocates 4 bytes for string pointer entries

	**Calls:**
	- `OID__AllocObject` - Memory allocation with debug info
	- `CSPtrSet__Init` (0x004e5840) - Initialize empty pointer-set (head/tail/count = 0)
	- `DXMemBuffer__ReadBytes` (`0x00548570`) - Read from file stream
	- `CSPtrSet__AddToTail` (0x004e5b20) - Add to linked list

### CFEPWingmen__Update (0x00521c80)

Per-frame update function for wingmen selection screen.

```c
void __thiscall CFEPWingmen__Update(CFEPWingmen *this, int param_1)
{
    // Increments animation timer at offset +0x14 by 0.01
    // Updates wingmen display at offsets +8, +0xC, +0x10
    // Decrements fade values at offsets +0x1C and +0x20 by 0.1
    // Clamps fade values to 0 if negative
    // If param_1 == 0 && g_bDevModeEnabled: calls virtual method
}
```

**Member Offsets:**
- `+0x14` (this[5]): Animation timer (float, += 0.01 per frame)
- `+0x1C` (this[7]): Fade value 1 (float, -= 0.1, clamped to 0)
- `+0x20` (this[8]): Fade value 2 (float, -= 0.1, clamped to 0)

**Calls:**
- `FUN_0046baf0` - Wingman display update
- Virtual method at vtable+0xC when in dev mode

## CFEPWingmen Class Structure (Partial)

Based on decompilation analysis:

```c
struct CFEPWingmen {
    void **vtable;           // +0x00: Virtual function table
    // ...
    void *wingman1;          // +0x08: First wingman data
    void *wingman2;          // +0x0C: Second wingman data
    void *wingman3;          // +0x10: Third wingman data
    float animTimer;         // +0x14: Animation timer
    // ...
    float fadeValue1;        // +0x1C: Fade animation 1
    float fadeValue2;        // +0x20: Fade animation 2
    // ...
    CSPtrSet *nameList;      // +0x28: Linked list of wingman name strings
    CSPtrSet *nameIterator;  // +0x30: Current position in name list
};
```

## Related Classes

- **CRelaxedSquad** - Squad management (initialized in Load)
- **CSPtrSet** - Pointer set/linked list for wingman names

## Cross-References

Functions that call CFEPWingmen methods:
- Exception handler at 0x005d68c0 references FEPWingmen.cpp (cleanup on exception)
- Data reference at 0x005dba34 points to CFEPWingmen__Load (likely vtable or function pointer table)
