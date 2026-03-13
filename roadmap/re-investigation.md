# RE Investigation (Archive)

> Historical investigation log. This file is not the canonical active queue.
> Current execution status lives in `roadmap/status-current.md` and `roadmap/ROADMAP-INDEX.md`; RE is a supporting lane.
> Canonical RE status lives in `reverse-engineering/binary-analysis/deep-validation-status.md`.

## Background RE Queue (Non-Blocking)

| Area | Status | Canonical Tracking |
|------|--------|--------------------|
| `mBaseThingsExists[9]` bit semantics | Backlog (targeted RE when app work needs evidence) | `reverse-engineering/save-file/struct-layouts.md` + subsystem contracts |
| Tech-slot bit meaning (`mSlots[32]`) | Backlog (partial mapping) | `roadmap/tech-slots.md` |
| Runtime god-mode behavior (`Maladim`) | Backlog (runtime-only path) | `reverse-engineering/game-mechanics/god-mode.md` |

## Superseded Investigations (Historical)

### Former "Mystery Region 3" Narrative

- [x] ~~Suspected EndLevelData cache at 0x24CC-0x2713~~ **RESOLVED**: EndLevelData is runtime-only and not serialized to `.bes`.
- [x] ~~0x24CC+ treated as unknown campaign cache~~ **RESOLVED**: save tail/options behavior is now documented; remaining bytes are tracked as reserved/unmapped and preserved.

## Known Unknowns

| Area | What's Unknown | Why It Matters |
|------|---------------|----------------|
| mBaseThingsExists bits | Which 288 bits control what | Level-specific objective state tracking |
| Tech slot bitmap | What each of 1024 bits enables | May unlock hidden features. Slots 61-62 control mission 500 branching |
| ~~EndLevelData cache~~ | ~~Per-level stats format at 0x24CC+~~ | **RESOLVED Dec 2025**: EndLevelData is runtime-only, never saved. See [resolved-archive.md](resolved-archive.md) |
| ~~God mode persistence~~ | ~~Steam per-player flags / Maladim path~~ | **TESTED Dec 12, 2025**: MP invincibility observed, SP not working. Steam offsets previously written up as `mIsGod[]` were incorrect (invert-Y). See [resolved-archive.md](resolved-archive.md) |
| Residual reserved bytes near 0x24C8-0x24CB | Exact semantics for remaining tail-adjacent bytes outside mapped P1/P2 fields | Value at 0x24C8 differs between saves |

## Unknown Unknowns (Blind Spots)

| Area | Risk | Mitigation |
|------|------|------------|
| Hidden checksums | Save could have integrity checks | Test modified saves extensively |
| Runtime dependencies | Some values may require game state | Compare active memory vs save file |
| Platform differences | Xbox/PS2/PC may differ | Test on multiple platforms if possible |
| Version differences | Steam updates may change format | Test with different game versions |
| Multiplayer state | MP unlocks may have separate storage | Investigate MP-specific saves |

## Hex Patterns to Search For

```
0x12345678  - END_OF_DATA sentinel from source code
0x4BD1      - Version word (16-bit at offset 0x0000; the first 4 bytes may *look* like 0x00004BD1 if the next 16 bits are zero)
0xFFFFFFFF  - Might mark uninitialized/unused slots
0xDEADBEEF  - Common debug marker
0x45524143  - "CARE" in little-endian (MKID macro)
```

## Save File Comparison Opportunities

| Comparison | Files | Expected Insights |
|------------|-------|-------------------|
| Fresh vs 1-level-played | base.bes vs organic.bes | Minimum changes from gameplay |
| Gold vs patched | gold.bes vs patched.bes | What makes gold stable |
| Before/after entering level | Two saves | Does game write on menu access? |
| PC vs console dump | Steam .bes vs Xbox/PS2 | Confirm encoding matches |

## Source Code Cross-Reference TODOs

