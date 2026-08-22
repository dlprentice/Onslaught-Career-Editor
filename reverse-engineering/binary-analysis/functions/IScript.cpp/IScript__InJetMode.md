# IScript__InJetMode

> Address: `0x005380F0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 125, registered as `InJetMode`: zero script
arguments; returns TRUE when the attached thing carries the class bit
`0x08` of `[thing+0x34]` **and** predicate `0x00408120` returns zero.
Boxes the answer as a `CBool` (vptr `0x005e4d50`). Five authored uses —
the tutorial/guardzone "is the player on foot?" gate.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk,
whole-`.text` rel32 xref scan, authored `.msl` recount. No `FUN_*`
milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 125 is `InJetMode` / `0x005380F0` / empty name-table
cell / 5 authored sites; confirmed this wake. Registration:

- Handler immediate: `mov ebp, 0x005380f0` (`bd f0 80 53 00`) at VA
  `0x00532c83` — exactly **one** image-wide imm32 (byte hit at
  `0x00532c84`). Zero rel32 inbound.
- Handler cell store: `mov [0x64ed90], ebp` at VA `0x00532c88`.
- Descriptor: handler cell `0x64ed90`, stride-paired name cell
  `0x64ed60` (`.rdata` `"InJetMode\0"` string exists; individual store
  not isolated this wake — same gap note as SetVelocity).
- Neighbors: `GetSlot` (124) `0x64ed50`; `SetPlayerLives` (126)
  `0x64edd0`.

## Contract (byte-exact)

Body `0x005380f0`–`0x0053813d` inclusive through the complete final
`ret 0xc`, **78 bytes**, SHA-256
`6a526a4e214860206d1b6f79a0a6b872fbb35b75f3e81f404e6610d04e2184ad`.

```
005380f0  mov ecx, [ecx+0x10]             ; attached thing
005380f6  test byte ptr [ecx+0x34], 8     ; class bit 0x08
005380fa  je box-false
005380fc  call 0x00408120                 ; jet-state predicate -> eax
00538103  test eax, eax; jne box-false    ; nonzero = NOT in jet mode
          mov esi, 1                      ; result TRUE
box:
0053812a  alloc 0x18 via 0x5490e0 (__FILE__ 0x64fa40, line 0x82a)
          mov dword ptr [eax], 0x005e4d50 ; CBool vptr
00538132  setne cl; mov byte ptr [eax+4], cl
          mov [out], eax; ret 0xc
```

Semantics: TRUE requires class bit AND `0x00408120()==0`. The
predicate's body is not walked this wake; its identity as the "jet mode
off" probe is inferred from position and polarity only — honest
unknown, cheapest instrument a caller census of `0x00408120`.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` / `[thing+0x34]&0x08` | class-bit gate (weapon/BattleEngine family marker) | `0x005380f6` |
| `0x00408120` | jet-state predicate (polarity: 0 ⇒ in jet mode) | `0x005380fc` |
| `0x005e4d50` / `+4 byte` | `CBool` vptr / payload | `0x0053812a` region |
| `0x64ed60` / `0x64ed90` | descriptor cells (name side by stride) | `0x00532c88` |

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**5 active sites in 5 files** (`level100 TargetZone2/3/4.msl`,
`level311/312 guardzone.msl`; pattern
`if (other_thing.InJetMode() == FALSE)`). Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet; pairs with the weapon-query family's class-bit law.
Focused test deferred until an owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x005380f0`–`0x0053813d` is not
  `6a526a4e…2184ad`, or the predicate leaves `0x00408120` or the vptr
  leaves `0x005e4d50`.
- A second image-wide imm32 of `0x005380f0`, or any rel32 inbound.
- The handler store leaves `0x64ed90`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famH_micro*.py`).
