# WinUI Goodies Gallery Display Flag Override Readiness Note

Status: validated local byte/catalog/UI contract plus bounded copied-game Goodies-wall comparison and one selected-Goodie presentation proof
Date: 2026-06-17

Scope:

- Added catalog row `goodies_gallery_display_unlock`.
- Exposed the row in WinUI Windowed & Mods as `Goodies gallery display flag override`.
- Added Proof quick-pick controls that select or clear the existing `goodies_gallery_display_unlock` row without touching other selected safe-copy mods.
- Kept the claim boundary explicit: copied-executable display-path patch only, not save editing or permanent unlock.

Patch evidence:

| Field | Value |
| --- | --- |
| Function | `0x0045d7e0 CFEPGoodies__Process` |
| Target VA | `0x0045d7f4` |
| File offset | `0x05d7f4` |
| Original bytes | `E8 97 7C 00 00 F7 D8 1B C0` |
| Patched bytes | `83 C4 04 83 C8 FF 90 90 90` |
| Clean specimen | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, size `2506752` |

Source/static basis:

- `references/Onslaught/FEPGoodies.cpp` uses the MALLOY-style `ischeatactive` flag to return `GS_OLD` from `get_goodie_state()`.
- `CFEPGoodies::Process()` derives that flag from cheat index `0`.
- `reverse-engineering/binary-analysis/functions/FEPGoodies.cpp/CFEPGoodies__Process.md` records the retail `IsCheatActive(0)` call and `g_Cheat_MALLOY` store.
- A read-only byte check confirmed the clean backup bytes at `0x05d7f4`; the currently installed patched executable has a different full-file hash but the same Goodies-region original bytes.

Not claimed:

- No installed-game/original-executable mutation.
- No save mutation.
- No permanent Goodies award.
- No `lat\\xEAte`/developer override patch.
- One selected Tatiana character-art presentation page was captured after a
  patched copied-game Goodies selection run. No 3D model-viewer, FMV,
  every-entry, save-state, or permanent unlock proof yet.
- No rebuild parity or no-noticeable-difference claim.

Runtime-proof correction:

- The first runtime-proof attempt on 2026-06-17 exposed a patch-payload defect:
  the original row skipped `IsCheatActive(0)` without discarding the pushed
  argument. The catalog/AppCore row now uses `add esp,4; or eax,-1` plus NOP
  padding, so byte verification alone is no longer being treated as behavior
  proof.

Bounded runtime proof:

- First baseline without `goodies_gallery_display_unlock`:
  `subagents/winui-safe-copy-live-runtime/goodies-baseline-no-display-patch-20260617/live-safe-copy-runtime-smoke.json`.
  The captured Goodies-wall frame showed `To Unlock: Complete Tutorial`.
- First patched with `resolution_gate`, `force_windowed`, and
  `goodies_gallery_display_unlock`:
  `subagents/winui-safe-copy-live-runtime/goodies-display-unlock-hardened-20260617/live-safe-copy-runtime-smoke.json`.
  The captured Goodies-wall frame displayed `Unlocked! Hawk Winter`.
- Both first-pair runs used copied executables only, issued bounded menu input,
  captured a bounded screen-region frame at verified target-window bounds, stopped the app-owned managed process,
  verified installed/override executable hashes unchanged, and left no BEA
  process running. The live proof helper now records source
  `defaultoptions.bea`/`savegames` hashes for future runs; this earlier pair
  should not be read as save/defaultoptions hash proof.
- Second selected-right baseline without `goodies_gallery_display_unlock`:
  `subagents/winui-safe-copy-live-runtime/goodies-slot-right-baseline-hardened-20260617/live-safe-copy-runtime-smoke.json`.
  The final Goodies-wall frame showed `To Unlock: Grade C on Blackout`;
  `capture/safe-copy-frame-04.png` SHA-256
  `ee51e0ebd0c85a20bc30ecfedef5b659aaf30f6b5f1401b59c605387f4059a6b`.
- Second selected-right patched with `resolution_gate`, `force_windowed`, and
  `goodies_gallery_display_unlock`:
  `subagents/winui-safe-copy-live-runtime/goodies-slot-right-patched-hardened-20260617/live-safe-copy-runtime-smoke.json`.
  The final Goodies-wall frame displayed `Unlocked! Tatiana Kiralova`;
  `capture/safe-copy-frame-04.png` SHA-256
  `feb44294a0e58b88b7888380a913bb9e329f644496d2db5027f4930780638a94`.
- Both second-pair runs sent 22 bounded key events, captured four bounded
  screen-region frames at verified target-window bounds, stopped the app-owned managed process, verified
  installed `BEA.exe`, `BEA.exe.original.backup`, source `defaultoptions.bea`,
  and source `savegames` hashes unchanged, and left no BEA process running. The
  playable copied game folder created `savegames/BEA 1.bes`, which is expected
  copied-game runtime state, not source mutation.
- Patched selected-Goodie run:
  `subagents/winui-safe-copy-live-runtime/goodies-select-patched-20260617/live-safe-copy-runtime-smoke.json`.
  This run used the patched copied executable, sent four bounded input batches
  and 24 key events, selected the displayed Tatiana Goodie, captured six bounded
  screen-region frames, and showed the Tatiana character-art presentation page.
  The first selected frame `capture/safe-copy-frame.png` has SHA-256
  `6fd025bbe64a914c609e8123391838ff9ebfc70d46deb5250cc57e6999e8f97e` and
  showed text beginning `Born in the Sohna Federation`. Source executable,
  source `defaultoptions.bea`, and source `savegames` hashes stayed unchanged,
  the managed copied process stopped, and no BEA process remained.

Consult/adversarial corrections included:

- The source/binary consult proposed the right function span but an off-by-one file offset; root byte read corrected it from `0x05d7f5` to `0x05d7f4`.
- The adversarial consult identified over-strong version-overlay wording and a public allowlist defense-in-depth gap; this slice weakens the version cave side-effect wording and mirrors generated-artifact deny patterns into the public allowlist checker.
