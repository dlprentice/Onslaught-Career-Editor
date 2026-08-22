# CGame__LoadLevel

> Address: `0x0046cdf0`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/game.cpp:685` (`CGame::LoadLevel`) |
Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Per-attempt level construction. Logs `"Game::LoadLevel %d"`,
stores the level id at `[this+0x30]`, resets the player count to the
multiplayer verdict of the freshly loaded world, reads the world file
into the global `CWorld` singleton `0x00855090`, allocates one 0x50-byte
`CPlayer` and one 0x178-byte `CController` per player from
`CDXMemoryManager__Alloc`, then builds tree geometry, renders a loading
frame, sets the engine track slot, and returns success. This is the
only place the retail binary constructs players/controllers for an
attempt.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly (`local-lab/famA/LoadLevel.txt`), raw byte reads (body
hash; `.rdata` string windows), whole-`.text` rel32 xref scan, and
name-table resolution. No `FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Contract (byte-exact)

Body `0x0046cdf0`–`0x0046d03a` inclusive through the final
`c2 04 00`, **587 bytes**, SHA-256
`a73e7a3a800a66bafcb77882efb2350cb0a7f0e6db94b69f3d316db40fd86fdc`.
22 direct `E8`, zero decoded `E9`. MSVC SEH frame
(`push -1; push 0x5d2922; fs:[0]`). `(int level)` at `[esp+0x1c]`;
returns nonzero on success via `ret 4`. Boundary: five `nop`
(`0x0046d03b`–`0x0046d03f`) then `CGame__PostLoadProcess`.

Sequence:

1. `CConsole__Printf("Game::LoadLevel %d", level)` (`.rdata
   0x0062bfd0`; format buffer `0x0066eb90`). Then six size probes —
   `CConsole__Printf("Size of tree = %d", 0x4c)`,
   `"Size of thing = %d"` (0x3c), `"Size of complex thing = %d"`
   (0x7c), `"Size of CST thing = %d"` (0x24),
   `"Size of CST Persistent thing = %d"` (0x38) — compile-time class
   sizes printed at every load (strings at `.rdata 0x0062bfbc` down to
   `0x0062bf50`).
2. `[edi+0x30] = level` (`edi` = `this`); `[edi+0x110] = 0x3f000000`
   (1.0f); `[edi+0xf4] = 0`; word `[0x0083da30] = 0`.
3. World load: `CWorld__LoadWorldFile(level)` with `ecx = 0x00855090`
   (`0x0050b520`). Zero return → failure tail (`eax` stays 0 path,
   `"G::LL succeeded"` is skipped). On success:
   `CWorld__IsMultiplayerMode()` (`0x0050d7d0`) on the same singleton;
   `[edi+0x29c] = 2` when multiplayer else `1` — **the player count**.
4. Player loop (`esi = 0 .. [edi+0x29c)-1`):
   `CDXMemoryManager__Alloc(0x50, "C:\\dev\\ONSLAUGHT2\\game.cpp",
   0x353)` (`0x005490e0`); on success
   `CPlayer__ctor(player, esi+1)` (`0x004d2780`);
   `[edi + esi*4 + 0x2a4] = player_or_0`. Port selection:
   `CFrontEnd__GetPlayer0ControllerPort` (`0x00466980`); for non-first
   players it re-reads the port plus `CFEPOptions__GetState`
   (`0x0051f370`) and inverts the port bit when they match.
   Second alloc: `CDXMemoryManager__Alloc(0x178, …, 0x366)` then
   `CController__ctor(controller, port_from_[0x662ad4 + esi*4],
   player, controller_table_entry)` (`0x005145f0`); result stored at
   `[edi + esi*4 + 0x2b4]`. The port table sits in `.data` at
   `0x00662ad4` (four dwords; this wake did not resolve what its bytes
   point at — recorded unknown).
