# CGame__FillOutEndLevelData

> Address: `0x0046d470` | Source: `references/Onslaught/game.cpp:910`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CGame__FillOutEndLevelData(void *this)`)
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:CGame::FillOutEndLevelData`)

## Purpose
Builds the end-of-level summary snapshot consumed by career/progression flows:
- objective completion flags
- score/time/grade-related values
- end-of-level kill/stat totals
- slot-bit flags (`mSlots`) used by MissionScripts (`GetSlot`/`SetSlot`) and persisted into CCareer on LevelWon
- related progression/context fields copied out of runtime state

## Notes
- Called on level shutdown paths before teardown/deallocation completes.
- Important bridge between runtime mission state and career persistence/reporting.
- Explicitly copies `END_LEVEL_DATA.mSlots = this->mSlots` (source parity). CCareer consumes this in `CCareer__Update` when the level ends in WON state.
