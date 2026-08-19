# CStaticShadows__SampleShadowHeightBilinear

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

> Address: `0x0047eb80`

## Contract

`thiscall` plus a register operand. `ECX` is this (`[ecx+0x1028]` /
`[ecx+0x102c]`). `EDX` is a pointer to two floats (`fld [edx]`,
`fld [edx+4]`). Zero stack args. Two bare `ret` (`c3`) sites:
`0x0047ec48` (in-grid) and `0x0047ec53` (OOB). Body
`0x0047eb80`–`0x0047ec53` is 212 bytes, SHA-256
`cc26a2010da70cfa51d84f256ec1ec759a15e5a1fb3adc717b7a84bda073ea63`.
Predecessor `0x0047eb00` ends `ret 4` at `0x0047eb7c`; one `nop` then
this prologue. Next function is `0x0047ec60`.

The return is **ST0**, not EAX.

| polarity | writer | when |
| --- | --- | --- |
| ST0 = bilinear word `fild` × `[this+0x102c]` | `fild [esp+4]` / `fmul [ecx+0x102c]` at `0x0047ec3b` | `(xbits \| ybits) & 0x3e0000 == 0` |
| ST0 = 0.0 | `fld [0x005d856c]` (`u32 0`) at `0x0047ec49` | that mask is nonzero |
| EAX | leftover grid / lerp / the OOB `or` | never a declared return |

`xbits` / `ybits` are the two incoming floats after `fsub [0x005dbdf0]`
/ `fadd [0x005dbdec]` and a bitcast. The in-grid index uses the same
6-bit / 3-bit / 8-bit split already pinned on `0x0047eb00`, then four
`movsx` words at `base+index*2`, `+2`, `+0x12`, `+0x14` and `imul` /
`sar 8` lerps before the `fild`.

One hundred ten `.text` `E8`s, zero `E9`. Every site has
`mov ecx, 0x006fadc8` before the call. `0x00490a40` is absent (already
pinned: that body calls `0x0047eb00`, not this one).

Fire wrappers `0x004fb500` / `0x004fb5a0` pass `EDX = target+0x1c` and
consume ST0:

```
lea  edx, [edi+0x1c]            ; 0x004fb523 / 0x004fb5d9
mov  ecx, 0x006fadc8
call 0x0047eb80
fld  [0x006fbdfc]
fcomp st(1)                     ; d8 d9
```

Cheapest falsifier: file `0x0007eb80` is not `83 ec 08 d9 02`, **or**
`0x0007ebf1` is not `8b 91 28 10 00 00`, **or** `0x0007ec3f` is not
`d8 89 2c 10 00 00`, **or** `0x0007ec48` is not `c3`, **or**
`0x0007ec49` is not `d9 05 6c 85 5d 00`, **or** `0x0007ec53` is not
`c3`, **or** `tools/call_xref_scan.py` on `0x0047eb80` is not exactly
110 `CALL` / 0 `JMP`, **or** `0x000fb523` is not
`8d 57 1c b9 c8 ad 6f 00 e8 50 36 f8 ff d9 05 fc`, **or**
`0x000fb536` is not `d8 d9`, **or** `0x000fb5d9` is not
`8d 57 1c b9 c8 ad 6f 00 e8 9a 35 f8 ff d9 05 fc`, **or**
`0x000fb5ec` is not `d8 d9`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0047eb80` | `CStaticShadows__SampleShadowHeightBilinear` | `83ec08 d902 d825f0bd5d00 … 8b9128100000 … d8892c100000 c3 d9056c855d00 … c3` | thiscall + EDX xy*; bare `ret`; ST0 = sample·`[this+0x102c]` or 0.0; this imm `0x006fadc8` on all 110 `E8`. HIGH on ABI, inbound count, both rets, ST0 polarity, fire-wrapper `target+0x1c`. **Not** on authored names or what `0x006fadc8` is beyond the shared BSS this. |

## Open

- What `0x006fadc8` is beyond the already-shared BSS this of
  `0x00490a40` / `0x0047eb00`.
- Authored names for `this+0x1028` / `+0x102c`.
- Why the bias is `fsub [0x005dbdf0]` / `fadd [0x005dbdec]` (bytes do
  that; the authored unit is not pinned here).
