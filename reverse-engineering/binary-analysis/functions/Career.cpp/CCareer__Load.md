# CCareer__Load

> Address: 0x00421200 | Source: `references/Onslaught/Career.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (read-back verified 2026-02-14)
- **Verified vs Source:** Behavior-level verified (2026-02-23): matches the XBOX `CCareer::Load(char*, bool)` shape plus retail PC-port-specific options/tail and callsite-flag behavior.

## Purpose
Deserializes career from buffer, validates the 16-bit version stamp, bulk-copies the fixed CCareer region, then conditionally loads the variable options entries and 0x56-byte tail snapshot.

## Signature
```c
// Binary calling convention: __thiscall, returns 0/1, pops 8 bytes (2 args)
int CCareer::Load(void* source, int flag);
```

Ghidra signature (Steam build, verified 2026-02-14):
```c
int CCareer__Load(void * this, void * source, int flag);
```

## Version Stamp
- Expected value: `current_version_stamp()` (source), observed `0x4BD1` in retail saves
- Location: first **2 bytes** of the `.bes` buffer (offset `0x0000`)
- In many saves, the first 4 bytes *look like* `d1 4b 00 00` in 4-byte aligned hex views: 16-bit version word `0x4BD1` followed by the low-16 of `new_goodie_count` (often `0`).

## High-Level Flow (BEA.exe)
1. Validate `*(uint16_t*)source == version_word`.
2. `memcpy(this, source + 2, 0x24BC)` (fixed CCareer dump).
3. Clamp/normalize the **top byte** of the first two kill counters (`this+0x23F4`, `this+0x23F8`), preserving the lower 24 bits.
4. If `(char)flag != 0`:
   - Call a frontend helper (likely “set current level to highest available”)
   - Restore pre-load music/sound volume fields (it stashes `this+0x248C/0x2490` before the memcpy)
   - Return `true` without applying options/tail.
5. Else (`(char)flag == 0`, full load):
   - Apply audio volumes (calls into SOUND/MUSIC)
   - Load variable options entries into the table at `0x008892d8` (reads only entries whose table byte[0] is non-zero, matching the save format).
   - Call `OptionsTail_Read` (`0x00420d70`) to load the final 0x56-byte tail snapshot.

This conditional matches a plausible porting intent: “load career without clobbering current global options” vs “load career + options snapshot”.

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Critical for understanding save file format
- Companion to CCareer__Save
- Deep-pass verified callsites (2026-02-23):
  - `0x00461f44` in `CFEPLoadGame__DoLoad` calls `CCareer__Load` after `PUSH 0x1` (`flag=1`, skip options/tail apply and preserve pre-load audio globals).
  - `0x00512337` in `CLTShell__WinMain` calls `CCareer__Load` after `PUSH 0x0` (`flag=0`, full options/tail apply path).

## Related Functions
- [CCareer__Blank](CCareer__Blank.md) - Called before load to clear state
- [CCareer__Save](CCareer__Save.md) - Reverse operation
- [CCareer__GetSaveSize](CCareer__GetSaveSize.md) - Returns expected buffer size
