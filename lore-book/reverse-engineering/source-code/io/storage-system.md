# Storage System

## Storage System (storage.cpp/h, DXMemBuffer.cpp/h, MemoryCard.h)

> Analysis added December 2025

**Purpose**: Platform-abstracted file I/O and save game management. This is **CRITICAL** for understanding save file formats across PC/Xbox/PS2.

### Architecture

The storage system uses a class hierarchy for platform abstraction:

```
CStorage (abstract base)
   |
   +-- CPCStorage     (PC implementation)
   +-- CPS2Storage    (PlayStation 2)
   +-- CXBOXStorage   (Xbox)

CDXMemBuffer (PC/Xbox buffered I/O)
CMEMORYCARD (save file management)
```

### Buffer Sizes

| Buffer | PC | Xbox |
|--------|-----|------|
| Read | 64KB | 64KB |
| Write | 2MB | 10KB |

The PC version uses a much larger write buffer (2MB vs 10KB) since it writes to HDD rather than memory cards.

### Version Stamp Formats

Retail/Steam uses a **16-bit version word** at file offset `0x0000`:

- `0x4BD1` (little-endian `d1 4b`)
- Retail `BEA.exe` validates only this word during `CCareer::Load`.

The internal source snapshot has its own versioning helpers, but that code is not the retail persistence layer. Do **not** rely on any internal-build “version + sizeof(CCareer)” formulas unless you have verified them against the retail binary.

### Steam Release Save Format

**File size**: 10,004 bytes (verified)

| Offset | Size | Content |
|--------|------|---------|
| 0x0000 | 2 bytes | Version word (0x4BD1) |
| 0x0002 | 10,002 bytes | CCareer dump + options entries + tail snapshot (Steam build observed fixed layout/size) |

**Note (Feb 2026)**: Retail `BEA.exe` validates the **16-bit version word** and copies CCareer bytes from/to `buffer + 2`. Many hex dumps show the first 4 bytes as `0x00004BD1` because the next 16 bits after the version word are often zero.

### Xbox Save Header (CXBoxSaveHeader)

Xbox saves include a tamper-detection header:

| Field | Type | Value | Purpose |
|-------|------|-------|---------|
| `mMagic` | char[4] | "NEKO" (0x4F4B454E) | File identification |
| `mVersion` | int | 100 | Header version |
| `mSig` | XCALCSIG_SIGNATURE | (varies) | Xbox signature for tamper detection |

The "NEKO" magic is likely a developer in-joke (Japanese for "cat").

### Memory Card Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `MAX_MEMORY_CARD_SAVES` | 4096 | Maximum saves per memory card |
| `XBOX_BLOCK_SIZE` | 16384 | 16KB per block on Xbox |
| `TOTAL_XBOX_CARDS` | 9 | 8 Memory Unit slots + 1 HDD |

### Platform-Specific File Operations

**PC (CPCStorage/CDXMemBuffer)**:
- Uses standard Win32 file I/O
- Buffered reads/writes for performance
- No signature or tamper detection
- `IsHDDAvailable()` always returns FALSE in stubbed PCMemoryCard.cpp

**Xbox (CXBOXStorage)**:
- Block-aligned I/O (16KB blocks)
- XCALCSIG signatures for tamper detection
- Supports 8 Memory Unit slots + HDD
- Save titles stored in Unicode

**PS2 (CPS2Storage)**:
- Memory card I/O via Sony SDK
- 8KB block alignment
- Icon data for memory card display

### Relevance to Save Editing

**CRITICAL** - This section explains:

1. **Why the version word is 0x4BD1**: Retail `BEA.exe` validates a 16-bit version word at file offset `0x0000`
2. **Why Steam saves are 10,004 bytes**: `BEA.exe` bulk-copies CCareer from/to `file + 2` and includes an options entries block plus a fixed 0x56 tail snapshot. The binary computes size as `0x2514 + 0x20*N`, but in the Steam build we’ve only observed `N=16` (so treat `.bes` as fixed-size in tooling).
3. **Why there's no Xbox signature in Steam saves**: The retail Windows build uses normal PC storage (no XCALCSIG tamper header)
4. **Why PCMemoryCard is stubbed**: PC version uses direct file I/O, not memory card abstraction

