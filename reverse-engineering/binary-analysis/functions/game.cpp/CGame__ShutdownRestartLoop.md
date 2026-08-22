# CGame__ShutdownRestartLoop

> Address: `0x0046ca70`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/game.cpp:530`
(`CGame::ShutdownRestartLoop`) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Per-attempt teardown, run after every
`RestartLoopRunLevel` return and after every one-off failure exit.
Released ordering: music stop → script VM reset → loading-screen
restart arm → monitor core shutdown → two controller-slot virtual
releases → debug-marker/console bookkeeping → world shutdown → trees →
map membership → atmospherics → physics nested sets → particle
manager teardown → script events → event manager → PC mouse shutdown.
The loading bar is advanced through ten `SetLoadingFraction` steps
(0.6→1.0) as this teardown runs, so the released "Loading…" bar during
a restart is this function's progress meter.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly (`local-lab/famA/ShutdownRestartLoop.txt`), raw byte reads
(body hash; `.rdata` string window), whole-`.text` rel32 xref scan,
and name-table resolution. No `FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Contract (byte-exact)

Body `0x0046ca70`–`0x0046cd27` inclusive through the final `c3`,
**696 bytes**, SHA-256
`38c1f07334d847a519198795d6ac349121fee1f46a0e4bef15f72c168f9d9e28`.
41 direct `E8`, zero decoded `E9`. `this` in `ecx` (`esi`); returns
void. Boundary: eight `nop` (`0x0046cd28`–`0x0046cd2f`) then
`CGame__LoadResources`.

Released order (each step one `E8` unless noted):

1. Restart bookkeeping: when `[esi+0x34] == 4` (QT_RESTART_LEVEL) and
   stress-test flag `[0x0083d448]` set, byte `[0x0066e8c0] = 1`;
   `CMusic__Stop` on `0x00889a48` when `[0x00662dcc]` set;
   `CScriptObjectCode__Reset` on `0x0089c5e0` (`0x00539980`) — the
   script VM is reset, not destroyed.
2. Loading-screen restart arm: when `[esi+0x34] == 4`,
   `CConsole__SetLoading(1,1,1)`; then `RenderLoadingScreen(0,0)`,
   byte `[0x0066e8c0] = 0`, `CConsole__Status("Freeing Up Level
   Resources...")` (`.rdata 0x0062bf20`) — the status line the player
   sees during every restart teardown.
3. `CMonitor__Shutdown_Core(this)` (`0x004bacb0`).
4. Two controller-slot releases at `[esi+0x2e4]` and `[esi+0x2e8]`:
   non-null → virtual `[vtable+4](1)` and slot cleared.
5. `CDebugMarkers_T3_00441e50(0)` (`0x00441e50`, name-table label);
   `SetLoadingFraction(0.6f)`.
6. World teardown: `CWorld__ShutdownAndClear_Thunk` with
   `ecx = 0x00855090` (`0x0050abb0`) — the same world singleton
   `LoadLevel` fills.
7. `CDXTrees__Reset` on `0x009cc148` (`0x0055a400`);
   `CMapWho__Destroy` on `0x00704200` (`0x00491930`);
   `Atmospherics__Shutdown` (`0x00404c10`);
   `CWorldPhysicsManager__FreeNestedThingSets_6C` (`0x00510740`).
8. Particle manager teardown: owner `[0x009c63e8]` list walked with
   `CParticle__Destroy` (`0x004cae50`) and the list unlinked in place;
   then `CParticleManager__ClearParticleOwnerBacklinks` /
   `PruneDeadOwnerLinks` / `CleanupHandles` (`0x004caf30`,
   `0x004cb080`, `0x004caf60`); manager `[0x009c63f4]` non-null →
   `CParticleManager__Shutdown` + `CDXMemoryManager__Free` with the
   manager pointer, cell cleared (`0x004cb1b0`, `0x00549220` on
   `0x009c3df0`).
9. `CScriptEventNB__DestroyAllEvents` on `0x0089c590` (`0x005388d0`).
10. `CEventManager__Shutdown` with `ecx = 0x00672fc8` (`0x0044b1f0`)
    — the same singleton `IScript__SetTimer` schedules against.
