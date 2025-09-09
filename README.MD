# Battle Engine Aquila *.bes* — Comprehensive Save-File Reference

*Last consolidated: 2025-05-02 12:59 EDT*

---

## 0a Current editor state

- All levels currently unlock with a rank of D regardless of rank selected.
- Goodies all unlock depending on toggle (marked NEW or OLD based on the setting).
- Multiplayer levels are all unlocked.

---

## 0 Quick facts

- **File size:** 10 004 B (4-byte stamp + struct)
- **Endian:** Little-endian (Xbox & PC builds)
- **Version stamp:** `0x00004BD1` (bytes 0x0000–0x0003)
- **Shift-16 rule:** *every* 32-bit integer in the original game is stored left-shifted by 16 bits (fixed-point 16.16). Example – `TRUE` → `0x0001 0000`.
- **Floats:** Raw IEEE-754 (`mRanking`, etc.)

---

## 1 File skeleton

| Section | Offset | Count | Entry size | Notes |
|---------|-------:|------:|-----------:|-------|
| Version stamp | 0x0000 | 1 | 4 B | Observed `0x00004BD1` in retail `.bes` (varies in sources) |
| `CCareerNode[100]` | 0x0004 | 100 | **64 B** | Per-mission data |
| `CCareerNodeLink[200]` | 0x1904 | 200 | **8 B** | Directed graph edges |
| Goodies (300) | 0x1F44 | 300 | 4 B | Unlockables (hi-word = state << 16) |
| Global kills (5) | 0x23A4 | 5 | 4 B | Kill totals driving certain goodies |
| Flags / slots / config | 0x22D4… | – | – | e.g. `mCareerInProgress`, god-mode, tech slots |
| **Total length** | — | — | — | 10 004 B |

---

## 2 `CCareerNode` layout (64 B each)

| Offset | Type | Name | Meaning |
|------:|------|------|--------|
| `+0x00` | int <<16 | `mIsStartOfNewIsland` | Unused flag |
| `+0x04` | int <<16 | **`mComplete`** | 0 = incomplete, **`TRUE32`** draws ✓ |
| `+0x08` | int <<16 | `mLowerLink` | Index → link array |
| `+0x0C` | int <<16 | `mHigherLink` | Index → link array |
| `+0x10` | int <<16 | **`mWorldNumber`** | 100, 110… |
| `+0x14` | 9 × int <<16 | `mBaseThingsExists` | Persistence & objective bits |
| `+0x38` | int <<16 | **`mNumAttempts`** | See ranking rules↓ |
| `+0x3C` | float | **`mRanking`** | Score / letter grade |

Note: On PC, this editor writes a sentinel float `-1.0f` (`0xBF80_0000`) at `+0x00` to engage the UI's grade computation path. This overwrites the legacy `mIsStartOfNewIsland` flag.

### 2.1 Ranking behaviour

| Scenario | Loader expectation | Practical advice |
|----------|--------------------|------------------|
| **Legit run** | `mNumAttempts > 0` and full stats block | OK |
| **Synthetic rank** | If `mNumAttempts ≠ 0`, loader **zeros `mRanking`** | **Keep `mNumAttempts = 0` when injecting** |

Two distinct grade tables are observed:

1. **Retail PC build UI (float 0-1):**

| Grade | `mRanking` |
|-------|-----------|
| S | ≥ 1.00 |
| A | ≥ 0.75 |
| B | ≥ 0.50 |
| C | ≥ 0.25 |
| D | ≥ 0.00 |
| E | < 0 |

1. **Console code (score 0-1 050 000):** 800 000 = “A”, 1 050 000 = “S”. When in doubt, use 900 000 + for **S**.

---

## 3 `CCareerNodeLink` layout (8 B each)

| Offset | Type | Name | Meaning |
|------:|------|------|--------|
| `+0x00` | int <<16 | **`mLinkType`** | 0 = NOT_COMPLETE, **`TRUE32`** = COMPLETE |
| `+0x04` | int <<16 | `mToNode` | Destination node index |

---

## 4 Goodies & globals

### 4.1 Goodies (300 × 4 B)

- Base offset `0x1F44 + 4 × id`
- State enum (`UNKNOWN=0`, `INSTR=1`, **`NEW=2`**, **`OLD=3`**) is stored in **high word** (after shift-16).

Note: The contiguous goodies region runs up to `0x23A4` (≈ 280 entries). Beyond that, goodies interleave with flags (`0x22D4…`) and kills (`0x23A4`). The editor writes all 300 goodies and then overwrites overlapping addresses with the intended flags/kills.

### 4.2 Global kill counters (5 × 4 B @ 0x23A4)