### Files Analyzed for This Section

| File | Purpose |
|------|---------|
| `storage.cpp` | CStorage base implementation |
| `storage.h` | CStorage class definition, platform #ifdefs |
| `DXMemBuffer.cpp` | CDXMemBuffer PC/Xbox buffered I/O |
| `DXMemBuffer.h` | CDXMemBuffer class definition |
| `MemoryCard.h` | CMEMORYCARD class, MCE_* error codes |
| `PCMemoryCard.cpp` | **EMPTY STUB** - `IsHDDAvailable()` returns FALSE |
| `PCMemoryCard.h` | PCMemoryCard class definition |

---

## Serialization Sentinel Value

```cpp
#define END_OF_DATA 0x12345678  // well, why not..
```

This sentinel may appear at the end of data sections. Worth checking .bes files for this value.

---

## MKID Macro for Chunk Identification

```cpp
#define MKID(foo) UINT(((foo)[0]) + ((foo)[1]<<8) + ((foo)[2]<<16) + ((foo)[3]<<24))
```

Creates 4-byte identifiers from string literals in little-endian. Example: `MKID("CARE")` = `0x45524143`.

---

## Memory Card Abstraction Layer (MemoryCard.cpp/h)

> Analysis added December 2025

The memory card system provides a platform-agnostic abstraction layer for save file operations across PC, PS2, and Xbox. This is particularly relevant for understanding how the game handles `.bes` career files.

### Architecture Overview

```
CMemoryCard (base class - abstract interface)
    ├── CPCMemoryCard (stub implementation)
    ├── CPS2MemoryCard (not present in the current reference snapshot)
    └── CXBoxMemoryCard (full implementation)
```

**Platform Selection** (MemoryCard.h lines 88-103):
```cpp
#if TARGET==PS2
#define CMEMORYCARD CPS2MemoryCard
#include "PS2MemoryCard.h"
#elif TARGET==XBOX
#define CMEMORYCARD CXBoxMemoryCard
#include "XBoxMemoryCard.h"
#else
#define CMEMORYCARD CPCMemoryCard
#include "PCMemoryCard.h"
#endif
```

The global singleton `MEMORYCARD` provides access to platform-specific implementation.

---

### Memory Card Error Codes

| Constant | Value | Description |
|----------|-------|-------------|
| `MCE_SUCCESS` | 0 | Operation completed successfully |
| `MCE_FAILURE` | 1 | Generic failure |
| `MCE_NOCARD` | 2 | No memory card present |
| `MCE_UNFORMATTED` | 3 | Card is unformatted |
| `MCE_CORRUPT` | 4 | Save file is corrupt |
| `MCE_CARDFULL` | 5 | Card is full |
| `MCE_FILEEXISTS` | 6 | File already exists (when creating) |
| `MCE_NOFILE` | 7 | File does not exist (when reading) |
| `MCE_TOO_MANY_SAVES` | 8 | Maximum save count reached |

---

### Memory Card Types

| Constant | Value | Description |
|----------|-------|-------------|
| `MCT_CARD` | 0 | Standard memory card |
| `MCT_HDD` | 1 | Hard disk drive (Xbox HDD or PC) |

---

### Key Constants

| Constant | Value | Notes |
|----------|-------|-------|
| `MAX_MEMORY_CARD_SAVES` | 4096 | Maximum saves per card |
| `XBOX_BLOCK_SIZE` | 16384 | Xbox storage block size (16 KB) |
| `TOTAL_XBOX_CARDS` | 9 | 8 MU slots + 1 HDD |
| `MAX_NAME_LEN` | 40 | Maximum save name length |
| `SAVE_FILE_NAME` | "SAVE.DAT" | Internal file within Xbox save folder |

