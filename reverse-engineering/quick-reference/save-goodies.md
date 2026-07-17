# Save Goodies quick reference

The authoritative format and evidence boundaries are in [goodies-system.md](../save-file/goodies-system.md). Unlock copy shown by the product is owned by [`GoodieUnlockRequirementService.cs`](../../OnslaughtCareerEditor.AppCore/GoodieUnlockRequirementService.cs).

## Storage

- Save size: `10004` bytes
- Version word: `0x4BD1`
- True Goodie base: `0x1F46`
- Entry offset: `0x1F46 + index * 4`
- Stored entries: `300`
- Displayable entries: indices `0..232`
- Reserved entries: indices `233..299`; preserve them

| Raw dword | State | Product display |
| ---: | --- | --- |
| `0` | unknown | Locked |
| `1` | instructions | Locked with hint |
| `2` | new | Gold badge |
| `3` | old | Blue badge |

MissionScript Goodie indices are one-based: `script index = save index + 1`. Script index `0` is invalid.

## Consequential boundaries

- Patch only a real copied baseline; never synthesize a save or write in place.
- Preserve every byte outside explicitly selected displayable Goodie dwords.
- Goodies `71..73` have source unlock hooks and shipped texture resources, but the observed ordinary wall path moves from `70` to `74`; hidden reachability remains unproven.
- Goodie `232` maps to cutscene `33` and lacks a matching `goodie_232_res_PC.aya` in the checked PC archive set.
- Goodie `228` is at `0x22D6`. The old `0x22D4` aligned-view value is not `mCareerInProgress`; that flag is at file offset `0x248A`.

Use the AppCore patcher and its focused tests for byte-preservation behavior.
