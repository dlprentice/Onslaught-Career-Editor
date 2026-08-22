# IScript__HighlightHudPart

> Address: `0x00535E60`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `HighlightHudPart` is absent from `references/Onslaught/`; the script-side constants live in the shipped `data/MissionScripts/onsldef.msl` (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 34, registered as `HighlightHudPart`: a 25-byte
twin — evaluates one integer argument (the HUD-part index, authored via
the `HUD_*` constants of `onsldef.msl`), then writes state value **2**
into the global per-HUD-part state array at `0x008aa51c`. Its twin
[`IScript__UnHighlightHudPart.md`](IScript__UnHighlightHudPart.md)
writes 1. No thing is touched; no gate.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor-cell
walk, whole-`.text` rel32 xref scan, array-reference census, authored
`.msl` recount (`local-lab/famF_hud.py`, `famF_hud2.py`,
`famF_hud3.py`). No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 34 is `HighlightHudPart` / `0x00535E60` / empty
name-table cell / 13 authored sites; confirmed this wake. Registration:

- Handler immediate: `mov edi, 0x00535e60` (`bf 60 5e 53 00`) at VA
  `0x00530b42` — exactly **one** image-wide imm32 (byte hit at
  `0x00530b43`). Zero rel32 inbound.
- Handler cell store: `mov [0x64d6d0], edi` at VA `0x00530b4c`.
- Name-pointer store: `mov dword ptr [0x64d6a0], 0x64f89c` at VA
  `0x00530bb9`; `.rdata 0x64f89c` = `"HighlightHudPart\0"`.
- Descriptor: name cell `0x64d6a0`, handler cell +0x30 at `0x64d6d0`.

## Contract (byte-exact)

Body `0x00535e60`–`0x00535e78` inclusive through the complete
`ret 0xc`, **25 bytes**, SHA-256
`d2a93e3bebd2d503307b5f1e3433926730059a7c413993ea8efbbdc0e479fc39`.
Zero `E8`, zero decoded `E9`.

```
00535e60  8b 44 24 04        mov eax, [esp+4]           ; args object
00535e64  8b 08              mov ecx, [eax]             ; element 1
00535e66  8b 11              mov edx, [ecx]
00535e68  ff 52 30           call [edx+0x30]            ; INT eval -> eax
00535e6b  c7 04 85 1c a5 8a 00
          02 00 00 00        mov dword [eax*4 + 0x8aa51c], 2   ; HIGHLIGHT
00535e76  c2 0c 00           ret 0xc
```

The evaluator here is `vtable[+0x30]` — the integer-return slot shared
with AddScore's arg handling ([`IScript.cpp.md`](../IScript.cpp.md)
Functions table), distinct from the `[+0x3c]` slot the
SetVisible/vulnerability natives use.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `args[0]` via `vtable[+0x30]` | integer HUD-part index | `0x00535e68` |
| `0x008aa51c + index*4` | global per-HUD-part state cell | `0x00535e6b` |
| state `2` | highlighted (this native) | `0x00535e73` |
| `0x64d6a0` / `0x64d6d0` | registration descriptor cells | `0x00530bb9`, `0x00530b4c` |

Authored indices come from `data/MissionScripts/onsldef.msl`:
`HUD_HEALTH_BAR=0, HUD_ENERGY_BAR=1, HUD_COMPASS=2,
HUD_BATTLE_LINE_MAP=3, HUD_RADAR=4, HUD_CURRENT_WEAPON=5` — so the
array has at least six live dwords.

## Consumers

Whole-`.text` literal-reference census for the base `0x008aa51c`: exactly
**two** hits — the two natives' stores. The HUD consumer reaches these
cells through a containing object (base-plus-offset addressing), not a
literal; its identity is an honest unknown and the cheapest instrument
is an operand scan for `0x8aa51c`-derived addresses (e.g. `0x8aa520…`)
or a data-xref walk from the array in Ghidra. State semantics beyond
{1 = normal, 2 = highlighted} are unproven this wake.

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**13 active sites in 2 files** (`level022/Level22Script.msl` 6,
`level100/LevelScript.msl` 7; e.g. `HighlightHudPart(HUD_COMPASS)`).
Matches corpus TSV. The tutorial levels highlight each HUD element as
it is introduced.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core/HUD owner yet. When one lands: a six-entry (minimum) per-part
highlight-state array with set-to-2/set-to-1 natives; consumer-side
rendering of state 2 is runtime behavior this static note does not
prove. Focused test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535e60`–`0x00535e78` is not
  `d2a93e3b…479fc39`, or the store leaves `0x008aa51c` or the value
  leaves 2.
- A second image-wide imm32 of `0x00535e60`, or any rel32 inbound.
- The handler store leaves `0x64d6d0`, or `.rdata 0x64f89c` stops being
  `"HighlightHudPart\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, array-reference census,
  authored `.msl` recount (`local-lab/famF_hud*.py`).
- Cross-reference (same wake):
  [`IScript__UnHighlightHudPart.md`](IScript__UnHighlightHudPart.md).
