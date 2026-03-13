# CFEPDebriefing__Initialize

> Address: 0x00456780 | Source: FEPDebriefing.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (read-back verified in mutation snapshots)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Initializes the mission debriefing screen after a mission is completed. This screen displays the player's performance including rank achieved, kill counts by category, and any newly unlocked goodies.

## Signature
```c
// Live read-back signature (wave217 snapshot)
int __fastcall CFEPDebriefing__Initialize(void * this);
```

## Signature Evidence

- `MCP-MUTATION-BACKLOG.md` completion record (2026-02-24): `int CFEPDebriefing__Initialize(void * this)`.
- `scratch/deep_semantic_tail_2026-02-27/all_after_wave217.tsv` line 917: `int __fastcall CFEPDebriefing__Initialize(void * this)`.
- `scratch/program_2026-03-01/phase5_signature_readback/index.tsv`: read-back `status=OK`.

## Algorithm

```
1. Retrieve mission completion data from EndLevelData (runtime struct)

2. Calculate mission rank:
   - Get ranking float from mission performance
   - Convert to grade using GetGradeFromRanking()

3. Populate kill statistics:
   - Aircraft kills
   - Vehicle kills
   - Emplacement kills
   - Infantry kills
   - Mech kills

4. Check for newly unlocked goodies:
   - Compare current kill totals against thresholds
   - Check grade-based unlocks (A-rank, S-rank bonuses)
   - Mark new unlocks for highlight

5. Set up UI elements:
   - Rank display (letter grade)
   - Kill count displays
   - Goodie unlock notifications
   - Continue/retry buttons

6. Play appropriate audio (victory fanfare, etc.)
```

## Data Sources

### EndLevelData (Runtime)

The debriefing screen reads from `EndLevelData`, a **runtime-only struct** that holds mission completion statistics. This struct is NOT saved to the .bes file - it only exists during gameplay.

### Kill Counters (Saved)

After the debriefing is acknowledged, kill counts are added to the career totals and saved to the `.bes` file:
- CCareer offset: `0x23F4`
- File offset (true dword view): `0x23F6` (`file_off = 0x0002 + career_off`)

Each kill dword is packed: `stored = (meta<<24) | (kills & 0x00FFFFFF)` (preserve `meta` when patching).

### Ranking (Saved)

The mission ranking is saved to the appropriate `CCareerNode.mRanking` as raw IEEE-754 float bits (true dword view). Older docs that described a “split-float” were looking at the legacy 4-byte-aligned view of the same bytes.

## Grade Display

The function converts the ranking float to a letter grade:

| Float | Grade | Display |
|-------|-------|---------|
| 1.0 | S | Gold "S" |
| 0.75+ | A | Silver "A" |
| 0.50+ | B | Bronze "B" |
| 0.25+ | C | "C" |
| 0.01+ | D | "D" |
| 0.0 | E | "E" |

## Goodie Unlock Notifications

When a kill threshold is crossed during the mission, the debriefing screen highlights the newly unlocked goodies. This uses the same threshold values as `FEPGoodies.cpp`.

## Call-Chain Position (Current Evidence)

- This initializer owns debrief-page state setup and runtime summary population.
- Internal data-flow anchor: `scratch/deep_semantic_tail_2026-02-26/pass2_semantic_wave48_prep/xrefs.tsv` shows `CFEPDebriefing__Initialize` referencing `CFEPDebriefing__ResetStateAndVector` at `0x004567c9`.
- Dedicated xref export (2026-03-01) for `0x00456780` shows a data reference from `0x005db9c0` (`ref_type=DATA`), consistent with indirect vtable/dispatch-table invocation rather than direct call xrefs: `scratch/program_2026-03-01/phase5_fepdebriefing_xrefs/xrefs.tsv`.
- Save/defaultoptions persistence side effects are downstream in frontend save/load/pause flows (documented in `high-impact-call-chain-appendix.md`), not at this entrypoint.

## Cross-References

### Calls
- `GetGradeFromRanking` - converts float to letter grade
- UI element initialization functions
- Audio playback functions

### Called By
- Game flow system after mission completion

### Related
- `EndLevelData` - runtime mission stats (NOT saved)
- `CCareer::Save` - saves updated stats after debriefing

## UI Elements

Typical debriefing screen layout:
```
+----------------------------------+
|        MISSION COMPLETE          |
|                                  |
|           RANK: [S]              |
|                                  |
|  Aircraft:  25    Infantry:  40  |
|  Vehicles:  100   Mechs:     20  |
|  Emplacements: 25                |
|                                  |
|    NEW GOODIE UNLOCKED!          |
|                                  |
|  [CONTINUE]      [RETRY]         |
+----------------------------------+
```

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- EndLevelData is runtime-only - don't confuse it with saved career data
- The debriefing screen is where kill counts get finalized into the save
- Grade display uses the same calculation as the career screen
