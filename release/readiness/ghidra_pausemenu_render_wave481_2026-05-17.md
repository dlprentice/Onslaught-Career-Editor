# Ghidra PauseMenu Render Wave481 Readiness

Date: 2026-05-17

## Scope

- Corrected `0x004d11d0` from stale `CEngine__RenderOverlayAndMenuTransitions` to `CPauseMenu__Render`.
- Corrected `0x004a4810` `CMenuItemRange__Render` return type from `int` to `short *`.
- Evidence: `CDXEngine__PostRender` source-aligned `GAME.GetPauseMenu()->Render()` caller, `CFEPOptions__Update` / `g_pOptionsContext` caller path, post-readback decompile, xrefs, tags, and instruction rows.

## Validation

- `py -3 tools\ghidra_pausemenu_render_wave481_probe_test.py`
- `py -3 tools\ghidra_pausemenu_render_wave481_probe.py --check`
- `cmd.exe /c npm run test:ghidra-pausemenu-render-wave481`
- Refreshed static queue: `6057` functions, `3897` commentless, `1702` undefined signatures, `1551` `param_N` signatures.

## Backup

- `[maintainer-local-ghidra-backup-root]\BEA_20260517-030002_post_wave481_pausemenu_render_verified`
- Verified: `19` files, `157289351` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary and source-callsite evidence only. Concrete `CPauseMenu` / menu-range layouts, runtime pause/options UI behavior, exact source body identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