11. Final PC-specific action: `PlatformInput__ShutdownMouse`
    (`0x0042d3b0`). Return.

Field map pinned by this body:

| Location | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x34]` | quit code (== 4 arms the restart loading path) | `0x0046ca7c`, `0x0046caac` |
| `[this+0x2e4] / [+0x2e8]` | two controller-slot pointers released via `[vt+4](1)` | `0x0046cae9`, `0x0046cb00` |
| `0x00855090` | global `CWorld` (shutdown) | `0x0046cbf8` |
| `0x0089c5e0 / 0x0089c590` | script VM / script-event owner singletons | `0x0046caa2`, `0x0046cced` |
| `0x00672fc8` | global `CEventManager` | `0x0046cd06` |
| `0x009c63e8/0x009c63f0/0x009c63f4` | particle owner list head/next/manager | `0x0046cc75`–`0x0046cce2` |
| `0x0062bf20` | `"Freeing Up Level Resources..."` | `0x0046cad3` |

## Callers

Whole-`.text` rel32 scan: **five** inbound `E8`, zero `E9` —
`0x0046dc7f` and `0x0046dcfd` in `CGame__RestartLoopRunLevel`
(`LoadLevel` / `PostLoadProcess` failure exits), and `0x0046e2d3`,
`0x0046e3c8` (after every attempt), `0x0046e409` (InitRestartLoop
failure on the restart path) in `CGame__RunLevel`. This matches the
lifecycle note's "called from both `RestartLoopRunLevel` and
`RunLevel`" with exact sites.

## Pinned-source status

`references/Onslaught/game.cpp:530` is the source twin; the lifecycle
note already recorded the released ordering as material
(`BOUNDED_SEMANTIC_DIVERGENCE` demo twin preserves all 33 calls). This
wake pins the retail ordering to exact addresses and adds: the script
VM is **reset** (`CScriptObjectCode__Reset`), not destroyed, on the
per-attempt path; the ten-step loading-fraction choreography; the
`"Freeing Up Level Resources..."` status string; and the mouse
shutdown as the final action. Divergence from the older note: none
material; its "stops music/scripts as needed" is now the exact
`[0x00662dcc]` gate plus unconditional `CScriptObjectCode__Reset`.

## Rebuild mapping

No Core owner yet models per-attempt teardown ordering. The campaign
flow owner (`RetailCampaignFlowTests`) owns attempt counting, not
resource lifecycles. When a teardown owner lands, the released order
above is the contract — most importantly world-before-trees, particles
after physics, script events before the event manager, mouse last.
Implementing the ordering differently is false to the shipped game.
Focused test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x0046ca70`–`0x0046cd27` is not
  `38c1f073…9e28`, or the body does not end `5e 5d 5b c3`.
- The world teardown immediate is anywhere but `0x00855090`, or
  `CWorld__ShutdownAndClear_Thunk` anywhere but `0x0050abb0`.
- The event-manager shutdown immediate is anywhere but `0x00672fc8`,
  or the call anywhere but `0x0044b1f0`.
- The final `E8` before the pops is anywhere but `0x0046cd1f`
  targeting `0x0042d3b0`.
- A sixth inbound rel32 to `0x0046ca70` appears, or any of the five
  recorded sites moves.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 whole-body
  disassembly (`local-lab/famA/ShutdownRestartLoop.txt`), raw byte
  reads (body hash; `.rdata 0x0062bf20` window), whole-`.text` rel32
  xref scan (`local-lab/famA_xrefs.py`), name-table resolution
  (`tools/xref_targets.py`; the raw-scan hits at `0x0046cbe0`–
  `0x0046cbec` are mid-instruction bytes of the
  `SetLoadingFraction`/world-teardown window, not code).
- Corroboration (not duplicated):
  [`../../cgame-level-lifecycle-semantics-2026-08-11.md`](../../cgame-level-lifecycle-semantics-2026-08-11.md)
  (released-ordering claim + demo twin status);
  [`../CEventManager.cpp.md`](../CEventManager.cpp.md) pins
  `0x00672fc8`; `IScript__SetTimer.md` pins the same singleton from
  the native side; `CGame__LoadLevel.md` pins the world fill this body
  tears down.
