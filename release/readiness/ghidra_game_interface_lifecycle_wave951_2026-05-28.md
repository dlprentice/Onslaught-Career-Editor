# Ghidra Game Interface Lifecycle Wave951 Readiness Note

Status: complete read-only static evidence
Date: 2026-05-28
Scope: `game-interface-lifecycle-wave951`

Mutation status: no mutation.

Wave951 re-reviewed the CGame/GameInterface lifecycle and pause-menu state bridge after Wave950. The pass was read-only: no Ghidra mutation, no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, and no BEA launch.

Primary targets:

| Address | Evidence |
| --- | --- |
| `0x0046c210 CGame__ctor` | Called by `0x00541f10 CDXGame__ctor`; constructor first installs the IController vtable, initializes CGame-shaped state, then installs the CGame vtable `0x005dbbb4`. |
| `0x0046c2d0 CGame__dtor` | Called by `0x0046c2b0 CGame__scalar_deleting_dtor` and jumped to by `0x00541f00 CDXGame__dtor_thunk`; restores the CGame vtable, removes two active-reader style links when present, and calls `CMonitor__Shutdown`. |
| `0x004729d0 CGameInterface__ctor_base` | Constructor-style base body called from the global GameInterface setup path; initializes the monitor/control field and installs the `0x005dbc2c` GameInterface vtable anchor. |
| `0x004729e0 CGameInterface__ResetMenuState` | Called by `0x0046c360 CGame__Init` and `0x0046c430 CGame__InitRestartLoop`; clears fade/selection/menu-active state, enables six menu entries, enables background rendering, and sets menu mode `1`. |
| `0x00472ad0 CGameInterface__AdvanceMenuSelectionWithWrap` | Called by the menu input/selection path; advances selected entry `this+0x20`, respects disabled entry flags `this+0x2c..0x40`, uses a shorter option-submenu limit in mode `2`, and plays frontend move sound when selection changes. |

Context anchors:

- CGame/CDXGame lifecycle: `0x0046c2b0 CGame__scalar_deleting_dtor`, `0x00541f00 CDXGame__dtor_thunk`, `0x00541f10 CDXGame__ctor`, and `0x00541f30 CDXGame__scalar_deleting_dtor`.
- Startup/restart callers: `0x0046c360 CGame__Init` and `0x0046c430 CGame__InitRestartLoop`.
- GameInterface lifecycle/menu context: `0x00472a10 CGameInterface__InitResources`, `0x00472a50 CGameInterface__Shutdown`, `0x00472a90 CGameInterface__ToggleMenuDisplay`, `0x00472b40 CGameInterface__HandleMenuSelection`, and `0x00472f10 CGameInterface__Render`.

Read-back evidence:

- Primary exports: 5 metadata rows, 5 tag rows, 7 xref rows, 146 instruction rows, and 5 decompile rows.
- Context exports: 11 metadata rows, 11 tag rows, 15 xref rows, 2080 instruction rows, and 11 decompile rows.
- Vtable export: 2 anchors and 64 slot rows. The useful rows are the `0x005dbc2c` GameInterface prefix and the `0x005e509c` CDXGame/CGame prefix; later rows in those 32-slot windows intentionally overrun into adjacent constants/tables and are not treated as vtable proof.
- Wave911 focused re-audit progress after Wave951 is `271/1408 = 19.25%`.
- Static export-contract function-quality closure remains `6150/6150 = 100.00%`.
- Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-083735_post_wave951_game_interface_lifecycle_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.

What remains unproven:

- Exact GameInterface source-file body identity.
- Concrete CGame/GameInterface object layouts beyond observed static offsets.
- Runtime pause/menu/input/render behavior.
- BEA patching behavior.
- Rebuild parity.
