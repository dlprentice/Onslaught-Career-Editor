# CUMTexture__ConfigureByMode

Status: active static function note
Last updated: 2026-08-19
Source File: UMTexture.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Mode names and the `[vtable+8]` bodies are **not** this proof.

> Address: `0x004f7ab0`

## Contract

`thiscall`. Incoming `ECX` is used as `this` (no save). Three
stack args (`ret 0xc` at five exits: `0x004f7ade` / `0x004f7af8`
/ `0x004f7b1a` / `0x004f7b38` / `0x004f7b56`). Body
`0x004f7ab0`–`0x004f7b58` is 169 bytes, SHA-256
`7ff68fc8b3fa0bcd4088145e7834724d76b77d4da94ee69ab59017c57c6787f3`.
Zero `E8` / zero `E9`. The seven `nop`s at `0x004f7b59` are
**not** in the body.

Stores arg0 at `[this+0x14]` (`89 41 14` at `0x004f7ab8`) and
arg2 at `[this+0x18]` (`89 51 18` at `0x004f7abf`). Arg1 is
compared to `0` / `3` / `1` / `4` / `5` and writes `+0xc` /
`+0x10` / `+0x1c` before `call [vtable+8]`. Authored mode names
are **not** claimed.

Four inbound `.text` `E8`, zero `E9`: already-pinned Init
`0x0048e5b7`, `CLandscapeTexture__VFunc_1_0048e670` `0x0048e77c`,
`CDXFrontEndVideo__InitVideo` `0x00541603`, `CDXShadows__Init`
`0x005521b8`. Caller bodies other than the Init plant
(`6a 01 6a 01 50 8b ce e8`) are **not** claimed.

Cheapest falsifier: file `0x000f7ab0` is not
`8b 44 24 04 8b 54 24 0c`, **or** `0x000f7b56` is not
`c2 0c 00`, **or** body SHA-256 is not `7ff68fc8…87f3`, **or**
`tools/call_xref_scan.py` on `0x004f7ab0` is not exactly `E8` at
`0x0048e5b7` / `0x0048e77c` / `0x00541603` / `0x005521b8`, **or**
`0x000f7ab8` is not `89 41 14`, **or** `0x000f7abf` is not
`89 51 18`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004f7ab0` | `CUMTexture__ConfigureByMode` | `8b442404 8b54240c 894114 8b442408 895118 … c20c00` | thiscall; ret 0xc ×5; 169 B; 0 E8/E9; 4 inbound; writes `[+0x14]`/`[+0x18]`. HIGH on ABI, inbound set, those two stores, the five arg1 compares. **Not** on mode names or `[vtable+8]`. |
