# CLandscapeTexture__Init

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Mode-word meaning and callee bodies are **not** this proof.

> Address: `0x0048e4d0`

## Contract

`thiscall`. `ECX`→`ESI` at `0x0048e4d6`. Two stack args (`ret 8`
at `0x0048e5ef`). Body `0x0048e4d0`–`0x0048e5f1` is 290 bytes,
SHA-256
`9d436082cd09bc1ede9bd8ba421bde9979cb53ae68361ff7eff009bd48c8f398`.
Two `E8`: `0x005490e0` then `CUMTexture__ConfigureByMode`
`0x004f7ab0` (`e8 f4 94 06 00` at `0x0048e5b7`). Zero `E9`.
Callee bodies are **not** claimed.

Arg0 is stored at `[this+0x34]` (`89 7e 34` at `0x0048e4db`).
Arg1 is stored at `[this+0x30]` (`89 46 30` at `0x0048e54c`).
If arg0 `<= 4`, `jmp [arg0*4+0x0048e5f4]`. That table is five
dwords immediately after the `8b ff` align: `0x0048e4e7` /
`0x0048e4f5` / `0x0048e503` / `0x0048e511` / `0x0048e51f`. Each
arm writes `[+0x48]` / `[+0x4a]` then joins `0x0048e52b`. Also
writes `+0x38` / `+0x3c` / `+0x40` / `+0x44`. Authored names
are **not** claimed.

Two inbound `.text` `E8`, zero `E9`: `0x00544879` inside
`CDXLandscape__CreateMipLevels` and `0x00544bae` inside
`CDXLandscape__Init`. Caller bodies are **not** claimed.

Cheapest falsifier: file `0x0008e4d0` is not
`56 57 8b 7c 24 0c 8b f1`, **or** `0x0008e5ef` is not
`c2 08 00`, **or** body SHA-256 is not `9d436082…f398`, **or**
`tools/call_xref_scan.py` on `0x0048e4d0` is not exactly `E8` at
`0x00544879` / `0x00544bae`, **or** `0x0008e4db` is not
`89 7e 34`, **or** `0x0008e5b7` is not `e8 f4 94 06 00`, **or**
`0x0008e5f4` is not `e7 e4 48 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e4d0` | `CLandscapeTexture__Init` | `5657 8b7c240c 8bf1 89 7e34 … ff24bdf4e54800 … e8f4940600 … c20800` | thiscall; ret 8; 290 B; 2 E8 / 0 E9; 2 inbound; writes `[+0x34]`/`[+0x30]`. HIGH on ABI, inbound set, those two stores, the five JT dwords, the ConfigureByMode plant. **Not** on mode-word meaning, alloc algebra, or callee bodies. |
