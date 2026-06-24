# Resolved Archive

> Historical record of completed investigations and fixed bugs.

**Note (Feb 2026):** Many Dec 2025 investigations used a legacy 4-byte aligned hex view (`file_off % 4 == 0`). Retail/Steam `.bes` stores a 16-bit version word at `0x0000` and bulk-copies CCareer bytes from/to `file + 2`, so the **true dword boundaries** are at offsets where `file_off % 4 == 2`. For CCareer struct offsets, use:

```text
file_off = 0x0002 + career_off
```

## RESOLVED: Level Crash Bug (Dec 2025)

**Root Cause (updated Feb 2026)**: Early patchers wrote link state values at the **wrong dword alignment** (legacy aligned view). Those writes overlapped adjacent true dwords and corrupted unrelated bytes in/around the links region, causing crashes (notably on Evo levels).

### The Fix (True View + Minimal Change)

```python
# Link layout (true view): [0]=linkState/type, [4]=toNode (0xFFFFFFFF for unused).
# Preserve non-zero types (e.g., "2" is seen in real saves).
to_node = read_u32(buf, link_off + 4)
if to_node != 0xFFFFFFFF:
    current = read_u32(buf, link_off)
    if current == 0:
        write_u32(buf, link_off, 1)
```

### Evidence Chain

1. Node data for crashing levels was identical between working (gold) and broken (early patched) saves.
2. The early patcher wrote link dwords at legacy aligned offsets, producing differences that were not semantically valid in the true view.
3. After patching link dwords using the true view mapping and preserving existing non-zero link types: levels no longer crash.

---

## RESOLVED: Missing Goodie Bug (Dec 2025)

**Root Cause (updated Feb 2026)**: The patcher wrote to a legacy aligned offset (`0x22D4`) believing it was `mCareerInProgress`. In the true view, that write is misaligned and corrupts a neighboring goodie.

### The Problem (Offsets)

```text
Legacy aligned view (deprecated):
  0x22D4 was treated as mCareerInProgress (incorrect)

True view (retail/Steam):
  mCareerInProgress file offset = 0x248A  (CCareer +0x2488)
  Goodies file base             = 0x1F46  (CCareer +0x1F44)
  Goodie 228 file offset        = 0x22D6
```

### The Fix

Do not write to `0x22D4` as if it were `mCareerInProgress`. The save works without setting `mCareerInProgress` at all.

---

## RESOLVED: Rank Display (Dec 2025)

**Root Cause (updated Feb 2026)**: Earlier "split-float" conclusions were caused by interpreting the file in the legacy aligned view. In retail/Steam the rank is stored as raw float bits.

### The Solution

Ranking is stored as raw IEEE-754 float bits in `CCareerNode + 0x3C` (`mRanking`).

| Rank | Float | Bits |
|------|-------|------|
| S | 1.0 | 0x3F800000 |
| A | 0.8 | 0x3F4CCCCD |
| B | 0.6 | 0x3F19999A |
| C | 0.35 | 0x3EB33333 |
| D | 0.15 | 0x3E19999A |
| E | 0.0 | 0x00000000 |
| NONE | -1.0 | 0xBF800000 |

---

## RESOLVED: God Mode Investigation (Dec 2025)

**Status**: Tested. Steam build behavior appears to be driven by runtime cheat checks (save-name substring match). The persisted pause-menu toggle state exists, but per-player persisted god flags were mis-identified in older notes.

### Correct Offsets (True View, Retail/Steam)

| File Offset | Field | Notes |
|------------:|-------|------|
| 0x2496 | g_bGodModeEnabled | Runtime toggle state persisted in the CCareer dump |
| 0x249A | (unused/padding) | Observed 0 in Steam saves/options; preserve |
| 0x249E | Invert Y (Flight/Jet) (P1) | Steam stores `0=Off`, non-zero=On (verified in `FUN_00407540`) |

### Notes

- The internal/source cheat is `B4K42` (save-name substring).
- Retail/Steam uses `Maladim` (save-name substring) and also includes additional cheat codes not present in the internal source.
- **Steam build correction (Feb 2026):** offsets previously written up as `mIsGod[]` are used by the Controls UI for invert-Y; do not treat them as persisted god flags.

---

## RESOLVED: Tech Slots Location (Dec 2025)

**Previous belief**: Tech slots at 0x244C (legacy aligned view confusion)

**Actual location (true view)**: `mSlots` is at CCareer offset `0x2408`, file offset `0x240A` (128 bytes = 32 ints).

### Evidence

- Binary/source logic uses standard bit operations: `mSlots[slot >> 5] |= (1 << (slot & 31))`
- Retail/Steam saves show non-zero slot bitfields in the `0x240A` region in the true view.

---

## SOLVED: E-Rank Encoding (Dec 2025)

E is `0.0f` (`0x00000000` bits) in the node `mRanking` field.

Source logic (internal build) maps `f <= 0` to `E`:

```cpp
if (f == 1.f) c = 'S';
else if (f <= 0.f) c = 'E';
else c = 'D' - floor(f * 4);
```

Retail/Steam note: `NONE` is represented by `-1.0f` (`0xBF800000`) but rendering/handling may vary.

---

## Completed Tasks Checklist

- [x] Fix level crashes (true dword view offsets; minimal link patching)
- [x] Fix rank display (raw float bits in node `mRanking`)
- [x] Fix goodie overlap confusion (avoid legacy aligned writes like 0x22D4; patch in true view)
- [x] Multiplayer levels accessible (links completed where used)
- [x] Kill count offset fix (true view base 0x23F6; preserve meta byte)
- [x] E-rank encoding (0.0f bits displays E)
- [x] Trace IsEpisodeAvailable() (documented in source analysis)
- [x] Code parity Python/C# save patching and analysis
