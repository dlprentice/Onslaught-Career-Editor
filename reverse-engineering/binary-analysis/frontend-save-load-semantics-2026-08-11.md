# Frontend save/load and PC persistence semantics

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — complete pristine retail bodies, retained frontend source,
PC-platform call targets, released cheat-table bytes and callers, and fifteen
normalized-identical PC demo twins; UNKNOWN — destructive/fault-injected runtime
behavior, console adapter parity, dialog pixels, and rebuild-wide persistence
parity.
Verdict: the released PC frontend persistence transaction and its source
divergences are recovered. It preserves the shared page policy but replaces the
source `MEMORYCARD` service with the PC file adapter, treats save names
case-insensitively, and expands the source's four plaintext cheat names into a
six-entry XOR-obfuscated table.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.
The source anchors are `references/Onslaught/FEPLoadGame.cpp` (6,698 bytes,
SHA-256 `549719fc53f6f138b9f4bc4dd0ffbaf61f4dab67beaa2cec93aa3b534294d86e`)
and `references/Onslaught/FEPSaveGame.cpp` (16,122 bytes, SHA-256
`17c64a08913fcd4831f30097864eb789efb6f04601d2c8caf1a3ee7135353b72`).
Their headers have SHA-256 values
`8aa0092262f44ede5774401e57d99c81230dd87f358b3407ffd1c87720d8d0c3`
and `af7bf11578a65db4ce28868fa1fab5e9901bc1272231818d0f83c75282397fa3`.

## Result

The fifteen-function unit covers 5,148 retail bytes and 1,588 decoded
instructions. Every body has an independently mapped PC demo twin with zero
normalized instruction differences; 706 raw bytes differ only in encoded
addresses or displacements. The machine-readable result is
[`frontend-save-load-semantics-2026-08-11.tsv`](frontend-save-load-semantics-2026-08-11.tsv),
5,067 bytes, SHA-256
`69f11a78f4420eaf78cb4161266b33d80611809f7bb2757c244056b2225bee3b`.

This is a useful cross-build boundary. The demo was independently linked, yet
the complete page, transaction, comparison, and cheat-gate bodies survived
unchanged after relocation. These are production PC semantics rather than a
single retail-repack accident.

## Shared page policy

Both pages use the same released input law. Button IDs `0x2a`, `0x2b`, `0x36`,
and `0x37` adjust page motion and clamp it to `0..255`; `0x2c` accepts and
`0x2e` returns to frontend page zero. The paths issue move, select, and back
sounds `0`, `1`, and `2`. Load initialization additionally sets its selected
slot to `-1`; save initialization clears the save-name head.

When inactive, each `Process` returns. Otherwise it polls the platform storage
owner; the active/no-message-box state enters the page's transaction. Rendering
uses localized title token `0x0d` for load and `0x11` for save, shared help
prompt `4`, and the exact transition factor
`clamp((transition - 0.75) * 4, 0, 1)`.

## Load transaction

`CFEPLoadGame__DoLoad` is the released PC counterpart of the retained source's
`CFEPLoadGame::StartLoad`. It rejects an unselected `-1` slot, copies the chosen
wide save name into the save page and virtual-keyboard state, moves the edit
cursor to the end, and validates that the selected storage device is present
and formatted.

It allocates exactly `CCareer::GetSaveSize()` bytes, reads the selected `.bes`
file through `PCPlatform__ReadSaveFile`, and calls `CCareer::Load` with flag
`1`. A zero read result followed by a successful career load advances the
frontend, marks autosave state, and—when `DAT_0082b5b0` is zero—writes the
loaded options block as the default-options file. Career rejection receives a
bad-version path. File-read failure rechecks the storage device and separates
removal/invalid-device handling. Every allocated buffer reaches the memory
manager free path.

