# CLandscapeTexture__FreeTexture

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. `0x00549220` body is **not** this proof.

> Address: `0x0048e310`

## Contract

`thiscall`. `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x0048e32d`. Body `0x0048e310`–`0x0048e32d` is 30 bytes,
SHA-256
`21c3329ce4f9b3c7d0e1cb4b9b61a3b04949106993fb3470c1451f8383034554`.
One `E8` (`0x0048e320` → already-named
`CDXMemoryManager__Free` `0x00549220`). Zero `E9`. Two `nop`s
after the `ret` are **not** in the body.

Zero inbound `.text` `E8`/`E9`. Image encodings of imm
`10 e3 48 00` are exactly five, each a `push 0x0048e310`:

| site | next |
| --- | --- |
| `0x0048e2cc` | already-named `CLandscapeIB__CreateIndexBuffer` → `0x0055db0a` (size `0xc`) |
| `0x0054c633` | same four-arg shape into `0x0055db0a` |
| `0x0054ced1` | same four-arg shape into `0x0055db0a` |
| `0x0056ed07` | `push 0x0056f4e0` then `0x0055dc20` (size `0xc`) |
| `0x0056ef55` | same `0x0056f4e0` / `0x0055dc20` shape |

Those caller bodies are **not** claimed.

If `[this+8]` is live: `push` it, `mov ecx, 0x009c3df0`,
`call 0x00549220`, then `[this+8] = 0`. Else skip to the store.
`EAX` is not contracted. Authored names are **not** claimed.

Cheapest falsifier: file `0x0008e310` is not
`56 8b f1 8b 46 08 85 c0`, **or** `0x0008e32d` is not `c3`,
**or** body SHA-256 is not `21c3329c…4554`, **or**
`tools/call_xref_scan.py` on `0x0048e310` is not empty, **or**
`0x0008e31b` is not `b9 f0 3d 9c 00`, **or** `0x0008e325` is
not `c7 46 08 00 00 00 00`, **or** `0x0008e2cc` is not
`68 10 e3 48 00`, **or** the image contains a sixth
`10 e3 48 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e310` | `CLandscapeTexture__FreeTexture` | `568bf1 8b4608 85c0 740b 50 b9f03d9c00 e8fbae0b00 c7460800000000 5e c3` | thiscall; bare ret; 30 B; 1 E8 `0x00549220` / 0 E9; 0 inbound; five `push` sites; Free `[+8]` via `0x009c3df0` then store 0. HIGH on ABI, inbound-empty, those five pushes, that slot. **Not** on Free body or authored names. |
