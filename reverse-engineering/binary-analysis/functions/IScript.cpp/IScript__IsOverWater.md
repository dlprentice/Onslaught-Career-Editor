# IScript__IsOverWater

> Address: `0x00538150`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 143, registered as `IsOverWater`: zero script
arguments; calls the attached thing's water-overlap predicate
`0x004f3de0` (no gate, no class check) and boxes the answer as a
`CBool`. Zero authored uses (`DORMANT_CANDIDATE`).
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads, image-wide imm32 census, descriptor walk
(this block is ecx-carried; the handler store sits at `0x00533392`),
whole-`.text` rel32 xref scan, authored `.msl` recount. No `FUN_*`
milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 143 is `IsOverWater` / `0x00538150` / empty name-table
cell / 0 sites; confirmed this wake (recount zero). Registration:

- Handler immediate: `mov ecx, 0x00538150` (`b9 50 81 53 00`) at VA
  `0x0053334c` — exactly **one** image-wide imm32 (byte hit at
  `0x0053334d`). Zero rel32 inbound.
- Handler cell store: `mov [0x64f210], ecx` at VA `0x00533392`.
- Name-pointer store: `mov dword ptr [0x64f1e0], 0x64f234` at VA
  `0x00533360`; `.rdata 0x64f234` = `"IsOverWater\0"`.
- Descriptor: name cell `0x64f1e0`, handler cell +0x30 at `0x64f210`
  — the stride law holds on the last descriptor of the table.

## Contract (byte-exact)

Body `0x00538150`–`0x0053818e` inclusive through the complete final
`ret 0xc`, **63 bytes**, SHA-256
`09f0f6eec9fd75886d96ab221b8a21b63a6479d431118925c14972222cf3364f`.

```
00538150  mov ecx, [ecx+0x10]             ; attached thing
00538154  call 0x004f3de0                 ; water predicate -> eax
0053816c  alloc 0x18 via 0x5490e0 (__FILE__ 0x64fa40, line 0x832)
          mov dword ptr [eax], 0x005e4d50 ; CBool vptr
00538183  setne cl; mov byte ptr [eax+4], cl
          mov [out], eax; ret 0xc
```

The predicate `0x004f3de0` is not walked this wake (honest unknown;
cheapest instrument a caller census + head decode). The boxing shape is
identical to InJetMode's.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[this+0x10]` | attached thing (no gate) | `0x00538150` |
| `0x004f3de0` | water-overlap predicate | `0x00538154` |
| `0x005e4d50` / `+4 byte` | `CBool` vptr / payload | `0x0053817b` region |
| `0x64f1e0` / `0x64f210` | registration descriptor cells | `0x00533360`, `0x00533392` |

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**zero active sites** (DORMANT_CANDIDATE holds).

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet; pairs with the water-height consumers recorded in
the Family D notes. Focused test deferred until an owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x00538150`–`0x0053818e` is not
  `09f0f6ee…22cf3364f`, or the predicate leaves `0x004f3de0` or the
  vptr leaves `0x005e4d50`.
- A second image-wide imm32 of `0x00538150`, or any rel32 inbound.
- The handler store leaves `0x64f210`, or `.rdata 0x64f234` stops being
  `"IsOverWater\0"`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famH_micro*.py`).
