# Sentinel.cpp Functions

> Source File: Sentinel.cpp | Binary: BEA.exe
> Debug Path: 0x0063221c

## Overview

Sentinel unit implementation. CSentinel appears to be a defensive/turret-type unit.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| ~0x004de990* | CSentinel__Init* | Initialize sentinel | ~600 bytes |

*Note: Function not recognized in Ghidra - needs manual creation at address containing xrefs 0x004dead4, 0x004deb14, 0x004deb4f

## Xrefs to Debug Path

| Address | Type | Notes |
|---------|------|-------|
| 0x004dead4 | Main code | Memory allocator call |
| 0x004deb14 | Main code | Memory allocator call |
| 0x004deb4f | Main code | Memory allocator call |
| 0x005d4b50 | Unwind handler | Exception cleanup |
| 0x005d4b66 | Unwind handler | Exception cleanup |
| 0x005d4b7c | Unwind handler | Exception cleanup |

## Exception Handlers

| Address | Name | Purpose |
|---------|------|---------|
| 0x005d4b50 | Unwind@005d4b50 | Cleanup handler |
| 0x005d4b66 | Unwind@005d4b66 | Cleanup handler |
| 0x005d4b7c | Unwind@005d4b7c | Cleanup handler |

## Status

**PARTIAL** - Function needs manual creation in Ghidra. The code exists but Ghidra's auto-analysis hasn't recognized it as a function.

## Related Files

- Unit.cpp - Likely parent class
- Cannon.cpp - Similar turret/weapon unit

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
