# CLandscapeTexture__UpdateTile

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` after
`t_34e27664`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Tile / lighting algebra and callee bodies are **not** this
proof.

> Address: `0x0048ea80`

## Contract

`thiscall`. `ECX`→`ESI` at `0x0048ea95` (`8b f1`). One stack dword
(`ret 4` at `0x0048edf0`). After `sub esp, 0x20` that dword is
`[esp+0x24]`, then `and eax, 0xffff`. Body `0x0048ea80`–`0x0048edf2`
is 883 bytes, SHA-256
`cf33db9bdf5593dad0ab6a7d47059c9ebfc0d4880e69385fe9e163d6ace8a013`.
Five instruction-aligned `E8`, three internal `E9`. One `ret`.
`EAX` is not contracted. Thirteen `90` after the `ret` are outside
the body hash.

One inbound `.text` `E8`, zero `E9`: `0x0048e81e`. File `0x0008e816`
is `66 8b 45 04 8b 4d 00 50 e8 5d 02 00 00`:

```
mov  ax, word ptr [ebp+4]
mov  ecx, dword ptr [ebp]
push eax
call 0x0048ea80
```

That site sits in the table-label range
`CLandscapeTexture__FlushUpdateQueue`. Caller body is **not**
claimed. This body's this is **not** an immediate; do not collapse
it to `0x006fadc8`.

Unconditional this-write: `[esi+0x2c] = 1` at `0x0048eaa0`
(`c7 46 2c 01 00 00 00`). This-reads: `+8`, `+0x30`, `+0x34`,
`+0x3c`. Authored names are **not** claimed.

Both already-pinned blit sites reload the heightfield BSS first:

```
0048eb59  b9 c8 ad 6f 00 e8 8d 04 ff ff
0048ece9  b9 c8 ad 6f 00 e8 fd 02 ff ff
```

Other `E8` dests are `0x0048ee00` (twice) and `0x0048e950` (once).
Callee bodies stay on their own notes. A raw `E8` byte at
`0x0048eaaf` / `0x0048eab9` is mid-instruction (`c1 e8 03` /
`8b e8`); Capstone does not agree those are calls.

Cheapest falsifier: file `0x0008ea80` is not
`83 ec 20 8b 44 24 24`, **or** `0x0008edf0` is not `c2 04 00`,
**or** body SHA-256 is not `cf33db9b…a013`, **or**
`tools/call_xref_scan.py` on `0x0048ea80` is not exactly `E8` at
`0x0048e81e`, **or** `0x0008e816` is not
`66 8b 45 04 8b 4d 00 50 e8 5d 02 00 00`, **or** `0x0008ea95` is
not `8b f1`, **or** `0x0008eaa0` is not `c7 46 2c 01 00 00 00`,
**or** `0x0008eb59` is not `b9 c8 ad 6f 00 e8 8d 04 ff ff`, **or**
`0x0008ece9` is not `b9 c8 ad 6f 00 e8 fd 02 ff ff`, **or**
`0x0008eaae` is not `c1 e8 03`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048ea80` | `CLandscapeTexture__UpdateTile` | `83ec20 8b442424 … 8bf1 … c7462c01000000 … b9c8ad6f00 e88d04ffff … b9c8ad6f00 e8fd02ffff … c20400` | thiscall; ret 4; 883 B; 5 E8 / 3 internal E9; 1 inbound FlushUpdateQueue; writes `[+0x2c]=1`; two blit plants `mov ecx,0x006fadc8`. HIGH on ABI, inbound, those slots, those two plants. **Not** on tile algebra, authored names, or callee bodies. |
