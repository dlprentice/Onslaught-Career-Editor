# FEPDirectory.cpp - Function Analysis

**Source File:** `C:\dev\ONSLAUGHT2\FEPDirectory.cpp`
**Debug Path String:** `0x0063fb4c`
**RTTI Class Name:** `.?AVCFEPDirectory@@` at `0x00629bf8`

## Overview

CFEPDirectory is a Front End Page (FEP) class that handles directory/file browsing in the game's menu system. Based on analysis, this class manages save file enumeration and display in the load/save game menus.

## Class Structure

The class uses a large buffer structure:
- Offsets `0x04` to `0x4000`: Array of 4096 (0x1000) pointers to save file name strings
- Offset `0x4004`: Save file count (`mNumSaveFiles`)
- Offset `0x4008`: Selected file index (`mSelectedIndex`)
- Offset `0x400C`: Scroll offset for display (`mScrollOffset`)
- Offset `0x4010`: Last selection time (float, for animation)

## Functions Found

### CFEPDirectory__RefreshSaveFileList
| Property | Value |
|----------|-------|
| Address | `0x0051ad30` |
| Signature | `void __thiscall CFEPDirectory::RefreshSaveFileList(int forceRefresh)` |
| Size | ~224 bytes |
| Calling Convention | thiscall (ECX = this pointer) |

**Live Signature (normalized, 2026-02-24):**
- `void CFEPDirectory__RefreshSaveFileList(void * this, int force_refresh)`

**Purpose:** Refreshes the list of save files displayed in the directory browser.

**Behavior:**
1. Calls `FUN_0041a200()` - likely initializes/clears state
2. Checks platform storage availability via `FUN_00514960()`
3. If `forceRefresh == 0` AND no storage available, calls error handler and returns
4. Calls `EnumerateSaveFiles_1()` to get count of save files
5. Iterates through save files:
   - Allocates 512-byte (0x200) string buffers for file names if needed
   - Calls `EnumerateSaveFiles_2()` to populate each file name string
6. Cleans up unused string buffers (frees memory via `OID__FreeObject`)
7. Adjusts selected index if it exceeds the new file count
8. Ensures selected index is non-negative

**Decompiled Code:**
```c
void __thiscall CFEPDirectory::RefreshSaveFileList(int forceRefresh)
{
    int *numFiles = this + 0x1001;  // Offset to file count

    FUN_0041a200();  // Init
    FUN_00514960(g_Platform, &storageAvailable, 0, 0, 0);

    if (forceRefresh == 0 && storageAvailable == 0) {
        CFrontEnd__SetPage(&DAT_0089d758, 0, 0x32);  // page=0, time=0x32 (exact UX meaning TBD)
        return;
    }

    EnumerateSaveFiles_1(g_Platform, numFiles);

    // Populate file name strings
    for (int i = 0; i < *numFiles; i++) {
        if (this->fileNames[i] == NULL) {
            this->fileNames[i] = AllocString(0x200);  // 512 bytes
        }
        EnumerateSaveFiles_2(g_Platform, i, this->fileNames[i]);
    }

    // Free unused slots
    for (int i = *numFiles; i < 0x1000; i++) {
        if (this->fileNames[i] != NULL) {
            FreeString(this->fileNames[i]);
            this->fileNames[i] = NULL;
        }
    }

    // Clamp selected index
    if (this->selectedIndex >= *numFiles) {
        this->selectedIndex = *numFiles - 1;
    }
    if (this->selectedIndex < 0) {
        this->selectedIndex = 0;
    }
}
```

**Cross-References (Callers):**
- `0x0051ac51` - Within another CFEPDirectory method (likely Initialize or similar)
- `0x005202e1` - `CFEPVirtualKeyboard__Process` (`0x005202d0`) calls into directory refresh during keyboard page processing

## Related Functions

| Address | Function | Notes |
|---------|----------|-------|
| `0x0051ae70` | `CFEPDirectory__RenderSaveFileList` | Shared save-list renderer used by both `CFEPDirectory__Render` and `CFEPVirtualKeyboard__Render`; performs row draw, scroll/selection mouse hit-tests, and returns clicked save index (or `0` if none). |
| `0x0051a970` | `CFEPCredits__TransitionNotification` | Nearby vtable target from the adjacent `CFEPCredits` class (`0x005db880`), not part of CFEPDirectory. |

## Memory Allocation

The class uses debug-enabled allocation:
- `OID__AllocObject(size, type, __FILE__, __LINE__)` - Allocates memory with debug info
- `OID__FreeObject(ptr)` - Frees memory

This matches the pattern seen in other FEP classes where memory allocation includes source file tracking for debugging.

## Global References

- `DAT_008a9694` - Storage device id / platform slot (PC build uses this as the first arg to `EnumerateSaveFiles_*` and `PCPlatform__*SaveFile` calls; typically 0)
- `EnumerateSaveFiles_1` at `0x005149c0` - Gets save file count
- `EnumerateSaveFiles_2` at `0x00514a80` - Gets save file name by index

## Analysis Notes

1. **Max Save Files:** The class supports up to 4096 (0x1000) save files, though this is likely overkill for practical use
2. **Memory Management:** File name strings are allocated on-demand and freed when slots become unused
3. **Error Handling:** If storage is unavailable, transitions pages via `CFrontEnd__SetPage(page=0, time=0x32)` (exact UX meaning TBD)
4. **Thiscall Convention:** All methods use ECX as the this pointer, typical of MSVC-compiled C++

## Version Info

- **Analysis Date:** December 2025
- **Analysis Method:** Static binary analysis
- **Binary:** BEA.exe (Steam PC release)