---

### CMemoryCard Base Class Interface

```cpp
class CMemoryCard {
public:
    // Lifecycle
    void InitialiseOnce();      // One-time global init
    void Initialise();          // Per-level init
    void Shutdown();            // Cleanup

    // Card Detection
    BOOL IsHDDAvailable();
    int  GetNumCards(int *num);
    int  GetCardInfo(int card, BOOL *present, BOOL *formatted,
                     int *bytesfree, int *bytestotal);
    int  GetCardName(int card, WCHAR *buffer);
    int  GetCardType(int card, int *cardtype);

    // Card Management
    int  Format(int card);      // Format card
    int  Unformat(int card);    // Unformat card

    // Save Enumeration
    int  GetNumSaves(int card, int *num);
    int  GetSaveName(int card, int save, WCHAR *name);

    // Save Operations
    int  CreateSave(int card, WCHAR *name, int *save, BOOL allowed_overwrite);
    int  DeleteSave(int card, int save, WCHAR *name);
    int  WriteSave(int card, int save, WCHAR *name, void *data, int datasize);
    int  ReadSave(int card, int save, WCHAR *name, void *data, int datasize, int *bytesread);

    // Utility
    int  GetSaveSize(int datasize, int *savesize);
    int  MakeHumanReadableSize(int bytes, WCHAR *buffer);
    bool Update();              // Hot-swap detection
    BOOL CardBeenUnpluggedSinceLastTimeIAsked(int card);
};
```

---

### PC Implementation (CPCMemoryCard)

**Key Insight**: The PC implementation is a **complete stub** that does nothing!

```cpp
class CPCMemoryCard : public CMemoryCard {
public:
    void InitialiseOnce() {};
    void Initialise() {};
    void Shutdown() {};

    BOOL IsHDDAvailable() { return(FALSE); };  // Always FALSE!
    int  GetNumCards(int *num) { *num=0; return(MCE_SUCCESS); };
    // All operations return MCE_SUCCESS but do nothing
};
```

**Important Discovery**: This internal snapshot does not use a functional MemoryCard path for PC saves. Retail PC persistence follows a different, binary-verified path and should not be inferred solely from these stubs.

The only non-stub method loads the save game icon texture for Xbox compatibility:
```cpp
void CPCMemoryCard::AccumulateResources(CResourceAccumulator *ra, DWORD flags) {
    CTEXTURE *saveimage = CTEXTURE::GetTextureByName(
        "FrontEnd\\v2\\FE_XB_SaveGame.tga", TEXFMT_UNKNOWN, TEX_NORMAL, 1);
    saveimage->AccumulateResources(ra, flags | RES_NOTONPS2);
    saveimage->Release();
}
```

---

## Xbox Memory Card System (XBoxMemoryCard.cpp/h)

> Analysis added December 2025

The Xbox implementation is comprehensive and provides insight into the original console save system.

### Class Structure

```cpp
class CXBoxMemoryCard : public CMemoryCard {
    // Full implementation of abstract CMemoryCard interface
    // Handles Memory Units, HDD, hot-swap detection, Dashboard integration
};
```

`CXBoxMemoryCard` extends `CMemoryCard` base class, implementing all abstract methods for Xbox-specific storage hardware.

---

### Storage Slots

```cpp
#define TOTAL_XBOX_CARDS 9  // 8 MU slots + 1 HDD
```

| Card Index | Description | Port/Slot |
|------------|-------------|-----------|
| 0-1 | Controller Port 0 MUs | XDEVICE_PORT0, TOP/BOTTOM |
| 2-3 | Controller Port 1 MUs | XDEVICE_PORT1, TOP/BOTTOM |
| 4-5 | Controller Port 2 MUs | XDEVICE_PORT2, TOP/BOTTOM |
| 6-7 | Controller Port 3 MUs | XDEVICE_PORT3, TOP/BOTTOM |
| -1 or 8 | Hard Drive | Always present, MCT_HDD type |

