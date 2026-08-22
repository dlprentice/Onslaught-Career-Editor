# IScript__UnsetObjective

> Address: `0x00535EE0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked
2026-08-22)
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 30, registered as `UnsetObjective`: the exact
twin of [`IScript__SetObjective.md`](IScript__SetObjective.md) with
argument 0 — same 12-byte stub, same callee `0x004f3970`, which clears
bit `0x20` of `[thing+0x2c]` and removes the thing from the global
objective-marker set `0x00855140`. 250 authored sites across 217 files.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor-cell
walk, whole-`.text` rel32 xref scan, authored `.msl` recount. No
`FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 30 is `UnsetObjective` / `0x00535EE0` / empty name-table
cell / 250 sites; confirmed this wake. Registration:

- Handler immediate: `mov edi, 0x00535ee0` (`bf e0 5e 53 00`) at VA
  `0x005309ab` — exactly **one** image-wide imm32 (byte hit at
  `0x005309ac`). Zero rel32 inbound.
- Handler cell store: `mov [0x64d5d0], edi` at VA `0x005309b5`.
- Name-pointer store: `mov dword ptr [0x64d5a0], 0x64f8dc` at VA
  `0x00530a30`; `.rdata 0x64f8dc` = `"UnsetObjective\0"`.
- Descriptor: name cell `0x64d5a0`, handler cell +0x30 at `0x64d5d0`.

## Contract (byte-exact)

Body `0x00535ee0`–`0x00535eec` inclusive through the complete
`ret 0xc`, **13 bytes**, SHA-256
`0ec7dfff6ad0dba017b45b0a9840f6b587b899e88aaedb29d1d0eabfb842b35f`.

```
00535ee0  8b 49 10           mov ecx, [ecx+0x10]        ; attached thing
00535ee3  6a 00              push 0                     ; clear
00535ee5  e8 86 da fb ff     call 0x004f3970            ; objective flag
00535eea  c2 0c 00           ret 0xc
```

The setter's full contract (bit law, set membership, cross-anchors) is
owned by [`IScript__SetObjective.md`](IScript__SetObjective.md) and not
repeated here.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` | attached thing (no gate) | `0x00535ee0` |
| `0x64d5a0` / `0x64d5d0` | registration descriptor cells | `0x00530a30`, `0x005309b5` |

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**250 active sites across 217 files** (`TargetZone*`/checkpoint/
transport/vital-building scripts). Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet; shares the future owner with SetObjective (one flag,
two entry points). Focused test deferred until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00535ee0`–`0x00535eec` is not
  `0ec7dfff…842b35f`, or the callee leaves `0x004f3970` or the constant
  leaves `0`.
- A second image-wide imm32 of `0x00535ee0`, or any rel32 inbound.
- The handler store leaves `0x64d5d0`, or `.rdata 0x64f8dc` stops being
  `"UnsetObjective\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famE_*.py`).
- Cross-reference (same wake):
  [`IScript__SetObjective.md`](IScript__SetObjective.md),
  [`IScript__IsObjective.md`](IScript__IsObjective.md).
