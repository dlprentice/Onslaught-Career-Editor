# CLandscapeTexture__VFunc_1_0048e670

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Device-create algebra is **not** this proof.

> Address: `0x0048e670`

## Contract

`thiscall`. `ECX`→`EBX` at `0x0048e67c`. Zero stack args. Bare
`ret` at `0x0048e786`. Body `0x0048e670`–`0x0048e786` is 279
bytes, SHA-256
`7da3b3a7fb15e7cabed1846e6ad2113b08c6c67be78af833f6db632a43519c8c`.
Three `E8`: `0x0042d080`, `0x005139a0`, already-pinned
ConfigureByMode `0x004f7ab0` (`8b cb e8 2f 93 06 00` at
`0x0048e77a`). Zero `E9`. Callee bodies other than that plant
are **not** claimed.

Zero inbound `.text` `E8`/`E9`. Unique image copy of the entry
VA is vtable slot 1 at `0x005dc1f4` (slot 0 is
`CLandscapeTexture__VFunc_0_005449a0`; slot 2 is already-pinned
Reset `0x0048e610`). Early-out if `[0x006fabf4]` is live. Join
always plants ConfigureByMode(`this`, `[0x0062d864]`, `1`, `1`).
Authored names are **not** claimed.

Cheapest falsifier: file `0x0008e670` is not
`a1 f4 ab 6f 00 83 ec 08`, **or** `0x0008e786` is not `c3`,
**or** body SHA-256 is not `7da3b3a7…9c8c`, **or**
`tools/call_xref_scan.py` on `0x0048e670` is not empty, **or**
`0x001dc1f4` is not `70 e6 48 00`, **or** `0x0008e77a` is not
`8b cb e8 2f 93 06 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e670` | `CLandscapeTexture__VFunc_1_0048e670` | `a1f4ab6f00 83ec08 85c0 5356 8bd9 … 8bcb e82f930600 … c3` | thiscall; bare ret; 279 B; 3 E8 / 0 E9; 0 inbound; vtable slot 1 at `0x005dc1f4`; plants ConfigureByMode. HIGH on ABI, inbound-empty, that slot, that plant. **Not** on device-create algebra or authored names. |