5. Tail: first player pointer `[edi+0x2a4]` copied to global
   `0x0066e854`; `CDXTrees__BuildTreeGeometry` with
   `ecx = 0x009cc148` (`0x0055a420`);
   `CConsole__RenderLoadingScreen(1, 0)`; engine track slot
   `CDXEngine__SetTrackSlotByFlag(0xff, 1)` with `ecx = 0x0089c9a0`
   (`0x0053f010`); `Input__ResetKeyStateTables` on `0x0088a0a8`
   (`0x005159b0`); `CConsole__Printf("G::LL succeeded")` (`.rdata
   0x0062bf40`); return 1.

Field map pinned by this body:

| Location | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x30]` | current level number | `0x0046ce24` |
| `[this+0x29c]` | player count (1 single / 2 multiplayer) | `0x0046cec4`, `0x0046ced0` |
| `[this+0x2a4 + i*4]` | per-player `CPlayer*` (0x50 bytes each) | `0x0046cf2d` |
| `[this+0x2b4 + i*4]` | per-player `CController*` (0x178 bytes each) | `0x0046cfb4` |
| `0x00855090` | global `CWorld` (load + multiplayer query) | `0x0046cea2`, `0x0046ceb6` |
| `0x9c3df0` | global `CDXMemoryManager` | `0x0046cefe`, `0x0046cf7e` |

## Callers

Whole-`.text` rel32 scan: **one** inbound `E8` — `0x0046dc74` in
`CGame__RestartLoopRunLevel`, immediately after the first-time-round
loading-range setup (see
[`CGame__RestartLoopRunLevel.md`](CGame__RestartLoopRunLevel.md)). Zero
`E9`.

## Pinned-source status

`references/Onslaught/game.cpp:685` is the source twin ("loads world
file/data, creates per-player camera/controller/player chain"). The
bytes agree and add: the two exact allocation sizes and their
`game.cpp` line anchors (851 / 870), the multiplayer→player-count law
(`[+0x29c]`), the `[+0x110] = 1.0f` reset, and the six size-probe log
lines. Divergence from the older note ("prepares geometry/tree build
and load-screen state"): confirmed, with the tree build now pinned to
`0x009cc148` as owner.

## Rebuild mapping

Owner **partially exists**: `rebuild/OnslaughtRebuild.Core/RetailWorldCatalog.cs`
owns world admission (level → world identity), and Level100 mission
program owns the attempt loop. What has no Core owner yet is the
per-attempt spawn law: exactly one `CPlayer` + one `CController` per
player-count slot, allocated fresh each attempt (the restart loop calls
`LoadLevel` again), with counts driven by the loaded world's
multiplayer verdict. When that owner lands, map
`[+0x29c]/[+0x2a4]/[+0x2b4]` onto it; implementing player creation
outside a world-load would be false to the shipped game. Focused test
deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x0046cdf0`–`0x0046d03a` is not
  `a73e7a3a…86fdc`, or the body does not end `33 c0 … c2 04 00` with
  the success path returning 1 (`mov eax, 1` at `0x0046d021`).
- The alloc sizes are anything but `0x50` / `0x178`, or their line
  immediates anything but `0x353` / `0x366`.
- `CWorld__LoadWorldFile` resolves anywhere but `0x0050b520`, or the
  world immediate anywhere but `0x00855090`.
- A second inbound rel32 to `0x0046cdf0` appears.
- `.rdata 0x0062bfd0` stops being `"Game::LoadLevel %d"`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 whole-body
  disassembly (`local-lab/famA/LoadLevel.txt`), raw byte reads (body
  hash; `.rdata` windows `0x0062bfd0`–`0x0062bf40`, `0x0062bba4`),
  whole-`.text` rel32 xref scan (`local-lab/famA_xrefs.py`),
  name-table resolution (`tools/xref_targets.py`: all named targets
  resolved; `0x0046cece/0x0046cf1f/0x0046cf42/0x0046cfb0` are
  compiler-generated alloc-null fallback joins inside this body, not
  missing functions).
- Corroboration (not duplicated):
  [`../cgame-level-lifecycle-semantics-2026-08-11.md`](../cgame-level-lifecycle-semantics-2026-08-11.md)
  bounds this body's demo twin;
  [`IScript__GetVariable.md`](IScript.cpp/IScript__GetVariable.md)
  independently pins `0x00855090` as the `CWorld` singleton.
