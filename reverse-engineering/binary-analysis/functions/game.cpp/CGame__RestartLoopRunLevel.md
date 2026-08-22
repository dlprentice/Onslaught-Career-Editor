# CGame__RestartLoopRunLevel

> Address: `0x0046dc30`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/game.cpp:1260`
(`CGame::RestartLoopRunLevel`) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: One attempt, start to quit code. Loads the level, post-load
processes it, runs the optional intro FMV, executes `autoexec.con`,
runs the pre-run update phase (wait-for-start), selects tutorial vs
in-game music by a level==100 comparison, then calls `MainLoop` until
`[this+0x34]` is nonzero — with an in-loop timeout law that force-wins
or force-loses the level when global timers expire. On exit: kills all
samples, records end-level data, trims VBuffers, releases four player
slots, and returns `[this+0x34]`.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly (`local-lab/famA/RestartLoopRunLevel.txt`), raw byte reads
(body hash; `.rdata` string windows; float constants), whole-`.text`
rel32 xref scan, and name-table resolution. No `FUN_*` milled; no Core
owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Contract (byte-exact)

Body `0x0046dc30`–`0x0046e22a` inclusive through the final
`c2 04 00`, **1531 bytes**, SHA-256
`dee636c3cc58ab1e673357436d2447b17aa379f79afa4a09bcc23905fa4a45f6` —
57 direct `E8`, **two decoded `E9`** (both at failure tails
`0x0046dc89`/`0x0046dd07`, jumping to the common epilogue
`0x0046e211`). MSVC SEH frame (`push -1; push 0x5d293b; fs:[0]`),
0x10c locals. `(int level)` forwarded from the caller's stack. Returns
the quit code via `ret 4`.

Sequence:

1. First-time-round loading range: when `[esi+0xa08] == 0`,
   `CConsole__SetLoadingRange(0.0f, 80.0f)`.
2. `LoadLevel(level)` (`0x0046cdf0`). Failure →
   `ShutdownRestartLoop`, `eax = 3`, `E9` to epilogue.
3. Intro-FMV gate (only when `[esi+0xa08] != 0`, demo flags
   `[0x00663050]/[0x0083d448]/[0x0083d454]` in their non-demo arms,
   and `[esi+0x30] != 0`): `lookup_FMV([esi+0x30], 0)` (`0x00523120`)
   → hit ≠ -1 and stress flag clear → `SetLoadingRange(100.0f, 80.0f)`
   else `SetLoadingRange(90.0f, 80.0f)`.
4. `PostLoadProcess` (`0x0046d040`). Failure → `ShutdownRestartLoop`,
   `eax = 3`, second `E9` to epilogue.
5. Memory dump + debug registration block:
   `CMemoryManager__DumpMemory`; nine `CConsole__RegisterCommand`
   calls (`0x0042af80`) registering the gameplay console commands;
   byte `[0x0062ba44]` cleared after read.
6. `autoexec.con`: `CConsole__ExecScript("autoexec.con")`
   (`.rdata 0x0062c0f4`, `0x0042ad30`), bracketed by
   `SetLoadingFraction(0.6f)` / `(0.7f)`; then
   `MEM_MANAGER__Cleanup` with `ecx = 0x009c3df0` (`0x00549270`).
7. Wait-for-start / pre-run window: `CController__SetToControl(
   [esi+0x2b4], &deadline)` where `deadline = PLATFORM__GetSysTimeFloat()
   + [esp+0x14]` (constant loaded to the stack cell before the call);
   `PLATFORM__Process` on `0x0088a0a8` (`0x00515880`); virtual
   `[vt+8]` on the controller; loop while now < deadline, toggling
   byte `[0x0062493c]` and re-rendering the loading screen
   (`RenderLoadingScreen`); then `CController__GetToControl` — when it
   returns the deadline cell address, `InactivityMeansQuitGame`
   decides an early quit (`0x0042d810`).
8. Music selection: `eax = [esi+0x30]; cmp eax, 0x64` — level 100 gets
   selection `2`, every other level `4`;
   `CMusic__PlaySelection` on `0x00889a48` (`0x004bb8c0`). The
   2026-06-24 CDB observation of `CMusic__PlaySelection` returning to
   `0x0046e0bf` lands exactly here (return site = next instruction).
9. Loading completion: `SetLoading(0,0,0)`; main loop:
   `ebx = 5` seed; repeat `{ if ([esi+0x34]==0) { …timeout checks…
   } MainLoop(this) }` while `[esi+0x34] == 0`. Timeout law inside:
   three float comparisons against `.rdata` constants
   (`0x005db4d0`, `0x005d85d8`, `0x005db1e4`) using global time
   `[0x00672fd0]`; when one fires **and** `[esi+0x28] == 4`,
   `[esi+0x34] = 1` and `[esi+0x28] = ebx` — a timed force-win path.
   `[0x0083d454] > 0` (demo mode) additionally enables
   `CEngine__SetOptionValueAndNotifyTarget(1)` over up to
   `[esi+0x29c]` slots.
10. Exit tail: `CSoundManager__KillAllSamples` on `0x00896988`
    (`0x004e12b0`); when the quit code is 6, 4, or 7 —
    `QT_TIMEOUT`, `QT_RESTART_LEVEL`, `QT_USER_TITLE_SCREEN` per
    `Platform.h:6` — play frontend sound via `CFrontEnd__PlaySound(1)`
    (`0x00468770`) and `CSoundManager__UpdateStatus`
    (`0x004e1b20`); `CGame__FillOutEndLevelData(this)` (`0x0046d470`);
    `Atmospherics__Shutdown` (`0x00404c10`);
    `CEngine__TrimVbIbPoolCapacitiesPow2` (`0x005015c0`); release four
    slots starting `[esi+0x284]`/`[esi+0x2a4]` region via virtual
    `[vt+4](1)` / `[vt+0x20](1)` pairs; return `[esi+0x34]`.

Field map pinned by this body:

| Location | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x30]` | current level (drives FMV lookup and level-100 music) | `0x0046dcbb`, `0x0046e0a6` |
| `[this+0x34]` | quit code cell (loop condition and return) | `0x0046e0cc`, `0x0046e18a`, `0x0046e20d` |
| `[this+0xa08]` | first-time-round flag | `0x0046dc52`, `0x0046dc8e` |
| `[this+0x2b4]` | first controller | `0x0046df70`, `0x0046dff7` |
| `[this+0x29c]` | slot count for the demo option sweep | `0x0046e0f1` |
| `[this+0x28]` | state cell checked `== 4` by the force-win path | `0x0046e157`, `0x0046e187` |
| `0x00672fd0` | global time float (timeout base) | `0x0046e144`, `0x0046e15f`, `0x0046e16d` |
| `0x005db4d0 / 0x005d85d8 / 0x005db1e4` | timeout thresholds (.rdata floats, values not re-derived this wake) | cited sites |
| `0x889a48 / 0x896988` | global `CMusic` / `CSoundManager` | `0x0046e0b5`, `0x0046e19a` |