Increment to satisfy loader sanity checks when awarding kill-based goodies.

### 4.3 Career / flags / slots

| Offset | Size | Purpose |
|------:|-----:|---------|
| 0x22D4 | 1 B | **`mCareerInProgress`** (`01` = started) |
| 0x240C | 4 B | **`mIsGod[0]`** (`0x0001 0000` = god-mode) |
| 0x244C | 32 × 4 B | Tech slot bit-field (WIP) |
| … | … | Other debug flags (TBD) |

---

## 5 Practical patch recipes

### 5.1 Unlock **one** mission with retained grade

```python
TRUE32  = 0x0001_0000
SCORE   = 900_000.0      # Grade S on console; use 1.0 for PC UI

# per-node (off = start of node)
patch32(buf, off + 0x04, TRUE32)   # mComplete ✓
patch32(buf, off + 0x38, 0)        # mNumAttempts = 0 (critical!)
struct.pack_into('<f', buf, off+0x3C, SCORE)
```

### 5.2 Unlock **all** missions & goodies

```python
for n in range(100):
    off = 0x0004 + n*64
    patch32(buf, off + 0x04, TRUE32)
    patch32(buf, off + 0x38, 0)
    struct.pack_into('<f', buf, off+0x3C, SCORE)

for l in range(200):
    patch32(buf, 0x1904 + l*8, TRUE32)              # mLinkType

for gid in range(300):
    patch32(buf, 0x1F44 + gid*4, 0x0003_0000)       # mark OLD

# ensure career flag & kills
buf[0x22D4] = 1
for i in range(5):
    patch32(buf, 0x23A4 + i*4, TRUE32)
```

### 5.3 Toggle god-mode (invulnerable)

```python
# single dword: mIsGod[0]
patch32(buf, 0x240C, 0x0001_0000)  # TRUE32 → god-mode on
```

### 5.4 Show an ‘S’ immediately (RAM-only)

*Works until you restart the game.*

```python
# assumes the node offset is already known
patch32(buf, node+0x38, 0)                  # mNumAttempts = 0
struct.pack_into('<f', buf, node+0x3C, 1_050_000.0)  # high score
patch32(buf, node+0x18, 0x0007_0000)        # objective bit-mask (all objectives)
```

---

## 6 Why letter grades default to “E/D”

The mission-select UI recalculates the grade the first time you highlight a mission tile.
It relies on an in-RAM *EndLevelData* block (time, accuracy, objectives, kills). If that
block is missing—as is the case for any mission you have never completed legitimately—
the fallback is the placeholder grade **E/–** (or **D** in some builds/UI paths), ignoring `mRanking`.

`EndLevelData` is only written to the save when you press **Continue** after the debrief
screen. Therefore grades cannot be permanently pre-seeded without replicating the entire
hidden structure—outside the scope of simple byte-patch scripts.

---

## 7 Credits

- Foundational PC source and guidance by desimbr (aka [stuart73](https://github.com/stuart73)). Without this work, this editor would not exist.
- C++ symbols & structs: `Career.cpp`, `Career.h`
- Fixed-point 16.16 heritage confirmed via original Xbox build
- Hex-diffing & runtime verification by the BEA reverse-engineering community

---

## 8 Open questions

- Confirm exact **max score** tolerated before loader clamps / zeros.
- Map secondary-objective bits inside `mBaseThingsExists[9]` for perfect S.
- Catalogue god-mode & debug flags in the global block.

---

> This document merges and supersedes previous notes (*distilled*, *full reference*, *SITREP*).

---

## 9 Known limitations

- Rank forcing is currently unreliable. Regardless of UI selection, in-game typically shows D due to grade recomputation from hidden EndLevelData.
- The editor does not rebuild EndLevelData; displayed grades may not reflect `mRanking` fields.
- Objective mask is written at `node+0x18` (`0x0007_0000` for all objectives) and may vary by build.
- God mode impacts Free-Play only. Tech slot management is WIP.

## 10 Contributing

- Build: Visual Studio 2022, .NET 9 SDK, Windows, WPF. Open `Onslaught - Career Editor.sln`, build `net9.0-windows`.
- Run: Launch the app, select an input `.bes`, choose options, patch to a new file.
- Help wanted:
  - Stable rank injection without EndLevelData.
  - Map secondary-objective bits in `mBaseThingsExists`.
  - Verify offsets across platforms; expand god-mode/flags catalog.
  - Improve tech slot tooling and tests.

## 11 License

This repository is licensed under the MIT License (see `LICENSE`). The `Onslaught/` directory is local reference only and is not part of the public repository.
