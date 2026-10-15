# CTexture__ctor

Status: active static function note
Last updated: 2026-08-19
Source File: Texture / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. Child `t_9e2c3720` report is data only; every pin below
was re-read from `74154bfa`. The Ghidra database was not opened.
Table name is a research label. Already-pinned callee `0x00512ca0`
and `0x004f2710` bodies are **not** this proof.

> Address: `0x00556cc0`

## Contract

`thiscall` with an SEH frame (`push -1` / `0x005d7d43` /
`fs:[0]`). `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x00556d6e`. Body `0x00556cc0`–`0x00556d6e` is 175 bytes,
SHA-256
`218531027bedb4f90f857713f676e11b20ad910a783899f748cfb62e7dd2fa43`.
Two `E8`: `0x00556ce1` → `0x004f2710` (`ecx = this+8`);
`0x00556d48` → already-pinned `CShaderBase__Init` `0x00512ca0`
(`ecx = 0x00855bb0`, arg `this`). Zero `E9`.

Seven inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x004f2908` | table `CTexture__FindTexture` |
| `0x0053a0a3` | table `CDXBattleLine__Constructor` |
| `0x0053a237` | table `CDXBattleLine__LoadTextures` |
| `0x0053bfa1` | table `CDXCompass__Init` |
| `0x0053bfe2` | table `CDXCompass__Init` |
| `0x0053fbd5` | table `CDXFont__CreateGDIFont` |
| `0x00559c2d` | table `CDXTexture__Deserialize` |

Zero image encodings of imm `c0 6c 55 00`. Those hosts are
**not** claimed.

Stores `[this] = 0x005e59a0`. `[0x005e59a0-4] = 0x00619cc8`;
that COL `+0x0c` is type descriptor `0x006502e8` whose name
at `+8` is `.?AVCDXTexture@@` (file `0x002502f0`). Imm
`a0 59 5e 00` occurs twice: this store and a neighbor. That
neighbor is **not** claimed. `EAX` is `this`. Other this-writes
are offsets only and are **not** named.

Cheapest falsifier: file `0x00156cc0` is not
`6a ff 68 43 7d 5d 00`, **or** `0x00156d6e` is not `c3`,
**or** body SHA-256 is not `21853102…fa43`, **or**
`tools/call_xref_scan.py` on `0x00556cc0` is not the seven
`E8` above, **or** `0x00156cf1` is not
`c7 06 a0 59 5e 00`, **or** `0x002502f0` is not
`2e 3f 41 56 43 44 58 54 65 78 74 75 72 65 40 40 00`, **or**
an eighth inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00556cc0` | `CTexture__ctor` | `6aff 68437d5d00 … c706a0595e00 … b9b05b8500 e853bffbff … c3` | thiscall; SEH; bare ret; 175 B; 2 E8 `0x004f2710` + already-pinned `0x00512ca0` / 0 E9; 7 inbound E8; vptr `0x005e59a0`; COL `.?AVCDXTexture@@`; EAX=this. HIGH on ABI, inbound set, that plant, that COL string. **Not** on callee bodies, hosts, or field names. |
