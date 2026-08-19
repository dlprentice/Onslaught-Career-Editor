# CMonitor__SampleHeightfieldNormalAtXY

Status: active static function note
Last updated: 2026-08-18
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-18 from the pristine
specimen at file offset VA − 0x400000 with `tools/disasm_va.py` /
`tools/call_xref_scan.py`. Official safe-copy twin
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` is byte-identical.
The Ghidra database was not opened. Table name is a research label.

> Address: `0x0047ec60`

## Contract

`thiscall`. `ECX` is this (`mov ebx, ecx` at `0x0047ec73`). `EDX` is
the out pointer (`mov esi, edx` at `0x0047ec6b`). One stack arg is a
pointer to two floats (`mov ebp, [esp+0x34]` after `sub esp, 0x28` /
two pushes; `fld [ebp]` / `fld [ebp+4]`). Two `ret 4` encodings
(`c2 04 00`): `0x0047ee22` (in-range) and `0x0047ef11` (OOB). EAX on
both paths is the out pointer. Body `0x0047ec60`–`0x0047ef13`
inclusive is 692 bytes, SHA-256
`cb187f3605193c35e17bd3aa7cd7a614a0c9d28491514e9a05a8f07d4c021f34`.
Predecessor `0x0047eb80` ends `c3` at `0x0047ec53`; twelve `nop` then
this prologue.

Two write polarities through EDX:

| path | when | bytes written |
| --- | --- | --- |
| OOB | `0x0047eef4` | `[out+0]=0`, `[out+4]=0`, `[out+8]=0x3f800000` (+1.0). No `[out+0xc]` |
| in-range | `0x0047ee02` | `[out+0]=ecx`, `[out+4]=[esp+0x18]`, `[out+8]=[esp+0x1c]`, `[out+0xc]=edx` |

In-range Z is seeded `mov [esp+0x30], 0xbf800000` (−1.0) at
`0x0047ed48`. `[out+0xc]` is a copied unread dword; this body does not
compute it. OOB does not touch it.

Twenty-one `.text` `E8`s, zero `E9`: `0x004017e6` / `0x004077c9` /
`0x00407b5b` / `0x0040c803` / `0x004118ef` / `0x004138ec` /
`0x00413bda` / `0x00424e43` / `0x00448ed1` / `0x00449302` /
`0x0047a0f2` / `0x0047d26e` / `0x00493737` / `0x0049a04a` /
`0x0049b1d2` / `0x004ba236` / `0x004bca37` / `0x004bd88d` /
`0x004da2c6` / `0x00508f6a` / `0x0053a51f`. Every site has
`mov ecx, 0x006fadc8` before the call.

Already-pinned `0x005088b0` arm at `0x00508f6a`:

```
mov  ecx, 0x006fadc8            ; 0x00508f2b
…
add  eax, 0x1c                  ; owner+0x1c
lea  edx, [esp+0x2c]
push eax
call 0x0047ec60                 ; 0x00508f6a
```

No `mov ecx, imm` between `0x00508f2b` and the `E8`. After return the
caller reads out+0/+4/+8 and ends `fadd [esp+0x14]` / `fstp [esp+0x14]`
at `0x00508fa3` (`d8 44 24 14 d9 5c 24 14`). Mix algebra is not claimed.

Cheapest falsifier: file `0x0007ec60` is not `83 ec 28 53 55 8b 6c 24 34`,
**or** `0x0007ec6b` is not `8b f2`, **or** `0x0007ec73` is not `8b d9`,
**or** `0x0007ee22` is not `c2 04 00`, **or** `0x0007ef11` is not
`c2 04 00`, **or** `0x0007eef4` is not
`c7 06 00 00 00 00 c7 46 04 00 00 00 00 c7 46 08 00 00 80 3f`,
**or** `0x0007ee09` is not `89 0e`, **or** `0x0007ee19` is not
`89 56 0c`, **or** `0x0007ed48` is not `c7 44 24 30 00 00 80 bf`,
**or** `tools/call_xref_scan.py` on `0x0047ec60` is not exactly those
21 `CALL` sites, **or** `0x00108f2b` is not `b9 c8 ad 6f 00`, **or**
`0x00108f61` is not `8d 54 24 2c`, **or** `0x00108fa3` is not
`d8 44 24 14 d9 5c 24 14`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0047ec60` | `CMonitor__SampleHeightfieldNormalAtXY` | `83ec28 53 55 8b6c2434 56 57 8bf2 … 8bd9 … c20400 … c70600000000 c7460400000000 c746080000803f … c20400` | thiscall; ECX→EBX; EDX=out*; one stack xy*; `ret 4`; OOB `(0,0,+1.0)`; in-range four dwords; this imm `0x006fadc8` on all 21 `E8`. HIGH on ABI, inbound set, both rets, OOB stores, in-range store slots, `0x00508f6a` add into `[esp+0x14]`. **Not** on authored names, `[out+0xc]`, or the `0x005088b0` mix meaning. |

## Open

- What `0x006fadc8` is beyond the already-shared BSS this of
  `0x00490a40` / `0x0047eb80`.
- Authored names for `this+0x1028` / `+0x102c`.
- What `[out+0xc]` is supposed to carry.
- The `0x005088b0` meaning of the FPU product that consumes these
  three dwords.
