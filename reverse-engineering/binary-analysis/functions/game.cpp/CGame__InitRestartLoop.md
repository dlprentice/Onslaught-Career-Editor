# CGame__InitRestartLoop

> Address: `0x0046c430`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/game.cpp:292`
(`CGame::InitRestartLoop`) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Per-attempt reset and allocation owner, called once before the
first attempt and again on every `QT_RESTART_LEVEL`. Resets attempt
clocks/score/camera state, re-inits input, HUD, event manager,
map-membership, interface menu state, render-queue var, and script
listeners; allocates the two fear grids, message box, message log,
pause menu, help display, briefing log, and seeds the deterministic
random stream with `123456` (0x1e240); then schedules the three-second
pre-run event 2001 (`0x7d1`) time-from-now against the global event
manager — the same scheduler subsystem `IScript__SetTimer` files its
event 2002 against.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly (`local-lab/famA/InitRestartLoop.txt`), raw byte reads
(body hash; float constants), whole-`.text` rel32 xref scan, and
name-table resolution. No `FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Contract (byte-exact)

Body `0x0046c430`–`0x0046c98e` inclusive through the final `c3`,
**1375 bytes**, SHA-256
`c54f1867544f2627462ed3f1fa704b405a89a96db0f00db430923cd1b15a3b02`.
43 direct `E8`, zero decoded `E9`. MSVC SEH frame
(`push -1; push 0x5d28db; fs:[0]`). `this` in `ecx` (`ebp`);
returns int (nonzero success).

Measured order:

1. Input/HUD reset: `PlatformInput__InitMouse` (`0x0042d310`);
   `CDXLandscape__ResetCameraPosition` on `[0x0089c9b0]`
   (`0x00546b10`); `CHud__Reset` on `0x008aa4e8` (`0x004815c0`).
2. Attempt-state clears: `[ebp+0xf4] = 0`; `[ebp+0xec] = 3.0f`
   (float constant `0x40400000`, the three-second pre-run window);
   `[ebp+0xc] = -1.0f`; `[ebp+0x48] = -1.0f`;
   `[ebp+0x38] = 1`.
3. Score/clock/camera resets and the eight in-body allocation sites:
   `CDXMemoryManager__Alloc` on `0x9c3df0` (`0x005490e0`) for the two
   fear grids (`CFearGrid__ctor_base` at `0x0046c634`/`0x0046c671`),
   message box (`CMessageBox__ctor_base` at `0x0046c6b1`), message log
   (`CMessageLog__ctor_base` at `0x0046c6ee`), pause menu
   (`PauseMenu__Init` at `0x0046c72c`), help display
   (`CHelpTextDisplay__ctor` at `0x0046c769`), and briefing log
   (`CLevelBriefingLog__ctor` at `0x0046c7a6`). Each site follows the
   same shape: alloc → null-check → ctor → `jmp +2` over a
   `xor eax, eax` failure join. The raw byte scan's `E9` hits inside
   this body are those two-byte `eb 02` skips plus mid-instruction
   bytes — **no decoded `E9` exists**.
4. Deterministic random seed: `RandomSeedPair__Set(0x1e240, 0)`
   (`0x004de8c0`) — 123456 as the fixed seed, matching the lifecycle
   note.
5. Event manager and listeners: `CGame__ClearDwordValue` scratch
   (`0x00441e40`); `CEventManager__Init` with `ecx = 0x00672fc8`
   (`0x0044b060`); particle/map-membership clears
   (`[0x9c6400]/[0x9c63f4]/[0x9c63f0]/[0x9c6404] = 0`);
   `CMapWho__Init` on `0x00704200` (`0x004919b0`);
   `CGameInterface__ResetMenuState` (`0x004729e0`);
   `CDXEngine__InitConsoleVar_UseRenderQueue` (`0x005515a0`);
   `CScriptEventNB__CreateListenerSet` on `0x0089c590`
   (`0x00538860`).
6. Pre-run event schedule: `CEventManager__AddEvent_TimeFromNow(
   &[ebp+0xec], 0x7d1, this, 0, 0, 0)` with `ecx = 0x00672fc8`
   (`0x0044b2d0`) — event **2001**, receiver = the CGame object,
   delay = the `[ebp+0xec]` float set to 3.0f in step 2. This is the
   pre-run event the lifecycle note records as "queues the
   three-second pre-run event", now pinned to number 2001.
   `[ebp+0x28] = 1`; `[ebp+0x2c] = 0`; `[ebp+0x9cc] = 0`;
   `[ebp+0x9fc]/[+0xa00] = -1`.
