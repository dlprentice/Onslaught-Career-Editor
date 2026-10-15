# CLandscapeTexture__CopyTileToTexture

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Tile-copy algebra is **not** this proof.

> Address: `0x0048e950`

## Contract

`thiscall`. `ECX`→`EBP` at `0x0048e955` (`8b e9`), parked at
`[esp+0x10]`. One stack dword (`ret 4` at `0x0048ea5d` and
`0x0048ea74`). Body `0x0048e950`–`0x0048ea76` is 295 bytes,
SHA-256
`1369a53918733570d53ee340700ebea8d66095464468e0d568ed9d49a29e3684`.
Zero `E8` / `E9`. Two indirect calls: `[ecx+0x4c]` at
`0x0048e9b6` and `[eax/edx+0x50]` at `0x0048ea53` /
`0x0048ea6a`. 111 instructions, no gap.

Two inbound `.text` `E8`, zero `E9` — the already-pinned
UpdateTile / UpdateTileRange sites.

This-read: `+8` at `0x0048e99b` / `0x0048ea4b` (`8b 45 08`).
**No** this-write. Absolutes `[0x006fabf0]` / `[0x006fabcc]` /
`[0x006fabf4]` and `lea … [eax*2 + 0x0067a7d8]` are loads, not
this slots. Authored names are **not** claimed.

Cheapest falsifier: file `0x0008e950` is not
`83 ec 1c 53 55 8b e9`, **or** `0x0008ea74` is not `c2 04 00`,
**or** body SHA-256 is not `1369a539…3684`, **or**
`tools/call_xref_scan.py` on `0x0048e950` is not exactly `E8` at
`0x0048ec1e` / `0x0048f128`, **or** `0x0008ec1b` is not
`8b ce 52 e8 2d fd ff ff`, **or** `0x0008f125` is not
`8b cf 50 e8 23 f8 ff ff`, **or** `0x0008e955` is not `8b e9`,
**or** `0x0008e99b` is not `8b 45 08`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e950` | `CLandscapeTexture__CopyTileToTexture` | `83ec1c 5355 8be9 … 8b4508 … c20400` | thiscall; ret 4 ×2; 295 B; 0 E8/E9; 2 inbound UpdateTile/Range; reads `[+8]`. HIGH on ABI, inbound, that slot. **Not** on tile-copy algebra or authored names. |
