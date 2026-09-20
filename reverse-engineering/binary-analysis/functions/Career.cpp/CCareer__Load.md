# CCareer__Load

Status: mixed — inherited source comparison with independently rechecked retail load contract
Last updated: 2026-09-19
Summary: raw career copy, version admission and distinct load modes; size validation belongs to callers.
Source File: `references/Onslaught/Career.cpp` (partial-source comparison) | Binary: pristine `BEA.exe.original.backup`; September 19 byte/control evidence is linked below.
Specimen: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

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
- Rechecked retail expression: low 16 bits of `[00623e24] + 0x4bc0`; the pristine global is 17, yielding `0x4bd1`.
- Location: first **2 bytes** of the `.bes` buffer (offset `0x0000`)
- In many saves, the first 4 bytes *look like* `d1 4b 00 00` in 4-byte aligned hex views: 16-bit version word `0x4BD1` followed by the low-16 of `new_goodie_count` (often `0`).

## High-Level Flow (BEA.exe)
1. Validate `*(uint16_t*)source == version_word`.
2. `memcpy(this, source + 2, 0x24BC)` (fixed CCareer dump).
3. Clamp/normalize the **top byte** of the first two kill counters (`this+0x23F4`, `this+0x23F8`), preserving the lower 24 bits.
4. If the low byte of `flag` is nonzero:
   - Call a frontend helper (likely “set current level to highest available”)
   - Restore pre-load music/sound volume fields (it stashes `this+0x248C/0x2490` before the memcpy)
   - Return `true` without applying options/tail.
5. Else (`(char)flag == 0`, full load):
   - Apply audio values from absolute music/sound globals `00662ab0/00662aac`. These are fields of canonical CAREER `00660620`; an arbitrary receiver does not supply these values.
   - Load variable options entries into the table at `0x008892d8` (reads only entries whose table byte[0] is non-zero, matching the save format).
   - Call `OptionsTail_Read` (`0x00420d70`) to load the final 0x56-byte tail snapshot.

This function has no length argument and checks neither a checksum nor node/link
structure. Version mismatch returns before copying receiver state. The options
loop walks fixed 32-byte rows until ID `-1`; each destination's pre-copy active
byte selects whether to consume a serialized row. The copy replaces active/ID
metadata too, without validating it. It does not route rows by incoming ID.

The [September 19 recheck](../../save-options-static-review-2026-05-26.md#september-19-independent-recheck)
executes the canonical flag-zero path inside original WinMain, followed by the
separate startup Blank. Normal flag-one behavior and its complete frontend
publication transaction have fresh static checks, not new composed execution.
Load itself preserves the copied career-in-progress field; Blank clears it later
on the boot route. Flag `0x100` selects the zero-byte branch, not career mode.

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
