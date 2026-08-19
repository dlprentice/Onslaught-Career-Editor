# CGame__FillOutEndLevelData

Status: active static function note
Last updated: 2026-08-19
Summary: FillOut's score-time arm is live on L100: last LoadWorld
stores RLWD `300.0f` / `500.0f` so `(pct − full)=200>0`. Base-things
`Size` is 35 (At() membership, including two type-37 `CSafeSide`).
Training still unlocks goodies 0/8/78/121/164. Kill readout is
ctor-zero plus ConfirmedKill increments, not an authored L100
constant.
Source File: `references/Onslaught/game.cpp:910` | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from the official
safe-copy specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (twin of
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`).
The Ghidra database was not opened. Source names below are labels for
already-identified `CGame` / `END_LEVEL_DATA` slots.

> Address: `0x0046d470`

## Contract

Zero-arg `thiscall`. `ECX` → `EBP`. Bare `ret` at `0x0046d807`. Body
`0x0046d470`–`0x0046d807` is 920 bytes, SHA-256
`2cd8ee2693c5b5064e085d8893eadee34039eeadfa5e00d12fe7f4b6a54f8fd2`.
`CGame` singleton `this` is `0x008a9a98` (149 image `mov ecx, 0x008a9a98`;
`IScript__AddScore` `0x005343cb` is `add [0x008a9b8c], eax` =
`this+0xf4`). `END_LEVEL_DATA` is `0x006728f8`.

### Base-things walk

`[0x0085515c]` is the list `Size`. `cmp eax, 0x120` (288). `jg` logs
`0x0062c048` and skips the walk. Else `ebx=0`; while `ebx < Size` call
`CSPtrSet__At` (`0x004e5c90`, `ecx=0x00855150`, arg=`ebx`). Store at
`0x006728f8 + ebx*4`: `1` if `[thing] != 0` and `([thing+0x2c] & 4) == 0`,
else `0`. `operand_scan` of `0x0085515c` is those two FillOut reads only —
`Size` is not an image immediate.

Unwritten slots `Size..287` are not touched. They stay whatever
`END_LEVEL_DATA` already held (BSS 0 on a cold process).
`CCareerNode::SetBaseThingExistTo` (`0x0041b770`) treats only literal `1`
as set, so a leftover `0` **clears** that bit on the destination node.
`level_structure[0][3] = 110` is the destination after a world-100
primary; this body does not itself walk the career graph.

`Size` after a first-play Level 100 Won is **35**. That is
`CSPtrSet` `+0xc` on WORLD+`0xc0` (`0x00855150`). Only the is-base
`LoadWorld` `AddToTail` arms at `0x0050d00f` / `0x0050d05b` grow it.
L100 BSWD payload (AYA `100_res_PC.aya` WRES/WRLD/BSWD, inflated SHA-256
`115ede05…2df4`, tag at inflated `3595001`, payload `3595009`) is
`uint16` version 50 then, at payload `+60`, `int32 1` / `int32 0` /
`uint16 35`. Type 37 is created (`0x004bf745` `push 0x45` /
`push 0x00630c20`) and names `.?AVCSafeSide` at `0x00630b48` /
`CSafeSide` at `0x00630c98`. Do not drop those two slots. Do not adopt
materializer 33.

First-play script does not kill a list member. FillOut therefore stores
`1` at `0x006728f8+i*4` for `i=0..34` and leaves `35..287` untouched (0
on a cold BSS). A player who destroys a type-35 iceberg *and still Wins*
would flip those indices; that is not the first-play script contract and
is not claimed. No TTD dword at FillOut was read.

### Scalars, objectives, slots, kills

| dest | source |
| --- | --- |
| `0x00672e18` | `[this+0x30]` current level |
| `0x00672e1c` | `[this+0x28]` game state |
| `0x00672d78` | ten stride-8 primaries from `this+0x4c` |
| `0x00672dc8` | ten stride-8 secondaries from `this+0x9c` |
| `0x00672e20` | `0x3f800000` (`1.0f`) **before** the score-time arm |
| `0x00672e28` | `[0x00672fd0]` event-manager time |
| `0x00672e24` | `[this+0xf4]` score |
| `0x00672e2c` | `[this+0x114]` lost-reason |
| `0x00672e44` | 32 dwords from `this+0x308` (`cmp eax, 0x80`) |

If `[this+0x2a4]` (player 0) is live: copy **five** dwords from
`player+8` to `0x00672e30` (`0x0046d60f`). Else store five zeros.
`CPlayer__ctor` `0x004d2780` writes those five dwords to 0
(`89 46 08` … `89 46 18` at `0x004d27de`–`0x004d27eb`, EAX=0).
The only image incrementer is `0x004d30d0` (table name
`CInfluenceMap__AccumulateThingFlags`; one inbound `E8` at
`0x0040a578` inside `CBattleEngine__VFunc_101_0040a560`):
`inc [player+8/+c/+10/+14/+18]` gated on `[thing+0x34]` bits
`0x400` / `0x20000` / `0x40000` / `0x4000` / `0x800`, and only
when `[thing+0x138]==1`. That is not an authored L100 constant.
A first-play Won does not require a ConfirmedKill, so the snapshot
is **0,0,0,0,0 unless the player actually scored those bits**.
`CCareer__UpdateThingsKilled` (`0x0041c180`) still does
`cmp [0x00672e18], 0x64` / `je` return, so world 100 never adds
them to career totals. No TTD dword was read.

### Score-time arm

```
fld  [this+0x10c]          ; 0x008a9ba4
fsub [this+0x108]          ; 0x008a9ba0
fst  [esp+0x10]
fcomp [0x005d856c]         ; 0.0f
test ah, 0x41
jne  0x0046d79b            ; skip if (percentage - full) <= 0
```

Live path (source `game.cpp:988-1026`): compare event time to the two
floats; scale `[this+0xf4]` by that multiplier (clamped to `[0,1]` via
`0x005d8568` / `0x005d856c`); then rewrite `0x00672e20` from the scaled
score vs `[this+0xf8]` / `[this+0xfc]` (S/D grade ints). Borderline
`0.0` ranking is replaced with `0x3a83126f` (`0.001f`).

`CGame__LoadLevel` (`0x0046cdf0`) writes `[this+0x110] = 0x3f000000`
(`0.5f`) and `[this+0xf4] = 0`. It does **not** write `+0x108` / `+0x10c`.
`CGame__ctor` (`0x0046c210`) does not write them either.

The only image `fstp` of those two BSS dwords is inside
`CWorld__LoadWorld` (`0x0050b9c0`–`0x0050d4b1`):

| VA | store |
| --- | --- |
| `0x0050d2cf` | `fstp [0x008a9b9c]` `this+0x104` time-limit |
| `0x0050d2e0` | `fstp [0x008a9ba0]` `this+0x108` full-score time |
| `0x0050d2ed` | `fstp [0x008a9ba4]` `this+0x10c` percentage-score time |
| `0x0050d301` | `fstp [0x008a9ba8]` `this+0x110` score percentage |

Each float was just `CDXMemBuffer__Read` (`0x00548570`, 4 bytes) into
`[esp+0x7c]` / `[esp+0x84]` / `[esp+0x8c]` / `[esp+0x68]`. Version
`[esp+0x18]` in `{45,46,47}` reads five extra dwords first; Level 100
is version 50, so those extras are skipped (`cmp ax, 0x2d` / `0x30` at
`0x0050d242`).

Last `LoadWorld` on a Level 100 start is the outer / level parse
(`LoadLevel` → `LoadWorldFile(level_id, is_base=0)`), stream
WRES/WRLD/RLWD (tag at inflated `3649678`, payload `3649686`, version
50). Dwords 8 and 9 of the 11-dword post-waypoint block are payload
`+0x147ba` / `+0x147be` = `0x43960000` / `0x43fa0000` (`300.0f` /
`500.0f`). `(500 − 300) = 200 > 0`, so FillOut's `test ah,0x41` /
`jne` skip does **not** fire. BSWD same slots are
`0x0068457d` / `0x0012ef72` and lose to the later RLWD `fstp`s.
Authored names for the other nine tail dwords are **not** claimed.

Independent re-read 2026-08-19 after `t_01b77abf` / `t_4302bd82`.
Specimen + twin `74154bfa…7750`. Inflated L100 AYA SHA-256
`115ede05…2df4`. No Ghidra.

### Secondary ranking clamp

After the arm (or its skip), count nonzero first-dwords over the ten
secondaries still addressed by `ESI` (`this+0x9c`). Zero → skip.
Nonzero → `CEndLevelData__IsAllSecondaryObjectivesComplete`
(`0x004496e0`) on `0x006728f8`. All-complete and ranking `< 0.4`
(`0x005d8c40`) stores `0x3ecccccd`. Else ranking `> 0.6`
(`0x005d8bb8`) stores `0x3f19999a`. Level 100's authored secondary
count is already pinned at 0, so this clamp does not run there.

Cheapest falsifier: file `0x0006d470` is not `a1 5c 51 85 00`, **or**
`0x0006d807` is not `c3`, **or** `0x0006d638` is not
`d9 85 0c 01 00 00`, **or** `0x0006d63e` is not `d8 a5 08 01 00 00`,
**or** `operand_scan` of `0x008a9ba0` / `0x008a9ba4` is not exactly one
`fstp` each at `0x0050d2e0` / `0x0050d2ed`, **or**
`0x0001c188` is not `83 f8 64`, **or** `0x0010d2e0` is not
`d9 1d a0 9b 8a 00`, **or** `0x0010d2ed` is not `d9 1d a4 9b 8a 00`,
**or** L100 RLWD payload `+0x147ba` is not `00 00 96 43`, **or**
`+0x147be` is not `00 00 fa 43`, **or** BSWD payload `+62` is not
`uint16 35`, **or** `0x0010d00f` is not
`8d 8a c0 00 00 00 e8 06 8b fd ff`, **or** `0x000d27de` is not
`89 46 08`, **or** `0x000d30dc` is not `ff 41 08`, **or**
`tools/call_xref_scan.py` on `0x004d30d0` is not exactly `E8` at
`0x0040a578`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0046d470` | `CGame__FillOutEndLevelData` | `a15c518500 81ec10010000 3d20010000 … d9850c010000 d8a508010000 … c3` | thiscall; bare `ret`; 920 B. HIGH on ABI, L100 `Size=35`, RLWD `300/500` live score-time arm, kill copy from `player+8`. **Not** on an authored five-kill vector, iceberg-destroy store-0, or names for the other nine tail dwords. |