- [ ] **Map mBaseThingsExists bits**: 288 bits for objectives, which bit controls what?
- [ ] **Find per-level grade thresholds**: Stuart says hardcoded in level data (.aya files?)
- [ ] **Decode tech slot bitmap**: 32 slots, which bits unlock which features?

Note: `IsEpisodeAvailable()` function fully documented in source analysis (Dec 2025).

## Ghidra/Binary Analysis Ideas

- [x] **Find cheat code validator**: ~~Search for "B4K42", "!EVAH!", "105770Y2" strings~~ **SOLVED Dec 2025**: Found `IsCheatActive()` at 0x00465490. PC port uses XOR encryption with key "HELP ME!!" - cheat codes are MALLOY, TURKEY, V3R5IOF, Maladim, Aurore, latête (NOT the original Lost Toys codes!) → Moved to [resolved-archive.md](resolved-archive.md)
- [x] **Trace god mode toggle**: Found via pause menu analysis - `PauseMenu__Init` at 0x004cde60 calls `IsCheatActive(3)` for god mode check → Moved to [resolved-archive.md](resolved-archive.md)
- [x] ~~**Locate EndLevelData struct**~~: **RESOLVED Dec 2025**: EndLevelData is runtime-only struct, never saved to .bes file - not part of mystery region
- [ ] **Check stripped debug keys**: Are V/U/I keys still functional in Steam release?
- [ ] **Test Maladim cheat**: User reports no god mode effect despite IsCheatActive(3) being the god mode check - investigate runtime flow

---

## Deferred RE Backlog (When Explicitly Scheduled)

### Tier 1: High-Value, Low-Effort (Deferred)

| Investigation | Tools | Expected Outcome |
|---------------|-------|------------------|
| **Apply source symbols to Ghidra** | Stuart's source + Ghidra MCP | Name 100+ functions from source (Career::*, Player::*, FEPGoodies::*) - transforms navigability |
| ~~**Find cheat code validator**~~ | ~~Ghidra string search + xrefs~~ | ✅ **DONE Dec 2025**: Found IsCheatActive at 0x465490, XOR decrypted PC port cheat codes |
| ~~**Investigate Steam god mode**~~ | ~~Trace Maladim / pause-menu gating path~~ | **TESTED Dec 12, 2025**: MP invincibility observed, SP not working. Offsets previously written up as `mIsGod[]` were incorrect (invert-Y). See [resolved-archive.md](resolved-archive.md) |
| **Debug Maladim cheat** | Trace IsCheatActive(3) callers | User reports no effect - trace runtime god mode activation path |

### Tier 2: Medium Effort, High Value

| Investigation | Approach | Why It Matters |
|---------------|----------|----------------|
| **Decode tech slot bitmap** | Cross-ref FEPGoodies.cpp unlock conditions + test patches | Could reveal hidden unlockable features |
| ~~**Trace EndLevelData**~~ | ~~Find save/load functions in Ghidra~~ | **RESOLVED Dec 2025**: EndLevelData is runtime-only, never saved - mystery region 3 is NOT EndLevelData |
| **Find grade thresholds** | Parse .aya level files with AYAResourceExtractor | Enable per-level grade optimization |

### Tier 3: Ambitious but Valuable

| Project | Description | Impact |
|---------|-------------|--------|
| ~~**God mode binary patch**~~ | ~~Find runtime check in exe, create patch~~ | ⚠️ **Candidate found Dec 2025**: historical note only; revalidation required |
| **Widescreen fix analysis** | Analyze existing patch in media/patches/ | Community value, documentation |
| **Full struct recovery** | Apply all source structs to Ghidra DB | Definitive RE reference for community |

---

## Binary Patching (NEW Dec 2025, archival)

Historical candidate patch notes from early RE passes. Treat as non-canonical until re-validated.

### All-Cheats Patch (DISCOVERED)

