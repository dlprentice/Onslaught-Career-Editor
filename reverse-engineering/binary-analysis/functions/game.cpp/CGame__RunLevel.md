# CGame__RunLevel

> Address: `0x0046e240`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/game.cpp:1573` (`CGame::RunLevel`) |
Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Top-level level driver. One-off `Init` → one-off `LoadResources`
(with a loading-bar choreography of 0→65→0.33→0.66→1.0→65–80) → restart
loop over `InitRestartLoop` / `RestartLoopRunLevel` /
`ShutdownRestartLoop` until the quit code leaves `QT_RESTART_LEVEL` (4),
with a demo-mode auto-restart guard capped at 5 attempts → one-off
`ShutdownRestartLoop` + `Shutdown`-equivalent teardown → returns the
final `EQuitType` in `[this+0x34]`. This wake adds the byte-level
sequencing: the exact restart predicate, the demo restart cap, the
failure exits that return `QT_LOAD_ERROR` (3), and the three inbound
callers (`CLTShell` stress-test and frontend loops).
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 disassembly of the
whole body (`local-lab/famA/RunLevel.txt`), raw byte reads (body hash,
float constants, `.rdata` strings), and a whole-`.text` rel32 xref scan
(`local-lab/famA_xrefs.py`). Call targets resolved against
[`../ghidra-function-name-table-2026-08-17.tsv`](../ghidra-function-name-table-2026-08-17.tsv).
No `FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Contract (byte-exact)

Body `0x0046e240`–`0x0046e45b` inclusive, **540 bytes**, SHA-256
`6bcb72c3a1d6e800ca77fea8e8a5f501b593905162b22adf21dd5c91f5bc9f7c`.
29 direct `E8`, zero `E9`. `this` in `ecx`; one stack argument at
`[esp+0x10]` after the three-register push (the level number, forwarded
to `RestartLoopRunLevel`); returns `EQuitType` in `eax` via `ret 4`.
Boundary: four `nop` (`0x0046e45c`–`0x0046e45f`) then `CGame__Render`
at `0x0046e460`.

1. `mQuit` cleared (`[esi+0x24] = 0`); if the stress-test flag
   `[0x0083d448]` is set, byte `[0x0066e8c0] = 1`.
2. `CConsole__SetLoading(1,1,1)` on the console singleton `0x00663498`.
3. If `[0x00662dcc]` set: `CMusic__Stop` on `0x00889a48`. If
   `[0x00662f40]` set: `CSoundManager__ReloadLanguageSampleBank` on
   `0x00896988`.
4. `[esi+0xa08] = 1` (first-time-round flag), then `Init`
   (`0x0046c360`). On failure: virtual `[vtable+8]` on `this` and
   **return 3 (`QT_LOAD_ERROR`)**.
5. Level number from `[esp+0x10]` stored to `[esi+0x2a0]`; then
   `InitRestartLoop` (`0x0046c430`). On failure:
   `ShutdownRestartLoop`, return 3.
6. `edi = -1` written to the four dwords `0x008552fc`–`0x00855308`
   (world-adjacent camera-slot scratch, cleared per run), then the
   one-off resource sequence: `LoadResources()` (`0x0046cd30`;
   failure → `FatalError__ExitWithLocalizedPrefix_A`
   with `.rdata 0x0062c140` = `"game resources"`),
   `CConsole__SetLoadingRange(50.0f, 65.0f)`, `CDXEngine__InitResources`
   (`0x0053d6d0`), `SetLoadingFraction(0.33f)`,
   `CGameInterface__InitResources` (`0x00472a10`),
   `SetLoadingFraction(0.66f)`, `CHud__LoadTextures` (`0x00481650`),
   `SetLoadingFraction(1.0f)`, `SetLoadingRange(65.0f, 80.0f)`
   — then `edi = 1` (`0x0046e38a`), the loop-continuation sentinel.
   Argument-passing note for `LoadResources`: the call site issues
   **no** stack pushes. The callee reads its two stack parameters from
   the caller's register-save area: `flag` slot = the saved `ebp`,
   which holds the level number (loaded from `[esp+0x10]` at
   `0x0046e2bc`), and `inLoadedSounds` slot = the saved `ebx`, which
   is 0. Effective call: `LoadResources(level, 0)`.
7. Restart loop (`ebp` counts demo-mode restarts; `edi` is the
   loop-continuation sentinel set to 1 before the loop and 0 on the
   restart path): per attempt it calls the three per-attempt texture
   loaders `CMessageBox__LoadPortraitTextures` (`0x004b7320`),
   `CMessageLog__LoadTextures` (`0x004b8e70`),
   `CPauseMenu__LoadPauseTextures` (`0x004d0510`), then
   `RestartLoopRunLevel(level)` (`0x0046dc30`); the returned quit code
   is kept in `[esi+0x34]`, then `ShutdownRestartLoop` runs.
8. **Demo auto-restart guard**: when the demo flag `[0x0083d454] == 4`
   and `ebp < 5`, the quit code in `[esi+0x34]` is **forced to 4**
   (`QT_RESTART_LEVEL`) and `ebp` increments — a demo loops its level
   at most five times before falling through.
