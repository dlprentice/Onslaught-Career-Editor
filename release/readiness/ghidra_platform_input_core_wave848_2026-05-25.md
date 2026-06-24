# Ghidra Platform Input Core Wave848 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `platform-input-core-wave848`

Wave848 platform input core saved comments, tags, and two signature corrections for four adjacent platform/input/render capture helpers from `0x00513120 PlatformInput__InitDirectInput` through `0x005135f0 PlatformInput__SetKeySinkCore`. These rows are compact but important connective infrastructure: they tie WinMain/platform setup to DirectInput device enumeration, per-pad polling, screenshot capture, and frontend virtual-keyboard key-sink routing. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00513120 PlatformInput__InitDirectInput` | `int __thiscall PlatformInput__InitDirectInput(void * this, void * window_handle)` | Source-reference `PCLTShell::InitDirectInput(HWND)`; calls `DirectInput8Create` at `0x00513178` with version `0x800`, enumerates controllers through callback `0x00512ff0`, caps joypad count to four, sets deadzone `0x96`, sorts new-type pads, and prints `Found %d joypads`. |
| `0x00513370 PlatformInput__PollPadState` | `int __thiscall PlatformInput__PollPadState(void * this, int pad_index, bool rotate_buttons)` | Source-reference `PCLTShell::UpdateJoystick(int)`; bounds `pad_index`, swaps current/old state buffers when requested, polls the device, reacquires on `0x8007001e`, reads state, and rotates button bytes `0x30` through `0x33` for new-type pads. |
| `0x005134a0 CEngine__GrabScreenshot` | `void __thiscall CEngine__GrabScreenshot(void * this, int screenshot_index)` | Source-reference ltshell screenshot path; handles `Failed for %s`, checks formats `0x15/0x16`, locks the render target, formats `grabs\scr%.4d.tga`, calls `ImageIO__WriteTGA24`, unlocks, and releases surfaces. |
| `0x005135f0 PlatformInput__SetKeySinkCore` | `void __thiscall PlatformInput__SetKeySinkCore(void * this, void * key_sink)` | Called from `PLATFORM__SetKeySink`, `CFEPVirtualKeyboard__Shutdown`, and `CFEPVirtualKeyboard__Process`; stores `key_sink` into `this+0x33458` and returns with `RET 0x4`. |

Read-back evidence:

- `ApplyPlatformInputCoreWave848.java dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0`
- `ApplyPlatformInputCoreWave848.java apply`: `READBACK_OK` for all four rows and `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0`
- `ApplyPlatformInputCoreWave848.java final dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 4 metadata rows, 4 tag rows, 7 xref rows, 396 instruction rows, 81 xref-site instruction rows, 5 context metadata rows, and 4 decompile rows.
- String evidence: `grabs\scr%.4d.tga`, `Found %d joypads`, `Found no joypads`, and `Failed for %s`.
- Queue after Wave848: 6098 total, 5678 commented, 420 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5678/6098 = 93.11%`, strict clean-signature proxy `5678/6098 = 93.11%`.
- Next raw commentless row: `0x00513640 CEngine__GetConstant32`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-070518_post_wave848_platform_input_core_verified`, 19 files, 171871111 bytes, `DiffCount=0`.

What this proves:

- The four target function rows exist in the saved Ghidra project.
- The saved signatures/comments/tags are present and read back from the Ghidra project.
- Static retail evidence links the rows to DirectInput startup, pad polling, screenshot capture, and key-sink routing.

What remains unproven:

- Exact DirectInput interface and pad-state structure layouts.
- Runtime controller behavior.
- Runtime screenshot output/filesystem behavior.
- Runtime virtual-keyboard behavior.
- BEA patching behavior.
- Rebuild parity.
