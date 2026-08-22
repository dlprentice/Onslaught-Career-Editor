# IScript__UnHighlightHudPart

> Address: `0x00535E80`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/`; script-side constants in the shipped `data/MissionScripts/onsldef.msl` | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 35, registered as `UnHighlightHudPart`: the
exact twin of [`IScript__HighlightHudPart.md`](IScript__HighlightHudPart.md)
writing state value **1** (instead of 2) into the same global per-HUD-part
state array at `0x008aa51c`. 13 authored sites, same two tutorial level
scripts.
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

Corpus TSV row 35 is `UnHighlightHudPart` / `0x00535E80` / empty
name-table cell / 13 authored sites; confirmed this wake. Registration:

- Handler immediate: `mov edi, 0x00535e80` (`bf 80 5e 53 00`) at VA
  `0x00530b60` — exactly **one** image-wide imm32 (byte hit at
  `0x00530b61`). Zero rel32 inbound.
- Handler cell store: `mov [0x64d710], edi` at VA `0x00530b6a`.
- Name-pointer store: `mov dword ptr [0x64d6e0], 0x64f888` at VA
  `0x00530bfd`; `.rdata 0x64f888` = `"UnHighlightHudPart\0"`.
- Descriptor: name cell `0x64d6e0`, handler cell +0x30 at `0x64d710`.

## Contract (byte-exact)

Body `0x00535e80`–`0x00535e98` inclusive through the complete
`ret 0xc`, **25 bytes**, SHA-256
`d273f5d1af93a54b9f7a9b3bbd2a56c0e9f84696f85048e2b3757e69eb9e9bd3`.
Zero `E8`, zero decoded `E9`.

```
00535e80  8b 44 24 04        mov eax, [esp+4]           ; args object
00535e84  8b 08              mov ecx, [eax]             ; element 1
00535e86  8b 11              mov edx, [ecx]
00535e88  ff 52 30           call [edx+0x30]            ; INT eval -> eax
00535e8b  c7 04 85 1c a5 8a 00
          01 00 00 00        mov dword [eax*4 + 0x8aa51c], 1   ; NORMAL
00535e96  c2 0c 00           ret 0xc
```

Identical to native 34 except the stored dword. The array's consumer
and semantics notes are owned by
[`IScript__HighlightHudPart.md`](IScript__HighlightHudPart.md).

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `args[0]` via `vtable[+0x30]` | integer HUD-part index | `0x00535e88` |
| `0x008aa51c + index*4` | global per-HUD-part state cell | `0x00535e8b` |
| state `1` | normal / not highlighted | `0x00535e93` |
| `0x64d6e0` / `0x64d710` | registration descriptor cells | `0x00530bfd`, `0x00530b6a` |

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**13 active sites in 2 files** (`level022/Level22Script.msl` 6,
`level100/LevelScript.msl` 7), mirroring the highlight pair one-for-one
(`UnHighlightHudPart(HUD_COMPASS)` etc.). Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

Shares the future HUD owner with HighlightHudPart. Focused test
deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535e80`–`0x00535e98` is not
  `d273f5d1…9eb9e9bd3`, or the store leaves `0x008aa51c` or the value
  leaves 1.
- A second image-wide imm32 of `0x00535e80`, or any rel32 inbound.
- The handler store leaves `0x64d710`, or `.rdata 0x64f888` stops being
  `"UnHighlightHudPart\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, array-reference census,
  authored `.msl` recount (`local-lab/famF_hud*.py`).
- Cross-reference (same wake):
  [`IScript__HighlightHudPart.md`](IScript__HighlightHudPart.md).