9. Loop exit: quit code `!= 4` leaves the loop. Quit code `== 3`
   (`QT_LOAD_ERROR`) runs `FatalError_LocalizedStringId(-1, 0xf5, 0)`
   on the console (string id 245) and jumps to the common exit.
   Quit code `== 4` path: `[esi+0x24] = 1` (restart marker),
   `CMusic__Stop`, `InitRestartLoop` again (failure →
   `ShutdownRestartLoop`, `edi = 0`), then `[esi+0xa08] = 0` and the
   loop re-enters at the per-attempt texture loaders (step 7) — the
   one-off `LoadResources` block is **not** repeated on restart.
10. Common exit: `SetLoadingRange(0.0f, 50.0f)`, `[esi+0x24] = 0`,
    virtual `[vtable+8]` teardown on `this`, return `[esi+0x34]`.

Field map pinned by this body:

| Location | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x24]` | restart marker (`mQuit`-adjacent), set during restart, cleared on exit | `0x0046e247`, `0x0046e3f0`, `0x0046e42a` |
| `[this+0x34]` | current `EQuitType`, returned to the shell | `0x0046e3c5`, `0x0046e3e4`, `0x0046e439` |
| `[this+0xa08]` | first-time-round flag (1 before first attempt, 0 after) | `0x0046e297`, `0x0046e413` |
| `[this+0x2a0]` | requested level number | `0x0046e2c2` |
| `[0x0083d448]` | stress-test mode flag (read) | `0x0046e24a` |
| `[0x0083d454]` | demo mode flag; `== 4` enables the auto-restart cap | `0x0046e3cd` |
| `0x008552fc`–`0x00855308` | four camera-slot scratch dwords cleared to −1 per run | `0x0046e2eb`–`0x0046e2fd` |
| `0x00663498` | global `CConsole` | `0x0046e260` et al. |
| `0x00889a48` / `0x00896988` | global `CMusic` / `CSoundManager` | `0x0046e279`, `0x0046e28b` |

## Callers

Whole-`.text` rel32 scan: **three** inbound `E8`, zero `E9` —
`0x004f02b2` inside `CLTShell__RunStressTestLevelLoop`
(`ecx = 0x008a9a98`, the stress-test `CGame`), and `0x004f036e` /
`0x004f04f9` inside `CLTShell__RunFrontEndAndGameLoop` (`ecx =
0x008a9a98`; the `0x004f036e` site treats return `2`
(`QT_SYSTEM_QUIT`) as exit and otherwise loops the frontend). The
`CGame` object is the shell's static; there is no other construction
site reached by these calls. `0x004f0373` (`cmp eax, 2`) is the
frontend-loop's quit-code consumer, matching `EQuitType` from
`Platform.h:6`.

## Pinned-source status

`references/Onslaught/game.cpp:1573` is the source twin; the released
body matches its shape (one-off init/resources, restart loop, load-error
handling, exact `EQuitType` return) as recorded in
[`../cgame-level-lifecycle-semantics-2026-08-11.md`](../cgame-level-lifecycle-semantics-2026-08-11.md)
(`SOURCE_ID_RETAIL_BODY_DEMO_ENTRY`). What this wake adds from bytes:
the demo five-restart cap, the per-attempt texture-loader placement
inside the loop (not in one-off setup), the `QT_LOAD_ERROR` string-id
245 fatal path, and the exact `[this+0x34]` quit-code cell. Divergence
from a naive source reading: none observed; the demo-cap `ebp < 5` is
the one released-only behavior the pinned source does not spell out.

## Rebuild mapping

Owner **exists**:
`rebuild/OnslaughtRebuild.Core` campaign flow
(`RetailCampaignFlowTests`, `RetailWorldCatalog`) models level admission
and the frontend→game handoff; `RetailFrontendFlow` consumes a quit
code. The `EQuitType` values (0–7, `Platform.h:6`) and this driver's
restart law (repeat attempts while quit == 4; demo cap 5; load-error 3)
are the contract a Core `RunLevel` driver must encode. Focused test
deferred until that owner exists (same recorded decision as the IScript
native notes).

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x0046e240`–`0x0046e45b` is not
  `6bcb72c3…c9f7c`, or the body does not end `5b c2 04 00`.
- The restart comparison is anything but `cmp [esi+0x34], 4` /
  `jne exit` at `0x0046e3e4`–`0x0046e3e9`, or the demo cap is anything
  but `cmp ebp, 5 / jge` at `0x0046e3db`–`0x0046e3de`.
- A fourth inbound rel32 to `0x0046e240` appears, or the three recorded
  sites move.
- The failure exits return anything but `3` (`mov eax, 3` at
  `0x0046e2b3`, `0x0046e2da`).

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 whole-body disassembly
  (`local-lab/famA/RunLevel.txt`), raw byte reads (body hash; float
  constants `0x42820000`=65.0, `0x42480000`=50.0, `0x3ea8f5c3`=0.33f,
  `0x3f28f5c3`=0.66f, `0x3f800000`=1.0, `0x42a00000`=80.0; `.rdata`
  `0x0062c140` = `"game resources"`), whole-`.text` rel32 xref scan
  (`local-lab/famA_xrefs.py`), and name-table resolution
  (`tools/xref_targets.py`).
- Corroboration (not duplicated):
  [`../cgame-level-lifecycle-semantics-2026-08-11.md`](../cgame-level-lifecycle-semantics-2026-08-11.md)
  fixed the six-function decomposition and demo-twin status;
  `CGame__Init.md`, `CGame__InitRestartLoop.md`,
  `CGame__LoadResources.md`, `CGame__RestartLoopRunLevel.md`,
  `CGame__ShutdownRestartLoop.md` carry the callee-side notes updated
  the same wake.
