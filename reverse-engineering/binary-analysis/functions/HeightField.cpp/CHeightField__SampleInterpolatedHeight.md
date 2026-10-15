# CHeightField__SampleInterpolatedHeight

Status: active static function note
Last updated: 2026-08-18
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-18 from the pristine
specimen at file offset VA − 0x400000. The Ghidra database was not opened.
Table name is a research label.

> Address: `0x0047eb00`

## Contract

`thiscall` plus a register operand. `ECX` is this. `EDX` is the X
fixed-point word. One stack arg is the Y word (`mov edi, [esp+0x10]`
after three pushes). One `ret 4` at `0x0047eb7c`. Body
`0x0047eb00`–`0x0047eb7e` is 126 bytes, SHA-256
`1071aafbc5919071d180c303049a904473f3a907de6b497bdb4e7abb10e55f9a`.
Next function is `0x0047eb80`
([`CStaticShadows__SampleShadowHeightBilinear.md`](CStaticShadows__SampleShadowHeightBilinear.md)).

EAX is a signed 16-bit bilinear sample from the word grid at
`[this+0x1028]`:

| piece | encoding |
| --- | --- |
| cell X | `(edx >> 11) & 0x3f` |
| cell Y | `(edi >> 11) & 0x3f` |
| fine X | `(edx >> 8) & 7` |
| fine Y | `(edi >> 8) & 7` |
| frac X | `edx & 0xff` |
| frac Y | `edi & 0xff` |
| index | `9 * (9 * (cellX * 64 + cellY) + fineY) + fineX` |

Four neighbour words at `base + index*2`, `+2`, `+0x12`, `+0x14`.
Lerp X at each Y (`imul` / `sar 8`), then lerp Y. EAX is that integer;
the sole caller `movsx`s AX and `fild`s it.

One `.text` `E8`, at `0x00490c47` inside `0x00490a40`: `push edi` /
`mov ecx, ebx` / park `[ebx+0x102c]` / `call`. After return:
`movsx ecx, ax`; `fild`; `fmul` the parked scale; `fcomp` current Z;
`test ah, 1` / `jne 0x00490cb3` (sample·scale `<` Z is a hit).

Cheapest falsifier: file `0x0007eb00` is not `53 56 57 8b 7c 24 10`,
**or** `0x0007eb7c` is not `c2 04 00`, **or** `tools/call_xref_scan.py`
on `0x0047eb00` is not exactly `E8 @ 0x00490c47`, **or**
`0x00090c47` is not `e8 b4 de fe ff`, **or** `0x00090c4c` is not
`0f bf c8`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0047eb00` | `CHeightField__SampleInterpolatedHeight` | `535657 8b7c2410 8bc2 8bdf c1f80b 83e03f 8b8928100000 … 0fbf1441 … c20400` | thiscall + EDX X-word; one stack Y; `ret 4`; EAX = signed bilinear word. HIGH on ABI, inbound, lerp shape. Not on authored cell-size names. |
