# CGame__PostLoadProcess

> Address: `0x0046d040`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/game.cpp:764`
(`CGame::PostLoadProcess`) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Per-attempt world validation and player start assignment, run
once after `LoadLevel`. Resets atmospherics, walks the player list and
either binds an existing start-position thing to each player or logs
`"No start position for player - creating a default one"` and mints a
default via `OID__CreateObject(0xf, 0)` + `CInitThing__ctor`, then
initializes each player, sets `[this+0x290]/[+0x294] = 2`, optionally
arms demo record/playback from two global bytes, sorts map membership,
builds the height-field min/max table, and returns success. This is
where the released binary decides where the player actually starts.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
above, verified before reading) with capstone 5.0.7 whole-body
disassembly (`local-lab/famA/PostLoadProcess.txt`), raw byte reads
(body hash; `.rdata` string window), whole-`.text` rel32 xref scan,
and name-table resolution. No `FUN_*` milled; no Core owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Contract (byte-exact)

Body `0x0046d040`–`0x0046d264` inclusive through the final `c3`,
**549 bytes**, SHA-256
`0903b78f65a5e2807e9bee27ad83555063cc2dd62cbe49419193dae0d2ed1895`.
20 direct `E8`, zero decoded `E9`. Frame reserves 0x3dc bytes;
`ebp = this`; returns nonzero on success. Boundary: eleven `nop`
(`0x0046d265`–`0x0046d26f`) then `CStartInitThing__VFunc_0_0046d270`.
The current name table ends this function at `0x0046d264` — the older
note's `0x0046dc2f` boundary was stale and is corrected by this note.

Sequence:

1. `CHud__PostLoadProcess` on `0x008aa4e8` (`0x00481af0`). Zero →
   immediate failure return.
2. `SetLoadingFraction(0.2f)`;
   `Atmospherics__Init` (`0x00404a00`);
   `Atmospherics__ResetAndUpdate` (`0x00404b90`);
   `SetLoadingFraction(0.4f)`.
3. Player loop (`edi = [ebp+0x2a4]`, count `[ebp+0x29c]`):
   - Walks the global start-position list head at `0x00855100`
     (next-pointer cell `0x00855108`). For each candidate, when its
     `[eax+0x80]` matches the player's `[ecx+0x2c]`:
     `CPlayer__AssignBattleEngine(player, [eax+0x7c])` (`0x004d3080`)
     — **start-position binding is the battle-engine assignment** —
     and stops walking.
   - Exhausted with no match: `CConsole__Printf` (buffer `0x0066f580`)
     with `.rdata 0x0062c008` =
     `"No start position for player - creating a default one"`, then
     `OID__CreateObject(type=0xf, flags=0)` (`0x004bf090`) and, on a
     non-null result, `CInitThing__ctor` placement at `[esp+0x24]`
     (`0x0048dcf0`) with position fields built as floats
     `(0x43800000, 0x43800000, 0)` = (256.0, 256.0, 0), pushed to the
     object's virtual `[edx+0x24]` along with `[edx+0x2c]`, then
     `CPlayer__AssignBattleEngine(player, [esi+0x7c])`.
   - Every iteration ends with `CPlayer__Init(player)` (`0x004d28a0`).
4. After the loop: `SetLoadingFraction(0.6f)`;
   `[ebp+0x290] = 2`; `[ebp+0x294] = 2`.
5. Demo hooks: byte `0x00662f36` set → `CController__StartPlayback(
   controller=[ebp+0x2b4], 0x00662f4c)`; byte `0x00662f34` set →
   `CController__StartRecording(controller, 0x00662f4c)`
   (`0x0042d8c0` / `0x0042d8a0`). Both read the same argument cell.
6. `SetLoadingFraction(0.8f)`; `CMapWho__Sort` on `0x00704200`
   (`0x4926e0`); `CHeightField__BuildCellMinMaxHeightTable` on
   `0x006fadc8` (`0x00490e30`); `SetLoadingFraction(1.0f)`; return 1.

Field map pinned by this body:

| Location | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x29c]` | player count (same cell `LoadLevel` writes) | `0x0046d08b` |
| `[this+0x2a4 + i*4]` | per-player `CPlayer*` array | `0x0046d0a3` |
| `[this+0x290] / [+0x294]` | attempt-state pair forced to 2 | `0x0046d1e8`, `0x0046d1ee` |
| `[this+0x2b4]` | first controller (demo hooks) | `0x0046d1fd`, `0x0046d216` |
| `0x00855100 / 0x00855108` | start-position list head/next | `0x0046d0a9`, `0x0046d0b4` |
| `0x008aa4e8` | global `CHud` | `0x0046d049` |
| `0x00662f34 / 0x00662f36` | demo record/playback request bytes | `0x0046d1f4`, `0x0046d20d` |
| `0x00704200 / 0x006fadc8` | global `CMapWho` / height-field owner | `0x0046d235`, `0x0046d23f` |

## Callers

Whole-`.text` rel32 scan: **one** inbound `E8` — `0x0046dcf2` in
`CGame__RestartLoopRunLevel`, directly after `LoadLevel` success and a
loading-range update. Zero `E9`.

## Pinned-source status

`references/Onslaught/game.cpp:764` is the source twin ("post-load
world validation and player/start setup … returns non-zero on
success"). The bytes agree and add: the exact start-position match rule
(`[thing+0x80] == [player+0x2c]`, engine handle from `[thing+0x7c]`),
the default-start fallback constants (type 15, position 256.0/256.0/0),
the `[+0x290]/[+0x294] = 2` state pair, and the demo-hook globals. The
older note's claim "resolves/assigns player start positions" is
confirmed and now pinned to specific offsets; its "finalizes post-load
world sorting/setup stages" maps to `CMapWho__Sort` +
`CHeightField__BuildCellMinMaxHeightTable`.

## Rebuild mapping

Owner candidates exist but none owns this contract:
`rebuild/OnslaughtRebuild.Core/RetailWorldCatalog.cs` owns admission,
and the Level100 program owns the mission loop; neither assigns start
positions. When a spawn-placement owner lands, it must encode: match
rule against a world-owned start list, default fallback at (256, 256)
with type 15, per-player `Init` after assignment, and the state pair
write. Focused test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x0046d040`–`0x0046d264` is not
  `0903b78f…d1895`, or the body does not end `b8 01 00 00 00 5d 81 c4 dc 03 00 00 c3`.
- The default-start type is anything but `push 0xf` before
  `OID__CreateObject`, or the fallback coordinates anything but
  `0x43800000` twice with zero z.
- The start-list head is anywhere but `0x00855100`, or the match field
  offsets anything but `+0x80` vs `+0x2c`.
- A second inbound rel32 to `0x0046d040` appears.
- The function's saved end moves off `0x0046d264` in the tracked name
  table.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: capstone 5.0.7 whole-body
  disassembly (`local-lab/famA/PostLoadProcess.txt`), raw byte reads
  (body hash; `.rdata 0x0062c008` window), whole-`.text` rel32 xref
  scan (`local-lab/famA_xrefs.py`), name-table resolution
  (`tools/xref_targets.py`; the four intra-body targets the older raw
  scan flagged — `0x0046d0be/0x0046d0f6` — are compiler joins inside
  this body).
- Corroboration (not duplicated):
  [`../../cgame-level-lifecycle-semantics-2026-08-11.md`](../../cgame-level-lifecycle-semantics-2026-08-11.md)
  bounds the demo twin of this body;
  [`CGame__LoadLevel.md`](CGame__LoadLevel.md) pins the player-count
  and player/controller arrays this loop consumes.