This confirms a clean service boundary: the retained shared flow calls
`MEMORYCARD.ReadSave`, while the PC executable performs the same policy through
`PCPlatform__ReadSaveFile` and PC storage queries.
The concrete implementation and its corrected `CPCMemoryCard` ownership are
recovered in the
[`CPCMemoryCard` PC save-backend crosswalk](cpcmemorycard-pc-save-backend-semantics-2026-08-11.md).

## Save transaction

`CFEPSaveGame__CreateSave` obtains storage presence, formatting, capacity, and
the enumerated save count through the PC adapter. It preserves the pre-save
career-in-progress state, reacts to storage-device changes, computes the exact
career buffer size, and enforces a maximum of 4,095 existing saves before
creation.

Existing names are enumerated and compared with
`CFEPSaveGame__WideStrCaseInsensitiveCompare`. An existing name without
overwrite authorization opens the overwrite question. Once authorized, the
function creates the file record, allocates an exact career-sized buffer,
serializes through `CCareer__SaveWithFlag`, and writes with
`PCPlatform__WriteSaveFile`. The released result paths distinguish success,
existing file, removal/no file, full storage, and the save-count limit; partial
failures delete the newly created file where required and refresh the count.
Success updates frontend/autosave state and marks the virtual-keyboard name as
no longer fresh.

`CFEPSaveGame__Process` owns the surrounding dialog state machine. Question
`3` handles overwrite/delete confirmation and question `9` handles storage
recovery. `RemovedMUWhinge` is only a fixed dialog builder and state reset; it
does not query a device. `AskIfYouWantToDelete` is a material PC divergence:
the released body reads only `because_4096`, selects localized token `0x9e` or
`0xa0`, and opens question `4`. Its `career_in_progress` and
`no_space_for_bea` parameters are not read, whereas the retained source has a
broader console-memory-card message composition.

## Released save-name identity

The retained source uses case-sensitive `wcscmp`. The PC executable instead
uses a dedicated case-insensitive comparator. ASCII `A..Z` is folded by adding
`0x20`; other characters pass through the released character-classification
and `LCMapStringW` compatibility path under locale lock index `0x13`. Thus two
PC save names that differ only by case collide for overwrite purposes even
though the retained source would treat them as distinct.

## Cheat-name gate

The current Ghidra name `IsCheatActive` is source-correlated to
`CFEPSaveGame::IsCheatActive`. Either the developer-mode flag or the runtime
all-cheats flag returns true immediately. Otherwise the body selects a
256-byte row beginning at VA `0x00629464`, XORs its first nine bytes with
`"HELP ME!!"` at VA `0x00629a64`, converts the current wide save name to the
PC byte form, and uses `strstr`. Matching is therefore substring-based and
multiple codes may coexist in one name.

The pristine table decodes exactly as follows:

| Index | Released byte string | Proven consumer meaning |
| ---: | --- | --- |
| 0 | `MALLOY` | Goodie unlock/state override. |
| 1 | `TURKEY` | Campaign-world availability bypass. |
| 2 | `V3R5IOF` | No released caller found; the retained-source version-display meaning remains only a source hypothesis for this PC build. |
| 3 | `Maladim` | God-mode menu gate; later runtime evidence confirms the toggle and normal combat-damage effect. |
| 4 | `Aurore` | Free-camera action gate. |
| 5 | `lat<0xEA>te` | Goodie state/gating override. The third byte is CP1252/Latin-1 `0xEA`, not UTF-8. |

This differs materially from the retained four plaintext strings
`105770Y2`, `!EVAH!`, `V3R5ION`, and `B4K42`. The released byte table and
callers win wherever the two builds disagree. Index 2's exact spelling is
`V3R5IOF`; assigning its source-era version-display effect to retail remains
unproven because no retail call has been found.

## Boundary

This closes the static PC semantics of these page and transaction bodies. It
does not authorize writing a real save, prove behavior under disk-full or
mid-write removal faults, establish Xbox/PS2 error-code equivalence, prove
frontend pixels, or claim complete rebuild persistence parity. Safe runtime
falsification must use a copied save and copied installation; the user's real
career remains outside any destructive test.
