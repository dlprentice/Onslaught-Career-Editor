# IScript__SetAllSegmentsHealth

> Address: `0x00535500`

Status: active static function note
Last updated: 2026-08-22
Source File: none — see [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md) for the pinned-source absence behind this whole family | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 52, registered as `SetAllSegmentsHealth`: the
no-name bulk twin of native 51 — same UNIT/controller gate, one float
element evaluated through `vtable[+0x34]`, then the controller call
`0x00444580(value)` stores it into every segment's health cell `+0xc`
in a plain counted loop. Unlike every other writer in this family it
triggers **no** cached-total recompute; consumers read stale `[ctrl+0x18]`
until another family member runs. All authored uses are the level530
hive boss.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads (body hash; image-wide imm32 census;
descriptor-cell walk), whole-`.text` rel32 xref scan, authored `.msl`
recount (`local-lab/famD_measure.py`, `famD_callees.py`, `famD_reg*.py`,
`famD_msl3.py`). Second-pass verification `local-lab/famD_review.py`:
68/68 green. No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 52 is `SetAllSegmentsHealth` / `0x00535500` / empty
name-table cell / 3 authored sites; confirmed this wake (the two extra
textual hits in the tree are commented-out lines — see Callers).
Registration:

- Handler immediate: `mov ebp, 0x00535500` (`bd 00 55 53 00`) at VA
  `0x0053120e` — exactly **one** image-wide imm32 (byte hit at
  `0x0053120f`). Zero rel32 inbound.
- Handler cell store: `mov [0x64db50], ebp` at VA `0x00531218`.
- Name-pointer store: `mov dword ptr [0x64db20], 0x64f770` at VA
  `0x005311ee`; `.rdata 0x64f770` = `"SetAllSegmentsHealth\0"`.
- Descriptor: name cell `0x64db20`, handler cell +0x30 at `0x64db50`.

## Contract (byte-exact)

Body `0x00535500`–`0x0053552d` inclusive through the complete
`ret 0xc`, **46 bytes**, SHA-256
`5674d8cdf6a9629523c5867184b36e5aef137e90b4eb6d3c71eebc03a5db3b5c`.
One `E8`, zero decoded `E9`.

```
00535500  8b 41 10           mov eax, [ecx+0x10]        ; attached thing
00535503  56                 push esi
00535504  f6 40 34 10        test byte [eax+0x34], 0x10 ; UNIT class bit
00535508  74 20              je 0x53552a                ; -> bare return
0053550a  8b b0 78 01 00 00  mov esi, [eax+0x178]       ; segments ctrl
00535510  85 f6              test esi, esi
00535512  74 16              je 0x53552a
00535514  8b 44 24 08        mov eax, [esp+8]           ; args object
00535518  8b 08              mov ecx, [eax]             ; element 1
0053551a  8b 11              mov edx, [ecx]
0053551c  ff 52 34           call [edx+0x34]            ; float eval -> st0
0053551f  51                 push ecx                   ; value slot
00535520  8b ce              mov ecx, esi               ; this = controller
00535522  d9 1c 24           fstp dword ptr [esp]       ; store the float
00535525  e8 56 f0 f0 ff     call 0x00444580            ; (value)
0053552a  5e                 pop esi
0053552b  c2 0c 00           ret 0xc
```

Boundary: one `nop` then `SetStealth` (native 138) at `0x00535530`.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` / `[thing+0x34]&0x10` / `[thing+0x178]` | shared gate law | `0x00535500`–`0x00535512`; full discussion in [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md) |
| `args[0]` via `vtable[+0x34]` | float health value (single arg) | `0x0053551c` |
| `0x64db20` / `0x64db50` | registration descriptor cells | `0x005311ee`, `0x00531218` |

## Controller dispatch — `0x00444580` `(value)` (byte-exact)

`thiscall`, `ret 4`. No gates of its own; the caller's gate is the only
one:

```
00444580  mov edx, [ecx+8]         ; segment count
00444583  xor eax, eax             ; i = 0
00444585  test edx, edx; jle done
00444589  push esi
0044458a  mov edx, [ecx+4]         ; segment array
0044458d  mov edx, [edx+eax*4]     ; segments[i]
00444590  test edx, edx; je skip
00444594  mov esi, [esp+8]         ; arg = float value
00444598  mov [edx+0xc], esi       ; SEGMENT HEALTH CELL
0044459b  mov edx, [ecx+8]; inc eax; cmp eax, edx; jl 0x0044458a
004445a3  pop esi
004445a4  ret 4
```

Writes `[seg+0xc]` for every non-null slot in `[ctrl+4][0..[ctrl+8])`.
**No `[seg+0x10]` write and no recompute call** — the only member of
the five-native family whose dispatch touches neither. Consequence:
after this native alone runs, the cached total `[ctrl+0x18]` and the
`GetHealth`/`GetRealHealth` windows (which sum per-segment cells via
`0x00442890`/`0x00442900` or read the cache — see
[`IScript__ResetSegmentHealth.md`](IScript__ResetSegmentHealth.md))
do not reflect the new health until another family member recomputes.
Authored scripts never rely on that gap: every hive use pairs it with
other family calls in the same tick.

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake
(pristine data tree, active lines only): **3 active sites, all**
`level530/hive.msl` (`support.SetAllSegmentsHealth(1000000.0)` ×2,
`(10.0)` ×1); plus 2 commented-out lines in `level521`/`level522`
`hive.msl` (`// support.SetAllSegmentsHealth(1000000.0);`) which are
not uses. Matches corpus TSV's 3.

## Pinned-source status

Absent, like the rest of the family (see
[`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md)).

## Rebuild mapping

No Core owner yet. When one lands: bulk write of one float into
every segment's health cell, gated identically; the missing-recompute
behavior above is part of the observable contract and should be pinned
by the owner's focused test. Focused test deferred until the owner
exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535500`–`0x0053552d` is not
  `5674d8cd…3b5b5c`, or the dispatch target is anything but
  `0x00444580`.
- A second image-wide imm32 of `0x00535500`, or any rel32 inbound.
- The handler store leaves `0x64db50`, or `.rdata 0x64f770` stops being
  `"SetAllSegmentsHealth\0"`.
- A recompute `E8` appears inside `0x00444580`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famD_measure.py`, `famD_callees.py`, `famD_reg.py`,
  `famD_reg2.py`, `famD_msl3.py`); second pass `local-lab/famD_review.py`
  68/68 green.
- Cross-reference (same wake):
  [`IScript__SetSegmentHealth.md`](IScript__SetSegmentHealth.md),
  [`IScript__ResetSegmentHealth.md`](IScript__ResetSegmentHealth.md),
  [`IScript__SetSegmentVulnerable.md`](IScript__SetSegmentVulnerable.md),
  [`IScript__SetAllSegmentsVulnerable.md`](IScript__SetAllSegmentsVulnerable.md).
