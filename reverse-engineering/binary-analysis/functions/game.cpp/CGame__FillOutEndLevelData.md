# CGame__FillOutEndLevelData

Status: active static function note
Last updated: 2026-08-19
Summary: FillOut's score-time arm skips unless CWorld__LoadWorld stored
(percentage − full) > 0; kills copy player+8; training still unlocks
goodies 0/8/78/121/164. L100 Size, kill totals, and authored time bytes
stay unclaimed.
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

`Size` after a first-play Level 100 Won is **not** measured here. Authored
BSWD has 35 unit records (materializer: 33 visible + 2 type-37 markers).
That is not a runtime `[0x0085515c]` reading.

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
`player+8` to `0x00672e30`. Else store five zeros. That is the inlined
`GetNumEnemyThingKilled` readout. The five values after a first-play
Level 100 Won are gameplay and are **not** measured here.
`CCareer__UpdateThingsKilled` (`0x0041c180`) still does `cmp [0x00672e18], 0x64`
/ `je` return, so world 100 never adds them to career totals.

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
`[esp+0x18]` in `{45,46,47}` reads three extra dwords first; Level 100
is version 50, so those extras are skipped (`cmp ax, 0x2d` / `0x30`).
Which BSWD/RLWD bytes become the two times is **not** claimed — last
`LoadWorld` wins. Until that map exists, do not invent a skip of this
arm for Level 100.

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
`0x0001c188` is not `83 f8 64`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0046d470` | `CGame__FillOutEndLevelData` | `a15c518500 81ec10010000 3d20010000 … d9850c010000 d8a508010000 … c3` | thiscall; bare `ret`; 920 B. HIGH on ABI, base-things 1/0 law, kill copy from `player+8`, pre-arm `1.0f`, score-time `fcomp` skip, LoadWorld-only BSS writers. **Not** on L100 `Size`, L100 kill totals, or authored time bytes. |
