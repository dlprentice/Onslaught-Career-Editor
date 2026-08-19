# CHeightField__TraceMapLoadRequestAndCheckLoadedFlags

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` after
`t_3ef06495`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Map-load runtime is **not** this proof.

> Address: `0x00490f50`

## Contract

`thiscall`. Three stack args. Four exits, all `ret 0xc` (`c2 0c 00`)
at `0x00490fe9`, `0x00491017`, `0x00491049`, `0x00491055`. `EAX` is
`1` on the first three exits and `0` on the last (`xor eax, eax`).
Body `0x00490f50`–`0x00491057` is 264 bytes, SHA-256
`f1cf592f2a6abcde7728c963b480d9fe87815c5b7db5802ad4112db59b955387`.
Four instruction-aligned `E8`, zero instruction-aligned `E9`. A raw
`e9` at `0x00490fc0` is the second byte of `c1 e9 02`
(`shr ecx, 2`).

| VA | dest (table label) |
| --- | --- |
| `0x00490f6a` | `0x0055de9b` (`sprintf`) |
| `0x00490fd0` | `0x0040c640` (`DebugTrace`) |
| `0x00491003` | `0x0040c640` |
| `0x00491035` | `0x0040c640` |

One inbound `.text` `E8`, zero `E9`: `0x0050bc29`. The site:

```
push 1
push eax
push ecx
mov  ecx, 0x006fadc8
call 0x00490f50
```

File `0x0010bc20` is `6a 01 50 51 b9 c8 ad 6f 00 e8 22 53 f8 ff`.
The caller body is **not** claimed.

This-relative **reads** only: `[this+0x93e0]` at `0x00490ff4`
(when arg2 != 0) and `[this+0x93e4]` at `0x00491026` (when arg2 ==
0 and arg3 != 0). No this-relative writes. Those are the same two
slots Deserialize sets to 1 and `0x00490f10` zeros. If arg1 == -1,
both slots are skipped and `EAX = 1`.

Quoted C-strings, not authored names: `Loading map %d`,
` (all)\n`, ` (properties only)\n`, ` (geometry only)\n`,
` (nothing?!)\n`, `Map geometry is already loaded - ignoring\n`,
`Map properties are already loaded - ignoring\n`.

Cheapest falsifier: file `0x00090f50` is not
`83 ec 44 53 55 8b 6c 24 50`, **or** `0x00091055` is not
`c2 0c 00`, **or** body SHA-256 is not `f1cf592f…5387`, **or**
`tools/call_xref_scan.py` on `0x00490f50` is not exactly `E8` at
`0x0050bc29`, **or** `0x0010bc20` is not
`6a 01 50 51 b9 c8 ad 6f 00 e8 22 53 f8 ff`, **or**
`0x00090ff4` is not `8b 81 e0 93 00 00`, **or** `0x00091026` is
not `8b 82 e4 93 00 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00490f50` | `CHeightField__TraceMapLoadRequestAndCheckLoadedFlags` | `83ec44 5355 8b6c2450 … 8b81e0930000 … 8b82e4930000 … c20c00` | thiscall; ret 0xc; EAX in {0,1}; this imm `0x006fadc8`; reads `[+0x93e0]`/`[+0x93e4]`. HIGH on ABI, inbound, those loads, four E8 dests. **Not** on caller body or authored names. |
