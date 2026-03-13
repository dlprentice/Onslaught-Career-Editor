# CCareer__Save

> Address: 0x00421350 | Source: `references/Onslaught/Career.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (2026-02-13; MCP call timed out + CodeBrowser froze, but signature was present on read-back after restart)
- **Verified vs Source:** Behavior-level verified (2026-02-23): matches XBOX-style struct dump flow, with retail PC options-entries + tail serialization and caller-side file-write behavior verified.

## Purpose
Serializes career to a buffer for saving as a `.bes` file: writes the 16-bit version stamp, dumps a fixed-size CCareer region, appends the options entries block, then appends a fixed 0x56-byte tail snapshot (`OptionsTail_Write`).

In the Steam retail build observed by this repo, `.bes` saves are fixed-size **10,004 bytes** and the options entries block is **16 entries** (`0x20 * 16` bytes).

## Signature
```c
// Binary calling convention: __thiscall, returns void, pops 4 bytes (1 arg)
void CCareer::Save(void* dest);
```

Ghidra signature (Steam build, verified 2026-02-13):
```c
void CCareer__Save(void * this, void * dest);
```

## On-Disk Layout (Steam Build Fixed 10,004 Bytes)
This matches the struct-dump save strategy in Stuart’s XBOX path, with additional PC-port “options + tail” appended. While the implementation counts “active” options entries, the Steam build observed here always produces a fixed 16-entry block.

| Offset | Size | Content |
|--------|------|---------|
| 0x0000 | 2 | Version word (`current_version_stamp()`) |
| 0x0002 | 0x24BC | Fixed CCareer dump (CCareer starts at file+0x0002; includes `new_goodie_count` at 0x0002..0x0005, so nodes begin at 0x0006) |
| 0x24BE | 0x200 | Options entries (16 entries × `0x20` bytes; populated from global table at `0x008892d8`) |
| 0x26BE | 0x56 | Tail globals/options snapshot (`OptionsTail_Write` @ `0x00420b10`) |

Internal size formula is `0x2514 + 0x20*N`. Retail Steam saves observed here have `N=16` => `0x2714` (10,004 bytes), and this project treats `0x2714` as invariant (do not resize).

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- 2026-02-13: MCP `functions_set_signature(0x00421350, ...)` timed out and hard-froze CodeBrowser; after restart, read-back (`functions_get`) showed the signature was present. Treat this as an MCP-signature hotspot: avoid repeating MCP signature writes here; use manual CodeBrowser `Edit Function...` if the signature ever needs to change.
- Writes version as a 16-bit word then bulk-copies `0x24BC` bytes into `dest + 2` (`rep movsd` with `ECX=0x92F`).
- Iterates the options definition table at `0x008892d8` until the sentinel (entry+4 == -1) and writes only “active” entries (byte[0] != 0). In the Steam retail build observed here, this yields 16 entries.
- Calls `OptionsTail_Write` (`0x00420b10`) with the pointer to the end of the options block to append the final 0x56 bytes.
- Does NOT set `mCareerInProgress` (see SaveWithFlag).
- Companion to CCareer__Load

## Side Effects and Boundaries (Verified)

- `CCareer__Save` itself is a **buffer serializer**:
  - writes only to caller-provided `dest`,
  - reads from `this` (`CAREER`) and the options descriptor table at `0x008892d8`,
  - appends options-tail bytes via `OptionsTail_Write`,
  - performs no direct disk I/O.

- File-write side effects occur in callers, not inside `CCareer__Save`:
  - `CFEPOptions__SaveDefaultOptions` (`0x0051f500`) allocates `size = CCareer__GetSaveSize()`, calls `CCareer__Save`, then writes `defaultoptions.bea` via `fopen/fwrite/fclose`.
  - `Platform__AsyncSaveCareer` (`0x004d2580`) on `DAT_0082b5b0 == 2` allocates/save-serializes and calls `CFEPOptions__WriteDefaultOptionsFile(dest, size)`, then frees.
  - `FUN_004d06e0` (PauseMenu path) serializes with `CCareer__Save`, conditionally writes selected save via `PCPlatform__WriteSaveFile`, then writes `defaultoptions.bea` via `CFEPOptions__WriteDefaultOptionsFile`.
  - `CFEPMain__Process` (`0x00462640`) calls `CCareer__Save` at `0x00462893`, then (same branch) calls `CFEPOptions__WriteDefaultOptionsFile` at `0x004628df` and conditionally writes slot data via `PCPlatform__WriteSaveFile`.

## Related Functions
- [CCareer__Load](CCareer__Load.md) - Reverse operation
- [CCareer__SaveWithFlag](CCareer__SaveWithFlag.md) - Save with progress flag
- [CCareer__GetSaveSize](CCareer__GetSaveSize.md) - Returns buffer size needed
