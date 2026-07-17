# High-impact call chains

Status: active static summary

These chains explain product-relevant ownership and side effects. They are
static evidence unless a linked runtime contract says otherwise.

## Save and options persistence

| Path | Static chain | Product consequence |
| --- | --- | --- |
| Load game | `CFEPLoadGame__DoLoad` → `CCareer__Load` → conditional `CFEPOptions__WriteDefaultOptionsFile` | Loading a retail save can update the boot-time options snapshot. |
| Main menu save | `CFEPMain__Process` → `CCareer__Save` and `CFEPOptions__WriteDefaultOptionsFile`, with an optional platform save write | Career and global options can be persisted by the same frontend transition. |
| Pause resume/exit | `CPauseMenu__ResumeGameAndPersistOptions` → `CCareer__Save` → optional platform save write → `CFEPOptions__WriteDefaultOptionsFile` | Resume/exit can update both career data and `defaultoptions.bea`. |
| Debrief | `CFEPDebriefing__Initialize` prepares debrief state upstream of the persistence paths | Debrief initialization itself is not the save write. |

Primary owners are
[`CFEPLoadGame__DoLoad`](functions/FEPLoadGame.cpp/CFEPLoadGame__DoLoad.md),
[`CCareer__Save`](functions/Career.cpp/CCareer__Save.md),
[`CPauseMenu__ResumeGameAndPersistOptions`](functions/PauseMenu.cpp/CPauseMenu__ResumeGameAndPersistOptions.md),
and the [save/options contract](save-options-static-review-2026-05-26.md).
These relationships are why AppCore patches real baseline files, preserves
unknown bytes, and writes separate outputs instead of synthesizing saves.

## World lifecycle

`CWorld__LoadWorldFile` calls `CWorld__LoadWorld`, which in turn reaches header
loading, LOD initialization, initial-thing spawning, and waypoint loading.
Teardown is owned by the corresponding world shutdown/reset cluster. The
reviewed ABI for `CWorld__LoadWorld` has three stack arguments and `RET 0x0c`;
see [`CWorld__LoadWorld`](functions/World.cpp/CWorld__LoadWorld.md) and the
[reviewed correction plan](ghidra-reviewed-correction-plan-2026-07-13.json).

## Text lookup

- `CText__Init` loads the language table and seeds the version, count, text-pool
  and audio-pool state.
- `CText__GetStringById` performs the versioned entry lookup and returns the
  text-pool fallback after a miss.
- `CText__GetStringByIdAfter` performs grouped lookup relative to a matched id
  and uses the same fallback boundary.

See [`CText__Init`](functions/text.cpp/CText__Init.md). These static paths
support the language decoder and mission-text maps, but do not prove every DAT
variant or runtime localization behavior.

## Claim boundary

The chains establish bounded call relationships and observed side-effect
ownership. They do not prove every branch, exact object layout, runtime timing,
patch safety, or rebuild parity. Current exact metadata corrections are owned
by the [Ghidra correction authority](ghidra-full-reaudit-closeout-2026-07-13.md),
not by retired phase or wave artifacts.