| Address (VA) | Before | After | Effect |
|--------------|--------|-------|--------|
| `0x004654a0` | `75 7A` (JNZ) | `EB 7A` (JMP) | Candidate force-true path in `IsCheatActive()` (needs revalidation) |

**Historical candidate mechanism**: The first conditional jump in `IsCheatActive()` checks `g_bDevModeEnabled`. Changing JNZ to JMP is a candidate force-true path, but this note remains archival and non-canonical until re-validation.

**Candidate effects (unrevalidated)**: all-cheat behavior was hypothesized (MALLOY=goodies, TURKEY=levels, V3R5IOF=version?, Maladim=god mode, Aurore=free camera, latête=goodie UI override), but this section is archival pending fresh runtime confirmation.

### Historical Note: File Offset Calculation (Resolved)

| Step | Value |
|------|-------|
| Virtual Address | 0x004654a0 |
| Image Base | 0x00400000 |
| RVA | 0x000654a0 |
| File Offset | `0x000654A0` (for this `.text` VA in canonical Steam image) |

### Alternative Patches (Data Section)

| Address | Patch | Effect |
|---------|-------|--------|
| `0x00662df4` | `01 00 00 00` | Set `g_bDevModeEnabled` flag |
| `0x00679ec1` | `01` | Set `g_bAllCheatsEnabled` flag |

**Note**: Data section patches require calculating file offsets from .data section headers.

### Future Patch Ideas

| Feature | Approach | Status |
|---------|----------|--------|
| **Infinite energy** | Find `SetInfinateEnergy()` call, patch condition | Not started |
| **Skip FMVs** | Find FMV player init, NOP or early return | Not started |
| **Force windowed** | Startup/display path patching | Archived: current repo baseline already has validated ungated path (see `reverse-engineering/binary-analysis/windowed-mode-analysis.md`) |
| **Unlock all MP** | Patch `IsEpisodeAvailable()` to always return TRUE | Not started |

### Deferred Actions Checklist

- [ ] Run Ghidra auto-analysis if not complete (track current coverage in `reverse-engineering/binary-analysis/deep-validation-status.md`)
- [x] ~~Import source function names~~ **PARTIAL Dec 2025**: 34 functions renamed including CCareer::*, IsCheatActive, PauseMenu__Init
- [ ] Search for magic strings: "Career", ".bes", "save", "load"
- [x] ~~Test god mode persistence~~ **DONE Dec 12, 2025**: MP invincibility observed, SP not working; offsets later determined to be invert-Y in Steam → See [resolved-archive.md](resolved-archive.md)
- [x] ~~Find cheat code implementation~~ **DONE Dec 2025**: IsCheatActive() found with XOR encryption → See [resolved-archive.md](resolved-archive.md)
- [x] ~~Define save file structs in Ghidra~~ **DONE Dec 2025**: CCareerNode, CCareerNodeLink, CGoodie created
- [x] ~~Trace why Steam god mode shows no visible effect~~ **TESTED Dec 12, 2025**: MP invincibility observed, SP not working; further investigation deprioritized pending better repro
- [x] ~~Calculate file offset for binary patch byte (VA 0x004654a0 → file offset)~~ **Resolved archival note**: `0x000654A0` for canonical Steam image.
- [ ] Test binary patch on BEA.exe to confirm all-cheats functionality

---

## Game Folder Investigations (Deferred Backlog)

> Run only in explicitly scheduled RE waves; not part of default app-first execution.

### Backlog Tier A: Quick Documentation (Deferred)

| Investigation | Priority | Approach | Expected Outcome |
|---------------|----------|----------|------------------|
| **textlist.h analysis** | High | Read and document | String ID mappings for all game text - developer artifact left in release |
| **Level numbering to node mapping** | High | Cross-reference level dirs with save nodes | Map level###/ directories to CCareerNode mWorldNumber values |
| **defaultoptions.bea comparison** | High | Binary diff vs gold save | Identify baseline vs unlocked differences, understand template |

