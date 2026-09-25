# CCareer__GetSaveSize

Status: active bounded retail size contract
Last updated: 2026-09-19
Summary: counts initialized active binding rows; this is allocation sizing, not loader validation.
Source File: `references/Onslaught/Career.cpp` (partial-source comparison) | Binary: pristine `BEA.exe.original.backup`; September 19 byte/control evidence is linked below.

> Address: 0x00421430 | Source: `references/Onslaught/Career.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (MCP, read-back verified 2026-02-13)
- **Verified vs Source:** No (source has `SizeOfSaveGame()` but the PC port adds an options entries block + fixed tail; Steam retail observed as 16 entries)

## Purpose
Calculate the save buffer size. Base is fixed, plus `0x20` bytes for each enabled options entry, plus a fixed `0x56`-byte tail. The ordinary initialized retail table yields **10,004 bytes** (`N=16`); changed active/sentinel metadata can change the result.

## Signature
```c
int CCareer::GetSaveSize(void);
```

## Return Value
- Internally returns `0x2514 + 0x20 * N`, where `N` is the count of “active” option entries in the global table at `0x008892d8` (byte[0] != 0), up to the sentinel (entry+4 == -1).
- Typical retail Steam saves observed here have `N=16` => `0x2714` (10,004 bytes).

## Breakdown (As Implemented)
| Component | Size |
|-----------|------|
| Version word | 2 |
| Fixed CCareer dump | 0x24BC |
| Options entries | 0x20 * N |
| Tail snapshot (`OptionsTail_Write`) | 0x56 |
| **Total** | **0x2514 + 0x20 * N** |

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- 2026-02-13: MCP signature set to `int CCareer__GetSaveSize(void)` and read-back verified via `functions_get`.
- Used by save system to allocate buffers
- September 19: the original single-binding initializer and this complete 52-byte body execute in the [startup controls](../../save-options-static-review-2026-05-26.md#september-19-independent-recheck), producing 10,004 bytes. Raw PE zero-filled storage is not an initialized table. Traversal uses 32-byte stride, not a linked list.
- For this project/tooling: treat save files as fixed `0x2714` bytes (do not resize) and preserve all bytes in options/tail regions.

## Related Functions
- [CCareer__Save](CCareer__Save.md) - Uses this size
- [CCareer__Load](CCareer__Load.md) - Has no size parameter; callers check their read count before invoking it