7. Console registration block: nine `CConsole__RegisterCommand`
   (`0x0042af80`) for Map/Win/Lose/RemoteCameraOn/Off/NavMapOn/Off and
   two debug-squad/unit toggles, then four `CConsole__RegisterVariable`
   (`0x0042b040`) for the split-screen/frame-length CVars — matching
   the older note's list; the first frame-length string follows
   `"Should memory deltas be shown?"` in `.rdata` (`g_framelength`).
8. Cursor centering: `Input__UpdateCursorCenterWithWindowScale`
   (`0x0042da00`). Success tail returns nonzero.

Field map pinned by this body:

| Location | Meaning | Anchor |
| --- | --- | --- |
| `[this+0xec]` | pre-run delay float (3.0f) and AddEvent reference | `0x0046c488`, `0x0046c5d4` |
| event `0x7d1` (2001) | pre-run event number filed against CGame | `0x0046c5df` |
| `0x00672fc8` | global `CEventManager` (init + schedule) | `0x0046c582`, `0x0046c5e5` |
| `0x009c3df0` | global allocator for the seven restart-local objects | `0x0046c609`, `0x0046c620` region |
| `0x008aa4e8 / 0x0089c590 / 0x00704200` | CHud / script-listener / map-membership owners | cited call sites |

## Callers

Whole-`.text` rel32 scan: **two** inbound `E8` — `0x0046e2c8`
(one-off setup, after `Init` success) and `0x0046e3fe` (restart path,
after `CMusic__Stop`), both in `CGame__RunLevel`. Zero `E9`.

## Pinned-source status

`references/Onslaught/game.cpp:292` is the source twin; the lifecycle
note already fixed ownership ("resets the attempt clock, score,
cameras, controllers, objectives, quit/game state, event manager,
particles, map membership, interface and script listeners … seeds …
with 123456, then queues the three-second pre-run event"). Bytes add:
the pre-run event **number is 2001** (sibling to native 19's 2002 on
the same scheduler), the delay cell is `[this+0xec]`, the seven
allocation sites with their ctors, and the nine-command/four-variable
console block addresses. Divergence from the older note: none material.

## Rebuild mapping

Mechanism owner **exists** for the scheduler half:
`rebuild/OnslaughtRebuild.Core/RetailEventScheduler.cs` models
`AddEventTimeFromNow`; this body instantiates it with
`(delay=3.0f, eventNum=2001, toCall=CGame)` per attempt. No Core owner
yet binds CGame attempt-reset to it. When an attempt-setup owner lands,
bind step 6 exactly (2001, receiver=this, reuse=none). Focused test
deferred until that owner exists — same recorded decision as native
19.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x0046c430`–`0x0046c98e` is not
  `c54f1867…a3b02`, or the body does not end with pops and `c3`.
- The pre-run event immediate is anything but `push 0x7d1` at
  `0x0046c5df`, or the delay reference anywhere but `[ebp+0xec]`.
- The seed immediate is anything but `push 0x1e240` at `0x0046c7e4`.
- A third inbound rel32 to `0x0046c430` appears, or either recorded
  site moves.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 whole-body
  disassembly (`local-lab/famA/InitRestartLoop.txt`), raw byte reads
  (body hash; float constants `0x40400000`=3.0f, `0xbf800000`=−1.0f;
  `.rdata` continuation check confirming `"g_framelength"` follows the
  Init CVar strings), whole-`.text` rel32 xref scan
  (`local-lab/famA_xrefs.py`), name-table resolution
  (`tools/xref_targets.py`; the raw-scan hits at
  `0x0046c63d…0x0046c7f4` are the eight alloc-failure `jmp +2` joins
  decoded in context, not code entries).
- Corroboration (not duplicated):
  [`../cgame-level-lifecycle-semantics-2026-08-11.md`](../cgame-level-lifecycle-semantics-2026-08-11.md)
  (ownership list, seed claim);
  [`IScript__SetTimer.md`](IScript.cpp/IScript__SetTimer.md) pins the
  same `AddEvent_TimeFromNow` ABI from the native side;
  [`../RetailEventScheduler.cs`](../../../rebuild/OnslaughtRebuild.Core/RetailEventScheduler.cs)
  encodes the callee's admission laws with tests.