### Tier 2: Content Discovery

| Investigation | Priority | Approach | Expected Outcome |
|---------------|----------|----------|------------------|
| **gill_m_on_a_fork.vid** | Medium | Play in RAD Video Tools, document content | Easter egg video? Developer in-joke? Cut content? 2.9 MB is substantial |
| **hack.msl script analysis** | Medium | Read level741/level742 scripts | Understand "hacking" gameplay mechanic - unique mission type |
| **MSL script language documentation** | Medium | Analyze multiple .msl files | Document mission scripting syntax for community modding reference |

### Tier 3: Format Research

| Investigation | Priority | Approach | Expected Outcome |
|---------------|----------|----------|------------------|
| **XAP audio format** | Low | Hex analysis of voice packs | Document format for potential extraction, 5+ language packs available |
| **STF string table format** | Low | Compare text.stf to english.txt | Understand compiled string tables |
| **DAT language file format** | Low | Hex analysis of language/*.dat | Localization binary format documentation |

### Investigation Details

#### gill_m_on_a_fork.vid

**Location:** `data/video/gill_m_on_a_fork.vid` (2.9 MB)

Unusual filename among standard videos like `OpeningFMV.vid`, `UsTheMovie.vid`, `LTLogo.vid`. The name pattern suggests:
- "gill" - possibly a developer name (team member?)
- "on_a_fork" - unknown meaning, possibly in-joke
- Worth viewing with Bink/RAD Video Tools to document content

**Status:** Not investigated

#### hack.msl Scripts

**Location:** `data/MissionScripts/level741/hack.msl`, `data/MissionScripts/level742/hack.msl`

These levels appear to implement special "hacking" gameplay distinct from standard combat missions. Questions:
- What objectives do these scripts define?
- Is this a different control scheme or mini-game?
- Are these missions accessible in normal gameplay or hidden/cut content?

**Status:** Not investigated

#### textlist.h Developer Artifact

**Location:** `data/MissionScripts/text/textlist.h`

A C/C++ header file left in the release build - contains string ID definitions used by the game's text system. Valuable for:
- Understanding text/UI message system
- Cross-referencing with .stf string tables
- Potential modding reference

**Status:** Not investigated

#### Level Numbering System

**Observation:** 97 level directories with numbering patterns:
- 000-030: Tutorial/early campaign
- 100-110: Island 1?
- 200-332: Main campaign with x11/x12/x21/x22 branching variants
- 500-524: Late campaign (Mission 500 = rocket/sub split)
- 700-742: End game (includes hack.msl levels)
- 800-888: Bonus/Evo levels
- 900-905: Multiplayer

**Question:** How do these directory numbers map to save file node IDs (mWorldNumber)?

**Status:** Needs cross-reference with save file analysis

#### defaultoptions.bea Analysis

**Location:** Root game directory, 10,004 bytes (same as .bes)

This is the template used when creating new career saves. Comparison with gold save would reveal:
- Which fields are zeroed in a fresh game
- Default volume settings
- Initial node/link/goodie state
- Any version-specific differences

**Status:** Not compared

### Symbol Import Strategy

Stuart's source provides key classes to match against Ghidra:

| Source File | Key Functions to Find |
|-------------|----------------------|
| Career.cpp | Save(), Load(), GetGradeFromRanking(), IsEpisodeAvailable() |
| Player.cpp | SetGodMode(), SetVulnerable(), AddToKillCount() |
| FEPGoodies.cpp | All goodie unlock condition checks |
| Controller.cpp | Cheat code validation logic |

Matching even 20-30 functions transforms the Ghidra project from opaque to navigable.

---

*See [resolved-archive.md](resolved-archive.md) for closed investigations*
*See [tech-slots.md](tech-slots.md) for dedicated tech slot investigation*
*See [../reverse-engineering/RE-INDEX.md](../reverse-engineering/RE-INDEX.md) for full technical docs*
