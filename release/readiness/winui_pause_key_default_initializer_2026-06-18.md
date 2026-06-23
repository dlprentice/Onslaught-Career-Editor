# WinUI Pause Key Default Initializer Readiness Note

Status: superseded by bounded copied-runtime proof
Date: 2026-06-18

This historical note records the original WinUI/AppCore byte/catalog readiness boundary for `pause_o_scan_initializer_experiment`.

Superseded by: `release/readiness/winui_pause_o_scan_initializer_runtime_2026-06-18.md`.

## Accepted

- Added a cataloged experimental visible row for copied executables only.
- The row targets the canonical clean Steam retail specimen hash `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and size `2506752`.
- The row changes file offset `0x1144CD` from `01` to `18`.
- The evidence anchor is `0x00514210 OptionsEntries__InitDefaultSingleBindingsTable`, where the retail pause row initializes `BUTTON_PAUSE` (`0x38`) with key argument `1`.
- The WinUI row is experimental, custom-only, and requires the normal copied-windowed pair (`resolution_gate` + `force_windowed`) before selection.
- Focused catalog probe: `tools/winui_pause_o_scan_initializer_catalog_check.py --check`.
- The installed game and original `BEA.exe` remain out of scope; this is for app-owned copied profiles only.

## Not Proven

- Superseded: the follow-up bounded copied-runtime proof now shows ordered same-window evidence for scoped `O` query, `BUTTON_PAUSE` dispatch, and one pause/unpause pair in a bounded free-camera context.
- Still not proven: second-`O` normal-gameplay unpause, broad/general pause-menu UX, broad pause/menu safety, gameplay safety, improved controls, all profiles, long-session behavior, render parity, online/netcode, rebuild parity, or no-noticeable-difference parity.
- This does not edit or expand the fixed `defaultoptions.bea` persisted options-entry model.
- This is not a Ghidra correction; current evidence points to retail runtime/options binding behavior rather than a wrong static name/signature/comment.

## Historical Next Gate

The follow-up proof launched a copied profile with this row selected and attached exact-PID CDB observers around:

- `OptionsEntries__InitDefaultSingleBindingsTable`
- aligned and shifted controller-table dumps for the pause row
- `CPCController__GetKeyOnce`
- `PlatformInput__GetKeyOnceCore`
- `CController__DoMappings`
- `CController__SendButtonAction`
- `CGame__Pause` / `CGame__UnPause`

That gate is now closed by `release/readiness/winui_pause_o_scan_initializer_runtime_2026-06-18.md`: scoped `O` input produced ordered same-window `BUTTON_PAUSE` dispatch and one pause/unpause pair with adjacent negative-control windows in the bounded copied-runtime proof. A later level-100 copied-runtime proof shows `O` opens the pause menu and `ENTER` resumes from it. The row still stays experimental because full debugger call-chain causality, second-`O` normal-gameplay unpause, broad/general pause-menu UX, broad pause/menu safety, gameplay safety, all profiles, and long-session behavior remain separate proof.
