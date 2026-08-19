# CLandscapeTexture__FlushUpdateQueue

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Queue algebra is **not** this proof.

> Address: `0x0048e7c0`

## Contract

Not incoming-`ECX` thiscall. Entry `ECX` is never read. Zero-arg.
Bare `ret` at `0x0048e874`. Body `0x0048e7c0`–`0x0048e874` is 181
bytes, SHA-256
`7c19ceee7c0fc172d47cb426f124b1e16f7bb44064d72750cec3ca04deff9502`.
One `E8` to already-pinned `0x0048ea80`, zero `E9`. 66
instructions, no gap.

The already-pinned UpdateTile inbound is this site:

```
0048e816  mov  ax, word ptr [ebp+4]
0048e81a  mov  ecx, dword ptr [ebp]
0048e81d  push eax
0048e81e  call 0x0048ea80
```

`EBP` walks stride `0x14` from imm `0x006fa7d8` until
`[0x0062d868]`. UpdateTile's this is `[ebp]`, not an image
immediate. Queue names are **not** claimed.

Two inbound `.text` `E8`, zero `E9`. Caller bodies are **not**
claimed.

Cheapest falsifier: file `0x0008e7c0` is not
`83 ec 40 8b 15 68 d8 62 00`, **or** `0x0008e874` is not `c3`,
**or** body SHA-256 is not `7c19ceee…9502`, **or**
`tools/call_xref_scan.py` on `0x0048e7c0` is not exactly `E8` at
`0x0048e8db` / `0x005472cf`, **or** `0x0008e816` is not
`66 8b 45 04 8b 4d 00 50 e8 5d 02 00 00`, **or** `0x0008e8db`
is not `e8 e0 fe ff ff`, **or** `0x001472cf` is not
`e8 ec 74 f4 ff`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e7c0` | `CLandscapeTexture__FlushUpdateQueue` | `83ec40 8b1568d86200 … 668b4504 8b4d00 50 e85d020000 … c3` | not incoming-ECX; bare ret; 181 B; 1 E8 UpdateTile / 0 E9. HIGH on ABI, that call site, the two abs. **Not** on queue algebra or authored names. |
