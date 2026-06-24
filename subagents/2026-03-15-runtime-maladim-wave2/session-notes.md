# Runtime Notes: Maladim positive-case wave 2

Date: 2026-03-15
Session type: live runtime probe against a patched-for-windowed installed build
Target executable: `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe`
Baseline note: this was not the clean retail specimen; the installed executable had display/windowed patches applied to keep the game attachable and visible while debugging.

## What We Were Trying To Prove

1. Whether the Steam-build `Maladim` save-name path really reaches `IsCheatActive(3)` at runtime.
2. Whether the current docs were wrong about the location/visibility of the god-mode menu item.
3. Whether the visible UI path is root pause menu or a later submenu surface.

## Confirmed Findings

### 1. Positive-case `Maladim` path is real

During the live positive-case pass on a new save named `Maladim`, the debugger hit:

```text
PauseMenu__Init this=03909040
IsCheatActive this=008a1374 cheat=3
PauseMenu_godmode_label_check god=0
```

This is enough to confirm that the Steam build really does evaluate cheat index `3` on the `Maladim` path.

### 2. The old “no visible effect” wording was wrong

User-visible confirmation from the live session:

- opening `Controller Options` while paused on the `Maladim` save showed `God OFF`
- toggling it changed the same line to `God ON`

This means the earlier simplified posture of “Maladim shows no visible effect” was too strong and is now superseded.

### 3. The toggle location is not the root pause page

The live session showed that the god toggle is exposed under:

- `Pause`
- `Controller Options`
- `God OFF` / `God ON`

It is not surfaced as a new top-level pause-menu line on the first/root pause page.

## What Is Still Open

- We have not yet re-proven the actual gameplay effect of `God ON` in this Steam build.
- We did not land a clean post-return capture of `IsCheatActive(3)` via `eax`, so the functional conclusion here rests on the visible UI plus the entry-site hits rather than a final return-value print.

## Practical Doc Correction

The canonical docs should now say:

- `Maladim` does have visible Steam-build effect.
- The effect is a cheat-gated `God OFF` / `God ON` toggle under `Controller Options`.
- Gameplay invulnerability remains the open question.
