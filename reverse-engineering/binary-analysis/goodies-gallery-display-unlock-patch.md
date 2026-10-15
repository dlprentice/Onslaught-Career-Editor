# Goodies gallery display override

Status: byte-verified copied-executable patch with bounded Goodies-wall and one selected-entry observation.

`goodies_gallery_display_unlock` forces the existing MALLOY display flag inside `CFEPGoodies__Process`; it does not alter save progression.

| Item | Value |
| --- | --- |
| Function | `0x0045D7E0 CFEPGoodies__Process` |
| Target VA / file offset | `0x0045D7F4` / `0x05D7F4` |
| Original bytes | `E8 97 7C 00 00 F7 D8 1B C0` |
| Patched bytes | `83 C4 04 83 C8 FF 90 90 90` |
| Clean specimen SHA-256 | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` |
| Clean specimen size | `2506752` |

The source sets the file-local display override from `IsCheatActive(0)`. The replacement discards the already-pushed argument with `add esp,4`, forces `eax` to `-1`, and leaves the following retail `neg eax` to produce the stored true flag. An earlier candidate omitted the stack repair and was rejected before any behavior claim.

Controlled copied-profile comparisons observed:

- baseline locked/tutorial copy versus patched `Unlocked! Hawk Winter` display;
- baseline `To Unlock: Grade C on Blackout` versus patched `Unlocked! Tatiana Kiralova` after the same right-navigation sequence;
- selection of that displayed Tatiana entry reaching its character-art presentation and descriptive text.

The runs used app-owned copied executables, bounded input and capture, terminated the managed processes, and verified installed/source executable and source save/options hashes remained unchanged.

## Boundary

The patch does not edit `.bes`, `defaultoptions.bea`, or permanent Goodie state. It does not prove every entry, 3D model viewing, FMV playback, progression behavior, or rebuild parity. It remains copied-profile-only and must never target the installed game or clean backup.
