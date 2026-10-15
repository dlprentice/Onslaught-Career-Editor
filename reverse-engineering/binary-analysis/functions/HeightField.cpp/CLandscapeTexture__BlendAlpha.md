# CLandscapeTexture__BlendAlpha

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Blend algebra is **not** this proof.

> Address: `0x0048ee00`

## Contract

Not incoming-`ECX` thiscall. First insn is `mov ecx, [esp+0x18]`
(`8b 4c 24 18`); entry `ECX` is never read. Seven stack dwords
(`ret 0x1c` at `0x0048eef3`). Body `0x0048ee00`–`0x0048eef5` is
246 bytes, SHA-256
`dfecc33cfea43e2c94180db58e39e47935d0731d0c2940c84810f74cbadc2c1d`.
Zero `E8` / `E9`. 91 instructions, no gap. Eight `90` after the
`ret` are outside the body hash. `EAX` is not contracted.

Three inbound `.text` `E8`, zero `E9` — the already-pinned
UpdateTile / UpdateTileRange sites:

| site | plant | file bytes |
| --- | --- | --- |
| `0x0048ebf4` | `mov ecx, esi` | `8b ce e8 07 02 00 00` |
| `0x0048ed84` | earlier `mov ecx, esi` at `0x0048ed74` | `e8 77 00 00 00` |
| `0x0048f0b1` | `mov ecx, edi` | `8b cf e8 4a fd ff ff` |

Those plants are the callers' thiscall shape. This body does not
consume them. Caller bodies beyond the site bytes are **not**
claimed.

No this-relative slot. The first stack dword used as a shift count
feeds `shl edi, cl` with `edi=1`. Pixel-walk / `0x07e0f81f` mask
algebra is **not** claimed.

Cheapest falsifier: file `0x0008ee00` is not
`8b 4c 24 18 53 55 56`, **or** `0x0008eef3` is not `c2 1c 00`,
**or** body SHA-256 is not `dfecc33c…2c1d`, **or**
`tools/call_xref_scan.py` on `0x0048ee00` is not exactly `E8` at
`0x0048ebf4` / `0x0048ed84` / `0x0048f0b1`, **or** `0x0008ebf2`
is not `8b ce e8 07 02 00 00`, **or** `0x0008f0af` is not
`8b cf e8 4a fd ff ff`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048ee00` | `CLandscapeTexture__BlendAlpha` | `8b4c2418 535556 … c21c00` | not incoming-ECX thiscall; ret 0x1c; 246 B; 0 E8/E9; 3 inbound from UpdateTile/Range. HIGH on ABI, inbound set, unused entry ECX. **Not** on blend algebra or authored names. |