```cpp
DWORD GetPort(int card) {
    if ((card==0) || (card==1)) return XDEVICE_PORT0;
    else if ((card==2) || (card==3)) return XDEVICE_PORT1;
    else if ((card==4) || (card==5)) return XDEVICE_PORT2;
    else return XDEVICE_PORT3;
}

DWORD GetSlot(int card) {
    if ((card==0) || (card==2) || (card==4) || (card==6))
        return XDEVICE_TOP_SLOT;
    else
        return XDEVICE_BOTTOM_SLOT;
}
```

---

### Save File Format

```cpp
#define XBOX_BLOCK_SIZE 16384       // 16 KB per block
#define SAVE_FILE_NAME  "SAVE.DAT"  // Career data within save container
```

#### CXBoxSaveHeader Structure

```cpp
class CXBoxSaveHeader {
public:
    DWORD               mMagic;     // "NEKO" (0x4F4B454E)
    DWORD               mVersion;   // Always 100
    XCALCSIG_SIGNATURE  mSig;       // Xbox cryptographic signature

    void CreateHeader(BYTE *data, DWORD datasize);
    BOOL CheckHeader(BYTE *data, DWORD datasize);
};
```

**Easter Egg**: The magic `MKID("NEKO")` = "NEKO" (Japanese for "cat") - likely Lost Toys studio mascot or team joke.

#### Signature Verification

Uses Xbox SDK's cryptographic signing APIs:
- `XCalculateSignatureBegin()` - Initialize signature context
- `XCalculateSignatureUpdate()` - Hash data blocks
- `XCalculateSignatureEnd()` - Finalize signature

Signatures prevent save file tampering and are verified on load via `CheckHeader()`.

---

### Dashboard Integration

```cpp
#define XBOX_DASH_ID (0xB16B00B5)  // "BIG BOOBS" in l33tspeak - developer joke
```

The Dashboard ID is passed when launching Xbox Dashboard for memory management and returned when user exits back to game.

#### Save Thumbnail

- **Dimensions**: 64x64 pixels
- **Format**: DXT1 compressed
- **Output file**: `saveimage.xbx` (within save container)
- **Source asset**: `FrontEnd\v2\FE_XB_SaveGame.tga`

```cpp
// From CPCMemoryCard::AccumulateResources (loads same asset for compatibility)
CTEXTURE *saveimage = CTEXTURE::GetTextureByName(
    "FrontEnd\\v2\\FE_XB_SaveGame.tga", TEXFMT_UNKNOWN, TEX_NORMAL, 1);
```

---

### Hot-Swap Detection

```cpp
enum UpdateReason {
    NO = 0,           // Doesn't need updating
    UNPLUGGED = 1,    // Card removed
    PLUGGED = 2,      // Card inserted
    MODULE_INIT = 3   // Memory card module initialized
};
```

```cpp
bool Update() {
    DWORD insertedcards, removedcards;
    XGetDeviceChanges(XDEVICE_TYPE_MEMORY_UNIT, &insertedcards, &removedcards);
    // Process bit masks for all 8 MU slots...
}
```

- **Device bitmap tracking**: Monitors insertion/removal across all 8 MU slots
- **File timestamp verification**: `CardBeenUnpluggedSinceLastTimeIAsked()` detects if a different card was swapped in since last save

---

### TCR Compliance

**TCR 1.7-2-22**: Full memory units must be reported as unformatted.

```cpp
// XBoxMemoryCard.cpp line 322
// "Because of TCR 1.7-2-22 let's just pretend it's crap. Even though we've
// written all the code to allow the user to go to the Dash and sort it out."
```

