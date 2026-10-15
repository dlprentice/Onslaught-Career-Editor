# CHeightField__GetHeightSamplePacked16

Status: active static function note
Last updated: 2026-09-08
Summary: integer packed-height lookup, including its asymmetric mask-edge index.
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. The Ghidra
database was not opened. Table name is a research label.

> Address: `0x0047ea20`

## Contract

`thiscall` plus a register operand. `ECX` is this (`[ecx+0x1028]`).
`EDX` is one packed coordinate. One stack arg is the other
(`mov eax, [esp+4]` before the push). Five `ret 4` sites:
`0x0047ea63` (in-range), `0x0047ea90`, `0x0047eab5`, `0x0047eae9`
(three mask-edge arms), `0x0047eaf0` (AX=0). Body
`0x0047ea20`–`0x0047eaf2` is 211 bytes, SHA-256
`a08365f3e96f7ad423c6e3853e8f1a4b0690e6d15cfa94b82ce85cb7420d32e6`.
Zero `E8`, zero `E9`.

September 8 integration re-read the body for AirGuide's 9×9 integer scan.
With X in EDX and Y on the stack, let `mx=X&0x3ffe00` and
`my=Y&0x3ffe00`. The signed-short element indices are:

| Branch | Element index |
| --- | --- |
| `(mx|my)==0` | `81*(64*((X>>3)&63)+((Y>>3)&63))+9*(Y&7)+(X&7)` |
| `mx==512 && my==512` | `331775` |
| `mx==512` | `326600+81*((Y>>8)&63)+9*(Y&7)` |
| `my==512` | `5175+5184*((X>>3)&63)+(X&7)` |
| Other | return zero without reading the table |

The X-edge arm really shifts Y by **8**, not 3. Mask comparisons also admit
coordinate aliases such as 513 and 768; this is not a conventional clamped
513×513 array lookup. `Level100Terrain.SampleAirGuideHeightUnits` preserves
these branches, separately from the continuous terrain sampler. AirGuide
`[004028e0,004029de)` (SHA-256
`2b6abd803ff6ea38899902a74a663d295cf709427f6d210335137ecd967336df`)
rounds owner X/Y to nearest-even, visits Y outer/X inner in steps of 5 from
−20 through +20, and retains minimum clearance above ground or water. Its
initial minimum is float word `497423f0` (999999), not FLT_MAX. The focused
`RetailPlaneMotionTests` cover edge aliases, the finite ceiling and the first
observed 6.16-unit clearance; this does not independently validate scheduling.

EAX is a 16-bit word, or 0:

| polarity | writer | when |
| --- | --- | --- |
| AX = `[base + index*2]` | `0x0047ea5f` | `(edx \| arg) & 0x3ffe00 == 0` |
| AX = `[base + 0xa1ffe]` | `0x0047ea89` | both coords have bits `0x3ffe00 == 0x200` |
| AX = `[base + index*2 + 0x9f790]` | `0x0047eaad` | EDX-side mask is 0x200, stack-side is not |
| AX = `[base + index*2 + 0x286e]` | `0x0047eae1` | stack-side mask is 0x200, EDX-side is not |
| AX = 0 | `0x0047eaec` | any other `0x3ffe00` residue |

`base` is `[this+0x1028]`. In-range index uses `>>3`/`&0x3f` cells
and `&7` fines with two `lea r, [r+r*8]` (×9) steps. Authored
cell-size names are **not** claimed.

Ten `.text` `E8`s, zero `E9`, including the already-pinned
`0x00490e79`. Other inbound `this` values are **not** claimed.

Cheapest falsifier: file `0x0007ea20` is not `8b 44 24 04 56 8b f2`,
**or** `0x0007ea63` is not `c2 04 00`, **or** `0x0007eaf0` is not
`c2 04 00`, **or** `0x0007eaec` is not `66 33 c0`, **or** body
SHA-256 is not `a08365f3…32e6`, **or** `tools/call_xref_scan.py` on
`0x0047ea20` is not exactly 10 `CALL` / 0 `JMP`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0047ea20` | `CHeightField__GetHeightSamplePacked16` | `8b442404 56 8bf2 0bf0 f7c600fe3f00 … 668b0441 c20400 … 6633c0 5e c20400` | thiscall+EDX; ret 4 ×5; AX=grid word or 0. HIGH on ABI, inbound count, both polarities. Not on authored names or other callers' `this`. |
