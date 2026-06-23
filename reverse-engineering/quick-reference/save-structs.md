Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
Summary: BES/CCareer struct layout lookup.
# BES Struct Layouts (Retail/Steam)

This is a concise reference for the **retail/Steam** `.bes` layout used by the current patchers in this repo.

**True dword view reminder:** `BEA.exe` copies `CCareer` bytes from/to `file + 2` after a 16-bit version word, so patch using `file_off = 0x0002 + career_off`.

## CCareerNode (64 bytes)

```c
struct CCareerNode {
    /* +0x00 */ uint32_t state;           // Flags/legacy (not fully mapped). Preserve unless experimenting.
    /* +0x04 */ uint32_t mComplete;       // Raw BOOL/int (0/1 observed in retail saves)
    /* +0x08 */ int32_t  mLowerLink;      // Link index (into CCareerNodeLink[200])
    /* +0x0C */ int32_t  mHigherLink;     // Link index (into CCareerNodeLink[200])
    /* +0x10 */ int32_t  mWorldNumber;    // Level ID (100, 110, 200...)
    /* +0x14 */ int32_t  mBaseThingsExists[9];  // 288 persistence bits (level-specific; preserve)
    /* +0x38 */ int32_t  mNumAttempts;    // Attempt counter
    /* +0x3C */ uint32_t mRanking;        // Raw IEEE-754 float bits (rank)
};
// Total: 64 bytes
```

**Ranking bits (true view):**
- S: `0x3F800000` (1.0)
- A: `0x3F4CCCCD` (0.8)
- B: `0x3F19999A` (0.6)
- C: `0x3EB33333` (0.35)
- D: `0x3E19999A` (0.15)
- E: `0x00000000` (0.0)
- NONE: `0xBF800000` (-1.0)

## CCareerNodeLink (8 bytes)

```c
struct CCareerNodeLink {
    /* +0x00 */ uint32_t mLinkType;  // Raw (0/1 observed; preserve unknown values)
    /* +0x04 */ int32_t  mToNode;    // Destination node index (0xFFFFFFFF for unused)
};
```

## CGoodie (4 bytes)

```c
struct CGoodie {
    /* +0x00 */ uint32_t state;  // Raw 0/1/2/3 in true dword view
};
```

Goodie states (true view):
- 0 = UNKNOWN
- 1 = INSTRUCTIONS
- 2 = NEW (gold)
- 3 = OLD (blue)

## Kill Counters (5 dwords)

Each counter is packed:

`stored = (meta << 24) | (kills & 0x00FFFFFF)`

Preserve `meta` when patching.

## Tech Slots (mSlots[32])

CCareer offset: `0x2408` (file offset `0x240A` in true view)

```c
// Set slot N:
mSlots[N >> 5] |= (1 << (N & 31));
// Test slot N:
(mSlots[N >> 5] & (1 << (N & 31))) != 0;
```

Known slot meanings (from Stuart’s source):
- 61: `SLOT_500_ROCKET`
- 62: `SLOT_500_SUB`

## Constants

```c
#define NUM_LEVELS       43
#define MAX_NODES       100
#define MAX_LINKS       200
#define MAX_NUM_GOODIES 300
#define MAX_CAREER_SLOTS 32
```