When an MU is completely full with no free space, the game reports it as "unformatted" rather than "full" to avoid confusing error messaging. Microsoft certification required this behavior.

---

### Save Size Calculation

```cpp
int GetSaveSize(int datasize, int *savesize) {
    *savesize = datasize + sizeof(CXBoxSaveHeader);
    *savesize += (2 * XBOX_BLOCK_SIZE);  // Icon file (~32KB)

    // Force minimum of 5 blocks (80KB)
    int bigsize = XBOX_BLOCK_SIZE * 4 + XBOX_BLOCK_SIZE / 2;
    if (*savesize <= bigsize) {
        *savesize = bigsize;
    }
    return MCE_SUCCESS;
}
```

Xbox save occupies at least 5 blocks (80KB):
- Career data (~10KB)
- Header with signature
- Save image icon (64x64 DXT1)
- Padding to minimum

---

### Xbox Save File Structure

```
Xbox Save Container (folder named after save)
├── saveimage.xbx         (64x64 DXT1 icon)
└── SAVE.DAT              (actual career data)
    ├── CXBoxSaveHeader   (NEKO magic + version + signature)
    └── CCareer           (raw struct data, ~10,000 bytes)
```

Compare to PC `.bes` files (simpler):
```
career.bes
├── Version word  (2 bytes: 0x4BD1)
└── CCareer bytes + options entries + tail snapshot (10,002 bytes total, starting at `file + 2`)
```

PC has no header signature or icon - just raw data.

---

### Developer Comments

| Line | Quote |
|------|-------|
| 322 | "Because of TCR 1.7-2-22 let's just pretend it's crap." |
| 1027 | "he's whipped the card out with ninja-like speed." |
| 1239 | "sorry the fact either \| or \|\| (pun intended) would work is delightful." |
| 1386 | "oh dear, couldn't mount this. Story of my life." |

#### Font Hijacking Workaround

```cpp
// Some characters in the memory card names aren't valid in our font
// because we've nicked them for special characters such as joypad buttons.
for (WCHAR *walker = mCardName[card]; *walker; walker++) {
    for (const WCHAR *lookup_walker = CBitmapFont::HIJACKED_FONT_ENTRIES; *lookup_walker; lookup_walker++) {
        if (*walker == *lookup_walker) {
            *walker = 0xdead;  // Replace with null character
            break;
        }
    }
}
```

---

### Integration with Career System

```cpp
// Conceptual flow (reconstructed from context)
void SaveCareer() {
    MEMORYCARD.CreateSave(card, savename, &save, overwrite);
    MEMORYCARD.WriteSave(card, save, savename, &CAREER, sizeof(CCareer));
}

void LoadCareer() {
    int bytesread;
    MEMORYCARD.ReadSave(card, save, savename, &CAREER, sizeof(CCareer), &bytesread);
}
```

The retail build computes save size via `CCareer::GetSaveSize()` and serializes bytes beginning at `file + 2` after a 16-bit version word. In the Steam build we patch here, `.bes` is **observed fixed at 10,004 bytes** (size formula yields that with `N=16`), so do not resize saves without separate build verification.

---

### PS2 Implementation Note

The PS2 implementation (`CPS2MemoryCard`) was not included in Stuart's source code dump. Based on the pattern, it would handle PlayStation 2 memory card I/O using Sony's libmc or similar APIs, with the 8MB card constraint and potentially different save file formatting.

---

### Files Analyzed for This Section

| File | Purpose |
|------|---------|
| `MemoryCard.cpp` | Base class implementation (stub) |
| `MemoryCard.h` | Abstract interface, error codes, platform routing |
| `PCMemoryCard.cpp` | PC stub (only texture loading) |
| `PCMemoryCard.h` | PC class definition (all methods are no-ops) |
| `XBoxMemoryCard.cpp` | Full Xbox MU/HDD implementation |
| `XBoxMemoryCard.h` | Xbox class definition, constants |

---
