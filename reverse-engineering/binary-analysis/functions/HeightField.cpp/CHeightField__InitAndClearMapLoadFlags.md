# CHeightField__InitAndClearMapLoadFlags

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` after
`t_b6c72d5c`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. The callee at `0x004fdc10` is only the six bytes below.

> Address: `0x00490f10`

## Contract

`thiscall`. Zero stack args. `ECX`→`ESI`. Two bare `ret` (`c3`) at
`0x00490f1d` and `0x00490f32`. `EAX` is `0` or `1`. Body
`0x00490f10`–`0x00490f32` is 35 bytes, SHA-256
`cb1c28ffcc76b351086c5c874cf5090b3c4b10a4f7a57c9d3c907ae34a25aef3`.
One `E8`, zero `E9`.

The `E8` at `0x00490f13` is `0x004fdc10`:

```
mov  eax, 1
ret
```

If that `EAX` is 0: early `ret` with that `EAX`. Else `xor eax, eax`,
`[this+0x93e0] = 0`, `[this+0x93e4] = 0`, then `EAX = 1`. On this
specimen the stub is always 1, so the early-out bytes exist but are
not taken unless `0x004fdc10` is patched. No name is claimed for the
stub.

One inbound `.text` `E8`, zero `E9`: `0x0046c38f`. The site loads
the already-pinned BSS this first:

```
mov  ecx, 0x006fadc8
call 0x00490f10
```

File `0x0006c38a` is `b9 c8 ad 6f 00 e8 7c 4b 02 00`. The caller
body is **not** claimed.

Already-pinned Deserialize `0x00491060` writes `1` into the same
two slots. Authored names are **not** claimed.

Cheapest falsifier: file `0x00090f10` is not `56 8b f1 e8 f8 cc 06 00`,
**or** `0x00090f32` is not `c3`, **or** body SHA-256 is not
`cb1c28ff…aef3`, **or** `tools/call_xref_scan.py` on `0x00490f10`
is not exactly `E8` at `0x0046c38f`, **or** `0x0006c38a` is not
`b9 c8 ad 6f 00 e8 7c 4b 02 00`, **or** `0x00090f20` is not
`89 86 e0 93 00 00`, **or** `0x00090f26` is not
`89 86 e4 93 00 00`, **or** `0x000fdc10` is not
`b8 01 00 00 00 c3`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00490f10` | `CHeightField__InitAndClearMapLoadFlags` | `568bf1 e8f8cc0600 85c0 7502 5ec3 33c0 8986e0930000 8986e4930000 b801000000 5e c3` | thiscall; EAX in {0,1}; zeros `[+0x93e0]`/`[+0x93e4]` after stub `0x004fdc10`; inbound `mov ecx,0x006fadc8`. HIGH on ABI, inbound, both stores, stub six bytes. **Not** on caller body or authored names. |
