# FEPDevelopment.cpp Functions

> Source File: FEPDevelopment.cpp | Binary: BEA.exe
> Debug Path String: 0x0062921c (`C:\dev\ONSLAUGHT2\FEPDevelopment.cpp`)

## Overview

CFEPDevelopment is a frontend page class for development/debug functionality. It provides file enumeration for world selection during development, allowing developers to quickly jump to any level.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00458100 | CFEPDevelopment__EnumerateWorldFiles | Enumerate world files using Win32 API | ~320 bytes |

## Function Details

### CFEPDevelopment__EnumerateWorldFiles (0x00458100)

**Signature:** `int __thiscall CFEPDevelopment__EnumerateWorldFiles(CFEPDevelopment* this, int maxFiles)`

Enumerates world files in the game's data directory for level selection.

**Behavior:**
1. Allocates array via `OID__AllocObject(size, 0x80, debug_path)`
   - Pool ID 0x80 (128) for generic allocations
2. Allocates 100-byte filename buffers for each potential file
3. Builds search path via `FUN_004f7c70()` (likely "data\\worlds\\*.wld")
4. Calls `FindFirstFileA` via function pointer to start enumeration
5. **Loop:** For each file found:
   - Skips directories (checks `dwFileAttributes & 0x10`)
   - Copies filename (max 99 chars) via `strncpy`
   - Calls `FindNextFileA` to continue
6. Closes search handle via `FindClose`
7. Sorts the file list via `FUN_0055e7ae()` (qsort wrapper)
8. Returns 1 on success, 0 on allocation failure

**Win32 API Calls:**
- `FindFirstFileA` (kernel32.dll) - Start file enumeration (via function pointer)
- `FindNextFileA` (kernel32.dll) - Continue enumeration
- `FindClose` (kernel32.dll) - Close search handle

**Memory Allocations:**
- Main array: Variable size based on maxFiles parameter
- Per-file buffers: 100 bytes each (99 chars + null terminator)
- OID Pool: 0x80 (128)

**Key Constants:**
- Max filename length: 99 characters
- Directory flag: 0x10 (FILE_ATTRIBUTE_DIRECTORY)
- Invalid handle: 0xFFFFFFFF (INVALID_HANDLE_VALUE)

## Sorting Function

The enumerated files are sorted via `FUN_0055e7ae`:
- Likely a qsort wrapper
- Comparison function at `LAB_00458050`
- Sorts alphabetically for consistent menu display

## Class Hierarchy

```
CFrontEndPage (base)
    |
    +-- CFEPDevelopment (dev menu page)
            |
            +-- EnumerateWorldFiles (file listing)
            +-- [comparison callback at 0x00458050]
```

## Related Files

- FrontEnd.cpp - Main frontend system, manages all FEP pages
- World.cpp - CWorld class that loads the enumerated world files
- CLIParams.cpp - `-level N` parameter uses similar world loading
- oids.cpp - OID__AllocObject memory allocation

## Technical Notes

1. **Debug Path:** `C:\dev\ONSLAUGHT2\FEPDevelopment.cpp` at 0x0062921c
2. **OID Pool:** 0x80 (128) for generic allocations
3. **Function pointer for FindFirstFileA:** Likely for platform abstraction
4. **Directory filter:** Excludes subdirectories from file list
5. **Sort ensures consistent ordering:** Alphabetical world file list

## Usage Context

This function is part of the developer menu system:
- Only accessible in dev builds (controlled by `g_bDevModeEnabled`)
- Allows quick level selection without going through campaign
- Useful for testing individual levels during development

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*Function renamed to CFEPDevelopment__EnumerateWorldFiles via MCP*
