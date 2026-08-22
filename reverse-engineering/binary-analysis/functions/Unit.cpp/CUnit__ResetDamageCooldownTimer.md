# CUnit__ResetDamageCooldownTimer

> Address: `0x004e6660`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `Unit.cpp` has no source body in `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the 21-byte damage-cooldown writer — stores global time plus a
5.0 s horizon into `[unit+0x88]`. Sole inbound caller is the cooldown-reset
gate inside `CUnit__ApplyDamage`.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
verified before reading) with capstone disassembly, raw byte reads (body
hash; float constants), whole-.text rel32 scan, and image-wide imm32
census (`local-lab/unitdmg/measure.py`, `cooldown_xref.py`). No `FUN_*`
milled; no Core owner changed.

> Address: `0x004e6660`

## Contract (byte-exact)

Body `0x004e6660`–`0x004e6674` inclusive through the complete
`ret 4`, **21 bytes**, SHA-256
`2f0568d877c62bd654adaef35fe8954ca23f24f286642dcf56aa6492c1c79b8`.
Zero `E8`, zero `E9`.

```
004e6660  d9 05 d0 2f 67 00   fld dword ptr [0x672fd0]   ; global time snapshot
004e6666  d8 05 d8 85 5d 00   fadd dword ptr [0x5d85d8]  ; + 5.0f
004e666c  d9 99 88 00 00 00   fstp dword ptr [ecx+0x88]  ; unit cooldown cell
004e6672  c2 04 00            ret 4
```

`thiscall`; one stack arg (unused by the body — the caller pushes the
source pointer but this callee never reads it). `[0x005d85d8]` is
`00 00 a0 40` = `5.0f`. `[0x00672fd0]` is the same global time snapshot
the IScript weather natives and `CEventManager` timing read.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x88]` | damage-cooldown expiry time | store `0x004e666c` |
| `[0x00672fd0]` | global time float snapshot | load `0x004e6660` |
| `0x005d85d8` | constant 5.0f | `fadd` operand |

## Consumers

Exactly **one** inbound rel32 image-wide: the reset gate at
[`CUnit__ApplyDamage`](CUnit__ApplyDamage.md) `0x004f9add`, which calls it
only when `[unit+0x148]` is live, source flags bit 2 is clear, and
`[src+0xec]+0x34` bit 4 is set. Zero imm32 sites. The reader of
`[unit+0x88]` remains an honest unknown. The proposed focused instrument
was run in the 2026-08-22 continuation: a whole-function capstone census
for an x87 `[reg+0x88]` operand in a body that also references global time
`0x00672fd0` returned zero candidates. That negative heuristic is not an
exhaustive proof of no reader. The `+0x88` load inside
`CUnitAI__CanUseIndexedSegmentEntry 0x00444f20` is separately disproved as
the cooldown: it supplies an integer alias index immediately consumed by
the controller segment array.

## Pinned-source status

Absent. No `Unit.cpp` in the drop.

## Rebuild mapping

No Core owner; nothing in the rebuild models per-unit damage cooldowns.
Focused test deferred until one exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x004e6660`–`0x004e6674` is not
  `2f0568d8…c79b8`, or the final instruction is anything but
  `c2 04 00` at `0x004e6672`.
- A second rel32 inbound or any imm32 of `0x004e6660` appears.
- `0x005d85d8` stops being `00 00 a0 40`.

## Receipts

- 2026-08-22 — pristine specimen
  (`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, main tree),
  SHA-256 verified before reading. Tools:
  `local-lab/unitdmg/measure.py` (disassembly + hash),
  `local-lab/unitdmg/cooldown_xref.py` (rel32 + imm32 census),
  `local-lab/unitdmg/consts.py` (constant resolution).
