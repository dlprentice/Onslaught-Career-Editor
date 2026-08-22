# CGame__Init

> Address: `0x0046c360`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/game.cpp:246` (`CGame::Init`) |
Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: One-off level-system initialization, run once per
`RunLevel`. The released body is a short guarded chain: tweak reset →
console built-ins → height-field init (early-exit gate) → engine init
(early-exit gate) → imposter globals → render-queue console var →
static shadows → interface menu state → HUD init → two gameplay
debug CVars (`cg_showmemdeltas`, `cg_showdatasizes`) → success. Both
failure exits return zero and abort the level run before any restart
state exists.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly (`local-lab/famA/Init.txt`), raw byte reads (body hash;
`.rdata` string windows), whole-`.text` rel32 xref scan, and
name-table resolution. No `FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Contract (byte-exact)

Body `0x0046c360`–`0x0046c42f` inclusive through the final `c3`,
**208 bytes**, SHA-256
`0c4121bf33e06ed038278c6db7fd1b3ed9783399e0d75f146514afdb9bbca7f8`.
12 direct `E8`, zero decoded `E9`. `this` in `ecx` (`esi`); returns
int (nonzero success). Boundary: no pad — `CGame__InitRestartLoop`
starts immediately at `0x0046c430`.

Sequence:

1. `[esi+0x2a0] = -1` (level slot invalidated; `RunLevel` overwrites
   it with the requested level); `[esi+0x24] = 0`.
2. `CTweakFLOAT__SetNumViewpoints(0)` on `0x0089c9a0` (`0x00528b50`).
3. `CConsole__RegisterBuiltinCommands` on `0x00663498`
   (`0x00429ef0`).
4. `CHeightField__InitAndClearMapLoadFlags` on `0x006fadc8`
   (`0x00490f10`). Zero → return 0.
5. `CDXEngine__Init` on `0x0089c9a0` (`0x0053d5f0`). Zero → return 0.
6. `CDXImposter__InitGlobals` (`0x005428d0`).
7. `CDXEngine__InitConsoleVar_UseRenderQueue` on `0x009c7490`
   (`0x005515a0`) — registered twice across the family (also from
   `InitRestartLoop`).
8. `CStaticShadows__Initialise` on `0x009c8010` (`0x004ebbc0`).
9. `CGameInterface__ResetMenuState` on `0x00679fa8` (`0x004729e0`).
10. `CHud__Init` on `0x008aa4e8` (`0x00481450`).
11. Two CVars via `CConsole__RegisterVariable` (`0x0042b040`), each
    `(name, help, type=3, &this-cell, 0)`:
    - `"cg_showmemdeltas"` / `"Should memory deltas be shown?"`
      (`.rdata 0x0062bc6c` / `0x0062bc80`, cell `[esi+0x9f4]`)
    - `"cg_showdatasizes"` / `"Should level data sizes be shown?"`
      (`.rdata 0x0062bc34` / `0x0062bc48`, cell `[esi+0x9f0]`)
12. `[esi+0x3b4] = 0`; return 1.

Field map pinned by this body:

| Location | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x2a0]` | level cell pre-invalidated to −1 | `0x0046c36a` |
| `[this+0x24]` | quit marker cleared | `0x0046c37e` |
| `[this+0x9f0] / [+0x9f4]` | the two debug-CVar cells | `0x0046c400`, `0x0046c3df` |
| `[this+0x3b4]` | counter cleared at init end | `0x0046c41f` |
| `0x0089c9a0` | global `CDXEngine` (init + tweak target) | `0x0046c365`, `0x0046c39a` |
| `0x00663498` | global `CConsole` | `0x0046c379` et al. |

The `.rdata window` after `"Should memory deltas be shown?"` continues
with `"g_framelength"` — the first of the frame-length CVars that
`InitRestartLoop` registers, matching the older note's claim.

## Callers

Whole-`.text` rel32 scan: **one** inbound `E8` — `0x0046e2a1` in
`CGame__RunLevel`'s one-off setup block (see
[`CGame__RunLevel.md`](CGame__RunLevel.md)). Zero `E9`.

## Pinned-source status

`references/Onslaught/game.cpp:246` is the source twin ("console
defaults, map, engine, imposters, render queue, static shadows, game
interface, and HUD … failure of map, engine, or imposter
initialization returns false"). Byte mapping against that list:
height-field = "map" gate, engine = engine gate — but the imposter
call's return is **not** tested in the released body
(`CDXImposter__InitGlobals` result unchecked); only the height-field
and engine gates early-exit. This refines the lifecycle note's failure
claim: two measured gates, not three. The two `cg_show*` CVars are
released-only detail the source twin does not name.

## Rebuild mapping

No Core owner models one-off level-system init ordering. When one
lands: height-field and engine are the two hard gates; imposter
globals and static shadows are unconditional; the two CVar cells live
on the CGame object at `+0x9f0/+0x9f4`. Focused test deferred until
that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x0046c360`–`0x0046c42f` is not
  `0c4121bf…ca7f8`, or the body does not end `b8 01 00 00 00 5e c3`.
- A third early-exit gate appears (the released body tests exactly two:
  height-field, engine).
- `.rdata 0x0062bc34` stops being `"cg_showdatasizes"`.
- A second inbound rel32 to `0x0046c360` appears.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 whole-body
  disassembly (`local-lab/famA/Init.txt`), raw byte reads (body hash;
  `.rdata` windows `0x0062bc34/48/6c/80`), whole-`.text` rel32 xref
  scan (`local-lab/famA_xrefs.py`), name-table resolution
  (`tools/xref_targets.py`; all ten call targets resolved to named
  functions).
- Corroboration (not duplicated):
  [`../../cgame-level-lifecycle-semantics-2026-08-11.md`](../../cgame-level-lifecycle-semantics-2026-08-11.md)
  (`NORMALIZED_IDENTICAL` demo twin);
  [`CGame__RunLevel.md`](CGame__RunLevel.md) pins the caller context.
