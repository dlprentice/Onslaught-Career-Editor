# Ghidra Input/Cursor Wave567 Readiness Note

Date: 2026-05-18
Status: PASS

## Scope

Wave567 hardened seven saved Ghidra rows:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005234d0` | `void __cdecl PlatformInput__SetGlobalInputState(int global_input_state)` | `PlatformInput__InitMouse` pushes `1`, `PlatformInput__ShutdownMouse` pushes `0`, and the body writes `DAT_0089bdf0`. |
| `0x005234e0` | `int __stdcall Input__HandleMouseWindowMessage(uint message, uint wparam, uint lparam)` | The caller at `0x00512f83` gates Windows mouse messages `0x200..0x20a`; `RET 0x0c` proves three stdcall arguments. The body updates stored mouse x/y from `lparam`, normalizes by window dimensions, scales to 640x480 under CVBufTexture global mode, tracks button latches, and accumulates wheel delta from `wparam`. |
| `0x00523b50` | `int __cdecl CDXEngine__GetCursorStateInRect(float left, float top, float right, float bottom)` | GameInterface, FrontEnd, and ControlsUI callers pass four rectangle bounds; the body checks cursor-ready `DAT_0089bdf4`, key-trap/dev-mode gates, and `[left,right)` / `[top,bottom)` bounds. |
| `0x00523bc0` | `uint __cdecl Input__DispatchClickInRect(float left, float top, float right, float bottom, int button_action)` | `CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture` passes four rectangle bounds plus an action id; the body consumes `DAT_0089bdfc` on hit and calls `CFrontEnd__ReceiveButtonAction(&DAT_0089d758,DAT_008a9564,button_action,1.0)`. |
| `0x00523cc0` | `uint __cdecl Input__GetClickStateInRect(float left, float top, float right, float bottom)` | Modal, GameInterface, MessageLog, FrontEnd, controller-definition, controls-list, and multiplayer-start callers use this click rectangle predicate; the body consumes `DAT_0089bdfc` on a hit. |
| `0x00523d40` | `uint __cdecl Input__GetCursorStateInRectAndConsume(float left, float top, float right, float bottom)` | Modal and directory-page callers use this cursor rectangle predicate; the body consumes `DAT_0089bdf4` on a hit. |
| `0x00523db0` | `void __cdecl Input__ResetMouseTransientState(void)` | Corrected from the misleading `CProfiler__ResetAll` label. The body clears cursor/click button down/up latches, click-ready and cursor-ready flags, wheel accumulator, and `DAT_00640054`; xrefs include input init/shutdown, frontend process, game main loop, and two no-function render-tail callsites. |

No `source-parity` tag was applied. Stuart's source has useful mouse-message and `CProfiler::ResetAll` / `CVBufTexture::ResetAll` callsite hints, but this saved tranche is bounded to retail input-state behavior rather than exact source identity.

## Verification

- Dry pass: `updated=0 skipped=7 renamed=0 would_rename=1 missing=0 bad=0`
- Apply pass: `updated=7 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `7` metadata rows, `7` tag rows, `31` xref rows, `679` focused instruction rows, `7` target decompiles, and `378` input/cursor callsite instruction rows
- Queue refresh: `6089` total functions, `2817` commented, `3272` commentless, `1494` exact-undefined signatures, `1174` `param_N` signatures
- Strict proxy: `2817 / 6089 = 46.27%`
- Focused probe: `py -3 tools\ghidra_input_cursor_wave567_probe.py --check` PASS
- NPM wrapper: `cmd.exe /c npm run test:ghidra-input-cursor-wave567` PASS
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-221852_post_wave567_input_cursor_verified`
- Backup verification: `19` files, `159943559` bytes, source/destination manifest hash `7DE67F4FB6FFBF25E3456303303D087CE10DEEC1A1BE8157ADE80769A0CCB72F`

## Limits

This is saved static Ghidra evidence only. Runtime mouse/window behavior, exact global names, exact source identity, BEA launch, game patching, and rebuild parity remain unproven.