The `CWaitForStart__ctor` object (`0x0046dbd0`) noted previously sits
immediately before this body and its vtable functions serve the
wait-for-start sink used in step 7's window.

## Callers

Whole-`.text` rel32 scan: **one** inbound `E8` — `0x0046e3be` in
`CGame__RunLevel`'s restart loop (see
[`CGame__RunLevel.md`](CGame__RunLevel.md)). Zero other callers; zero
additional `E9`.

## Pinned-source status

`references/Onslaught/game.cpp:1260` is the source twin; the lifecycle
note bounds the demo twin (`BOUNDED_SEMANTIC_DIVERGENCE`: demo omits
the wait-for-start controls block). This wake pins the retail-only
block to addresses and adds: the exact autoexec.con bracketing, the
level==100 music-selection comparison (source parity with
`CGame__PlayMusicForCurrentLevel` confirmed as an inline branch, not a
call), the two-tail `E9` shape, the quit-code 6/4/7 sound arm, and the
timed force-win law against `[this+0x28] == 4`. Divergence: none
material against the pinned source reading recorded in the lifecycle
note.

## Rebuild mapping

Owner candidates exist but none owns this contract:
`RetailCampaignFlowTests` owns attempt counting; Level100's mission
program owns in-mission flow. What has no owner yet: the per-attempt
pre-run law (wait-for-start deadline, inactivity quit check), the
level-100 music rule, and the timed force-win path. When an attempt
driver owner lands, encode steps 7–10 verbatim. Focused test deferred
until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x0046dc30`–`0x0046e22a` is not
  `dee636c3…4e45f6`, or the body does not end `8b 46 34 … c2 04 00`.
- The music branch compares anything but `cmp eax, 0x64` /
  selections `2` and `4`, or `CMusic__PlaySelection` resolves anywhere
  but `0x004bb8c0`.
- The two `E9` instructions do not both target `0x0046e211`.
- `ExecScript`'s argument is anywhere but `.rdata 0x0062c0f4`
  (`"autoexec.con"`), or the call anywhere but `0x0042ad30`.
- A second inbound rel32 to `0x0046dc30` appears.
- The return-site expectation breaks: the instruction after
  `call 0x004bb8c0` at `0x0046e0ba` is not `0x0046e0bf`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 whole-body
  disassembly (`local-lab/famA/RestartLoopRunLevel.txt`), raw byte
  reads (body hash; `.rdata` windows `0x0062c0f4`, `0x0062ba44`,
  `0x0062493c`; float constants `0x42c80000`=100.0, `0x42b40000`=90.0,
  `0x42a00000`=80.0), whole-`.text` rel32 xref scan
  (`local-lab/famA_xrefs.py`), name-table resolution
  (`tools/xref_targets.py`; raw-scan hits at `0x0046e211`,
  `0x0046ddc0`, `0x0046e180`, etc. are intra-body jump/call targets of
  this function, not missing functions).
- Corroboration (not duplicated):
  [`../cgame-level-lifecycle-semantics-2026-08-11.md`](../cgame-level-lifecycle-semantics-2026-08-11.md)
  (decomposition, demo divergence, CMusic CDB provenance note);
  [`CGame__MainLoop.md`](CGame__MainLoop.md),
  [`CGame__Update.md`](CGame__Update.md),
  [`CWaitForStart__ctor.md`](CWaitForStart__ctor.md),
  [`CGame__PlayMusicForCurrentLevel.md`](CGame__PlayMusicForCurrentLevel.md),
  [`CGame__FillOutEndLevelData.md`](CGame__FillOutEndLevelData.md)
  carry the callee-side notes.
