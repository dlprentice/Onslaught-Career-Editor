# Ghidra GameInterface Menu-Control Boundary Wave952 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `game-interface-menu-control-boundary-wave952`

Wave952 re-reviewed the CGameInterface menu execution/render cluster and recovered one missing vtable-slot function boundary at `0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput`. The pass created one function object, saved a bounded `void __thiscall` signature, comment, and tags, made no executable-byte change, did not launch BEA, and kept runtime pause/menu/input behavior as separate proof.

## Target

| Address | Saved state | Static evidence |
| --- | --- | --- |
| `0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput` | `void __thiscall CGameInterface__VFunc_03_HandleMenuControlInput(void * this, void * control_context, int button_id, int button_context)` | CGameInterface vtable `0x005dbc2c` slot `3` points at `0x00472d50`; pre-metadata had no function there; instruction evidence starts after `CGameInterface__HandleMenuSelection` `RET 0x4` and padding, dispatches button/control IDs `0x2a..0x39`, calls `CGameInterface__AdvanceMenuSelectionWithWrap`, `CGameInterface__HandleMenuSelection(control_context)`, `CController__RelinquishControl(control_context)`, and `CGame__UnPause(&DAT_008a9a98)`, then returns with `RET 0x0c`. |

## Read-Back Evidence

- `ApplyGameInterfaceMenuControlBoundaryWave952.java dry`: `updated=0 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- `ApplyGameInterfaceMenuControlBoundaryWave952.java apply`: `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyGameInterfaceMenuControlBoundaryWave952.java final dry`: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 6 metadata rows, 6 tag rows, 8 xref rows, 1714 instruction rows, 6 decompile rows, and 16 post-vtable rows.
- Queue after Wave952: 6151 total functions, 6151 commented, 0 commentless, 0 exact-undefined signatures, 0 `param_N`, strict export-contract closure `6151/6151 = 100.00%`.
- Wave911 focused re-audit progress after Wave952: `276/1408 = 19.60%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-091135_post_wave952_game_interface_menu_control_boundary_verified`, 19 files, 173542279 bytes, `DiffCount=0`.

## What This Proves

- The saved Ghidra project now has a function object at `0x00472d50`.
- The saved function name, signature, comment, and tags match the Wave952 static boundary claim.
- The CGameInterface vtable slot `3` now resolves to the recovered function.
- The recovered body statically connects CGameInterface menu-control dispatch with selection movement, selection execution, controller relinquish, and unpause paths.

## What Remains Unproven

- Exact source method name.
- Individual button semantic labels beyond the observed IDs and call paths.
- Meaning of `0x00679fbc`.
- Runtime pause/menu/input behavior.
- BEA patching behavior.
- Rebuild parity.
