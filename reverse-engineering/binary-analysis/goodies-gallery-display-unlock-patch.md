# Goodies Gallery Display Flag Override Patch

Status: byte-verified copied-executable patch exposed in WinUI with bounded copied-game Goodies-wall comparison and one selected-Goodie presentation proof
Last updated: 2026-06-17

This note records the bounded static/source evidence for `goodies_gallery_display_unlock`.
The patch is for app-owned copied `BEA.exe` files only. It must not be applied to the
installed Steam executable in place.

WinUI Windowed & Mods exposes this row both in the normal patch list and through
Proof quick-pick controls named `Add Goodies preview` and `Clear Goodies
preview`. Those controls only select or clear this existing visible row; they do
not add new bytes, edit saves, award Goodies, or change any unrelated selected
safe-copy mods.

## Patch Row

| Field | Value |
| --- | --- |
| Catalog id | `goodies_gallery_display_unlock` |
| Function | `0x0045d7e0 CFEPGoodies__Process` |
| Target VA | `0x0045d7f4` |
| File offset | `0x05d7f4` |
| Original bytes | `E8 97 7C 00 00 F7 D8 1B C0` |
| Patched bytes | `83 C4 04 83 C8 FF 90 90 90` |
| Clean specimen SHA-256 | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` |
| Clean specimen size | `2506752` |

## Evidence

- `references/Onslaught/FEPGoodies.cpp` has `get_goodie_state()` return `GS_OLD`
  when the file-local `ischeatactive` flag is true.
- `references/Onslaught/FEPGoodies.cpp` has `CFEPGoodies::Process()` set
  `ischeatactive` from save-cheat index `0`, the MALLOY Goodies cheat path.
- `reverse-engineering/binary-analysis/functions/FEPGoodies.cpp/CFEPGoodies__Process.md`
  identifies the retail function, the `IsCheatActive(0)` call at `0x0045d7f4`,
  and the `g_Cheat_MALLOY` store at `0x006798b0`.
- A read-only byte check of `BEA.exe.original.backup` on 2026-06-17 confirmed the
  canonical clean SHA-256, size, and original bytes at file offset `0x05d7f4`.
- The installed `BEA.exe` on this workstation currently has a different full-file
  hash because of the existing windowed patch, but the Goodies byte region still
  matched the canonical original bytes during the read-only check.

## Claim Boundary

Positive claim:

- The patch replaces the MALLOY-check/canonicalization instruction span in the
  copied executable with `add esp,4; or eax,-1` plus NOP padding. The `add esp,4`
  discards the argument that was pushed immediately before the skipped
  `IsCheatActive(0)` call; the following existing `neg eax` converts the forced
  `-1` value to the `1` stored in `g_Cheat_MALLOY`.

Correction note:

- An earlier 2026-06-17 row used `83 C8 FF 90 90 90 90 90 90`, which was
  byte-valid but stack-unsafe because it skipped a thiscall-style call without
  removing the already-pushed argument. A copied-game live smoke exited before
  scoped input/capture, and this row was corrected before making any runtime
  Goodies behavior claim.

Bounded runtime proof:

- First baseline copied-game run without `goodies_gallery_display_unlock`:
  `subagents/winui-safe-copy-live-runtime/goodies-baseline-no-display-patch-20260617/live-safe-copy-runtime-smoke.json`.
  The captured Goodies-wall frame at `capture/safe-copy-frame.png` showed the
  locked/tutorial state (`To Unlock: Complete Tutorial`).
- First patched copied-game run with `resolution_gate`, `force_windowed`, and
  `goodies_gallery_display_unlock`:
  `subagents/winui-safe-copy-live-runtime/goodies-display-unlock-hardened-20260617/live-safe-copy-runtime-smoke.json`.
  The captured Goodies-wall frame at `capture/safe-copy-frame.png` showed the
  displayed-as-unlocked state (`Unlocked! Hawk Winter`).
- Both first-pair runs launched copied executables only, issued bounded menu
  input, captured a bounded screen-region frame at verified target-window bounds, stopped the managed process,
  verified installed/override executable hashes unchanged, and ended with no
  BEA process remaining. The live proof helper now records source
  `defaultoptions.bea` and `savegames` hashes for future runs; this earlier
  pair should not be read as save/defaultoptions hash proof.
- Second selected-right baseline run without `goodies_gallery_display_unlock`:
  `subagents/winui-safe-copy-live-runtime/goodies-slot-right-baseline-hardened-20260617/live-safe-copy-runtime-smoke.json`.
  The captured Goodies-wall frame at `capture/safe-copy-frame-04.png` showed
  `To Unlock: Grade C on Blackout`; frame SHA-256
  `ee51e0ebd0c85a20bc30ecfedef5b659aaf30f6b5f1401b59c605387f4059a6b`.
- Second selected-right patched run with `resolution_gate`, `force_windowed`,
  and `goodies_gallery_display_unlock`:
  `subagents/winui-safe-copy-live-runtime/goodies-slot-right-patched-hardened-20260617/live-safe-copy-runtime-smoke.json`.
  The captured Goodies-wall frame at `capture/safe-copy-frame-04.png` showed
  `Unlocked! Tatiana Kiralova`; frame SHA-256
  `feb44294a0e58b88b7888380a913bb9e329f644496d2db5027f4930780638a94`.
- Both second-pair runs issued three bounded input batches, sent 22 key events,
  captured four bounded screen-region frames at verified target-window bounds, stopped the managed copied
  process, verified installed `BEA.exe`, `BEA.exe.original.backup`, source
  `defaultoptions.bea`, and source `savegames` hashes unchanged, and ended with
  no BEA process remaining. The playable copied game folder created
  `savegames/BEA 1.bes`, which is expected copied-game runtime state, not
  source mutation.
- Patched selection run with `resolution_gate`, `force_windowed`, and
  `goodies_gallery_display_unlock`:
  `subagents/winui-safe-copy-live-runtime/goodies-select-patched-20260617/live-safe-copy-runtime-smoke.json`.
  This run repeated the selected-right Goodies navigation, sent a fourth bounded
  input batch to select the displayed Tatiana Goodie, and captured six bounded
  screen-region frames at verified target-window bounds. The first selected
  frame at `capture/safe-copy-frame.png` showed the Tatiana character-art
  presentation page with the text beginning `Born in the Sohna Federation`;
  frame SHA-256
  `6fd025bbe64a914c609e8123391838ff9ebfc70d46deb5250cc57e6999e8f97e`.
  Later frames showed the same presentation page with advancing descriptive
  text. The run sent 24 bounded key events, stopped the managed copied process,
  verified installed `BEA.exe`, `BEA.exe.original.backup`, source
  `defaultoptions.bea`, and source `savegames` hashes unchanged, and ended with
  no BEA process remaining.

Not claimed:

- It does not edit `.bes` saves or `defaultoptions.bea`.
- It does not permanently award Goodies.
- It does not force the `lat\\xEAte`/developer Goodies override path.
- It does not prove 3D model viewing, FMV playback, every Goodies entry, save
  state, unlock progression, or permanent unlock behavior.
- It does not prove rebuild parity or no-noticeable-difference behavior.

Broader proof still needed:

1. Broaden selected-Goodie presentation proof beyond one displayed Tatiana entry.
2. Prove 3D model-viewer and FMV behavior for entries that use those paths.
3. Compare behavior across representative locked/unlocked source saves.
