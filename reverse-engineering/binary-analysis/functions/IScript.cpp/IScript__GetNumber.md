# IScript__GetNumber

> Address: `0x00535980`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 131, registered as `GetNumber`: zero script
arguments; when the attached thing carries the dword flag bit
`0x80000` of `[thing+0x34]`, reads the thing's number cell
`[thing+0x270]`, else 0. Boxes as a `CInt` (vptr `0x005e4af8` — the
same class FollowWaypoint boxes its arrived-flag into). Two authored
uses, both in level512's Tube script.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk,
whole-`.text` rel32 xref scan, authored `.msl` recount. No `FUN_*`
milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 131 is `GetNumber` / `0x00535980` / empty name-table
cell / 2 authored sites; confirmed this wake. Registration:

- Handler immediate: `mov ebp, 0x00535980` (`bd 80 59 53 00`) at VA
  `0x00532e6a` — exactly **one** image-wide imm32 (byte hit at
  `0x00532e6b`). Zero rel32 inbound.
- Handler cell store: `mov [0x64ef10], ebp` at VA `0x00532e6f`.
- Descriptor: handler cell `0x64ef10`, stride-paired name cell
  `0x64eee0` (`.rdata` `"GetNumber\0"` exists; individual store not
  isolated this wake).
- Neighbors: `TeleportOrientation` (139) `0x64eed0`; `SetSlotSave`
  (133) name cell `0x64ef60`.

## Contract (byte-exact)

Body `0x00535980`–`0x005359c3` inclusive through the complete final
`ret 0xc`, **68 bytes**, SHA-256
`2d68f980506706efc9c3b355264d86a0c76672b85ab1dfc6436c7af970a8a955`.

```
00535980  mov eax, [ecx+0x10]             ; attached thing
00535986  test dword ptr [eax+0x34], 0x80000   ; dword flag bit
0053598d  je box                          ; miss -> 0
0053598f  mov esi, [eax+0x270]            ; number cell
box:
00535995  alloc 0x18 via 0x5490e0 (__FILE__ 0x64fa40, line 0x477)
          mov dword ptr [eax], 0x005e4af8 ; CInt vptr
          mov dword ptr [eax+4], esi      ; int payload
          mov [out], eax; ret 0xc
```

Note this gate tests a **dword** (`f7 40 34 … 0x00080000`), unlike the
byte gates elsewhere — bit `0x80000` sits above the byte mask. The
`CInt` vptr matches the boxed value in IScript's arrived() fire site
([`IScript.cpp.md`](../IScript.cpp.md)), closing that class identity
from the other side.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` / `[thing+0x34]&0x80000` | numbered-thing flag (dword test) | `0x00535986` |
| `[thing+0x270]` | thing number cell | `0x0053598f` |
| `0x005e4af8` / `+4 dword` | `CInt` vptr / payload | `0x005359b5` region |
| `0x64eee0` / `0x64ef10` | descriptor cells (name side by stride) | `0x00532e6f` |

Who writes `[thing+0x270]`: open this wake (cheapest instrument: an
image-wide census of stores to `[reg+0x270]`).

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**2 active sites**, both `level512/Tube.msl` (`n = GetNumber();`).
Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands: optional per-thing integer tag,
surfaced to scripts only when the `0x80000` flag is set. Focused test
deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535980`–`0x005359c3` is not
  `2d68f980…70a8a955`, or the flag leaves `0x80000`, the cell leaves
  `[+0x270]`, or the vptr leaves `0x005e4af8`.
- A second image-wide imm32 of `0x00535980`, or any rel32 inbound.
- The handler store leaves `0x64ef10`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famH_micro*.py`).
