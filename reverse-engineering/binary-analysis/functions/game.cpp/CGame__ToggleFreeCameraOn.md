# CGame__ToggleFreeCameraOn

Status: active byte-matched function and bounded arithmetic contract; runtime acceptance remains separate
Last updated: 2026-09-30
Summary: free-camera construction preserves a float-rounded elevation argument before asin; fresh arithmetic evidence does not establish camera runtime or visual parity.
Evidence: MEASURED — fresh whole-body read, complete compiled-section/relocation match and 24 isolated arithmetic cases; no player or visual acceptance run.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/game.cpp:3240` | Binary: pristine BEA.exe.original.backup, identified above.

> Address: 0x00470430 | Source: `references/Onslaught/game.cpp`

Fresh September 30 read: 414-byte body `[0x00470430, 0x004705ce)`, ending in `ret 4` at `0x004705cb`;
SHA-256 `eaff4ef665831c0d26f6e52cb9c7d5c2f2a96109c37484b3a975ca795dafe0f7`.
The old “mostly verified” label did not establish the arithmetic or complete compiled match. The September 30
reconstruction now matches the entire 416-byte compiled section, including alignment, and all relocations.
The focused check retains all 89 checked functions and seven vtables in `game.cpp`; the subsequent full
build gains this function without losing earlier matches. No live Ghidra signature was changed.

## Purpose
Enables free camera mode for a player:

- Saves the current camera into `mOldCamera[player]`
- Allocates a controllable camera and hands it to the controller
- Switches the current camera to the controllable camera
- Sets `mFreeCameraOn[player] = TRUE`
- Records whether the game was paused when free cam started (`mPauseOnWhenStartedFreeCam[player]`)

The retained source routes this through the Aurore debug-button path; this pass did not rerun a retail input route.

## Signature
```c
// __thiscall, pops 0x4 (1 arg)
void CGame::ToggleFreeCameraOn(int player);
```

## Source Cross-Check
The workflow appears at `references/Onslaught/game.cpp:3240`. This abbreviated excerpt identifies the
workflow; the match uses the complete source body and reconstructed dependencies, not this abbreviated sketch:
```cpp
void CGame::ToggleFreeCameraOn(int playernumber) {
    mOldCamera[playernumber] = GetCurrentCamera(playernumber);
    // create CControllableCamera(...)
    mController[playernumber]->SetToControl(c);
    SetCurrentCamera(playernumber, c, false);
    mFreeCameraOn[playernumber] = TRUE;
    mPauseOnWhenStartedFreeCam[playernumber] = (mPause == TRUE);
}
```

## Elevation argument correction — September 30

The retail caller obtains the camera orientation, extracts its Y column through x87 loads
(`0x0047046d`–`0x0047047a`), computes its magnitude and keeps that magnitude in x87. On the positive-magnitude
path it divides Z by the magnitude, **rounds the quotient to float32** at `0x004704a5`, reloads it at
`0x004704ab`, and calls `_CIasin` at `0x004704af`. Those materialization boundaries matter; casting only
the return from `asin` does not require the same sequence.

The private reconstruction previously spilled magnitude first and passed an unrounded quotient to asin.
Using the pinned VC6 `asinf(float)` wrapper in `FVector::Elevation` reproduces this caller's arithmetic
sequence and argument. The separately compiled Elevation body (`0x0040d1a0`) remains an exact match;
the header-only full build preserved every previously matched function. The wrapper spelling is a
reconstruction, not a recovered original header. Restoring Stuart's original
`FMatrix m = FMatrix(s.Azimuth(), s.Elevation(), 0.0f)` then closes the remaining frame/stack differences.
The prior reconstruction had split declaration and assignment into separate statements. Both changes
together reproduce the complete free-camera function; the wrapper alone did not.

The lead ran 24 arithmetic-slice cases with positive, negative and zero Z, nonzero magnitudes, and chosen
x87 PC53/PC64 nearest-rounding modes. The corrected candidate and original instructions produced identical
raw ST0 arguments in all cases; the prior candidate differed in 12. For column `(0, 1, 1)`, retail supplies
`0.7071067690849304`, while the prior candidate supplies approximately `0.7071067932881648`.
Exact-axis controls agree. Execution stops **before asin**; no camera, allocator, rendering or game process runs.
Synthetic columns and chosen FPU modes are not observations of live camera inputs or the game's control word.
Zero magnitude, exceptional values, non-nearest modes, asin's implementation and full camera behavior remain outside this probe.

Private reproduction, from `bea-decomp` main:

```text
local-data/venv/bin/python local-data/elevation-call-argument-probe-20260930.py
```

Its adjacent JSON records the verified specimen, exact candidate-object/script hashes, inputs and raw x87
results. Prior and corrected compiled objects are frozen in the adjacent private input directory, so later
builds cannot silently replace them. Static and full-build receipts are in
`bea-decomp/.worktrees/codex-equiv-20260930/build/elevation-retail-readback-20260930.asm` and
`elevation-asinf-full-score-20260930.log` and `elevation-freecamera-full-score-20260930.log`;
`free-camera-asinf-source-init-20260930.txt` records the subsequent
whole-object match after restoring the original matrix declaration. Independent review checked the instruction slices and the initial
ten-case probe before the lead extended it to negative/zero-Z controls. A useful stronger falsifier would
exercise the actual asin callee and return-to-camera path with admitted object lifetimes; player-visible
orientation and transition behavior remain separate runtime acceptance work.

## Related Functions
- `CGame__SetCurrentCamera` (`0x004705e0`)
- `CGame__ReceiveButtonAction` (`0x0046f7e0`) (Aurore-gated entry point)
