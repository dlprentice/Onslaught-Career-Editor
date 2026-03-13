# Known Bugs

## Resolved Bugs

### Patched Saves Cause Level Crashes - RESOLVED (Dec 2025)

**Affected levels**: "Assault Force Fenrir (Evo)", "Air Raid (Evo)", possibly others
**Confirmed by**: desimbr (Sept 2025)
**Status**: FIXED - All levels now work including Evo missions
**Root Cause (updated Feb 2026)**: Early patchers were writing to the **wrong dword alignment** (legacy 4-byte aligned view). Retail `BEA.exe` copies CCareer bytes from/to `file + 2`, so those writes overlapped adjacent true dwords and corrupted unrelated state (notably in the links region).
**Fix (current tools)**: Patch using the **true dword view** offsets (`file_off = 0x0002 + career_off`) and make **minimal link changes** (only set state `0 -> 1`, preserve other non-zero values like `2`).

**Timeline from #game-dev**:
- Sept 9, 2025 - David releases Career Editor v0.1.0
- Sept 10, 2025 - Stuart reports: "Most levels work but some levels like 'assault force fenrir (evo)' and 'air raid (evo)' crash for me when the level is about to start."
- Sept 10, 2025 - superdeveloper1337 confirms crashes on Steam version
- Sept 11, 2025 - Stuart confirms: **"I can confirm the patched save files are causing my crash. I've tried that 'gold save' .bes file and that works fine."**

---

### Kill Count Offset Bug - RESOLVED (Dec 2025)

**Problem**: Kill counts were documented at offset 0x23A4 (legacy aligned view)
**Actual (true view)**: Kill counts start at offset 0x23F6 (5 dwords)
**Impact**: Patcher was writing to goodies array (280-284) instead of kill counters
**Fix**: Updated all offsets in documentation and code

**Proof**:
- Gold save has 3,221/9,738/3,002/3,953/1,024 kills at 0x23F6 (true view), zeros at 0x23A6
- Organic gameplay save has 68/95/0/84/0 kills at 0x23F6 (true view), zeros at 0x23A6
- Patched saves were writing to 0x23A4 (legacy aligned view) (goodies!) with zeros at 0x23F6

---

### Goodie 228 Overlap Bug - RESOLVED (Dec 2025)

**Problem**: Offset 0x22D4 (legacy aligned view) was documented as `mCareerInProgress` flag
**Actual (true view)**: Goodie 228 is at 0x22D6 and `mCareerInProgress` is at 0x248A (no overlap)

```
GOODIE_BASE (CCareer) = 0x1F44
GOODIE_BASE (file, true view) = 0x1F46
Goodie 228 (file, true view) = 0x1F46 + (228 x 4) = 0x22D6

// Legacy aligned view (deprecated) placed “goodie 228” at 0x22D4.
```

Writing `buf[0x22D4] = 1` after writing goodies corrupted Goodie 228 from `0x00020000` to `0x00020001`.

**Solution**: Do NOT write to 0x22D4 as if it were `mCareerInProgress`. If you ever need `mCareerInProgress`, use the true view offset `0x248A`. The save works without setting progress.

---

## Open Bugs / Unresolved Issues

### God Mode Patching Does Not Work

**Status**: Investigated, determined to be by design
**Details**: See `/reverse-engineering/game-mechanics/god-mode.md` for full analysis
**Workaround (original/internal builds)**: Use in-game cheat code `B4K42` instead of save patching.  
**PC port note**: The Steam/console-port build uses `Maladim` for the god mode name check, but user testing shows no visible effect so far (no confirmed workaround).

---

## Original Game Bugs (from community)

### Tentacle Base Boss AI Bug

Halfway through the fight, the starting tentacles will sometimes target ally ships and stop shooting anything. Happens multiple times - not one-time bug. Cause unknown.

### Ranking System Issues

Some missions appear to have broken ranking - players report being unable to achieve certain grades no matter what they do. Stuart confirmed (March 3, 2023): "I don't have the values for each mission... They are hardcoded in the level data somewhere."

### Fenrir AI Bug (Steam version)

The Fenrir is supposed to attack the main HQ when it gets close enough, but on the Steam version it never attacks. Reported by BermudaMaster (Jan 2025).

### Red Aquila UI Bug (Co-op)

In co-op mode, the Red Aquila's visual indicators from the player's perspective are still blue. NDjeneralBN noted (July 2022): "I fought that originaly red aquila was never suposed to be playable in the first place." This suggests multiplayer was added late and the UI wasn't fully adapted for red team perspective.

---

## S-Rank Tips (from vandal_117, March 2023)

Community-sourced strategies for difficult S-ranks:

| Mission | Strategy |
|---------|----------|
| **Thunderhead (3.3)** | Lancer config speedrun start - got S first try |
| **Warspite (4.3)** | Don't destroy buildings in previous missions - save them for this mission's ranking |
| **Final Mission** | Beat boss in <4:20, then destroy all fighters. Time alone isn't enough - need kills too |

A community-contributed gold all-S save file was used during development and validation.

---

## Legacy Bug Fix: Misaligned Writes (Aligned View)

Older patching attempts treated the save as if dwords started at 4-byte aligned offsets (`file_off % 4 == 0`). In retail `BEA.exe`, CCareer bytes are copied from/to `file + 2`, so the real dword boundaries are at offsets where `file_off % 4 == 2`.

Writing “TRUE”/states at the **legacy aligned offsets** overlapped adjacent true dwords and corrupted unrelated bytes, causing crashes (notably on Evo levels).

**Fix (current tools):**
- Patch using the **true dword view** offsets (`file_off = 0x0002 + career_off`).
- Preserve packed metadata where observed (e.g. kill counters use `(meta<<24) | (kills & 0x00FFFFFF)`; preserve `meta`).
