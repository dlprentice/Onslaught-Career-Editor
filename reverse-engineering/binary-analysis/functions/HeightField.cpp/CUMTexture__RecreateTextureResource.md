# CUMTexture__RecreateTextureResource

Status: active static function note
Last updated: 2026-08-19
Source File: UMTexture.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Device recreate algebra is **not** this proof.

> Address: `0x004f7b60`

## Contract

`thiscall`. `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x004f7bc6`. Body `0x004f7b60`–`0x004f7bc6` is 103 bytes,
SHA-256
`4d8ea055b14286a5104e6cb8423672a5fb47fee3ec1e60b9014781b9cfe9fae4`.
Three `E8` (`0x00513760`, `0x0055a0f0`, `0x00513a10`), zero `E9`.
One inbound `.text` `E8`: already-pinned Reset `0x0048e614`
(`8b f1 e8 47 95 06 00`). Callee bodies are **not** claimed.

Copies `[this+0xc]` to `[this+0x24]`; if that was 0, the first two
`E8`s refill `[+0x24]`. Then if `[+8]` live, `call [[+8]+8]` and
store 0 at `+8`. Last `E8` this is imm `0x00855bb0`. Live `EAX` is
forced to 0 when the last callee returns `>= 0`, else kept
(`setge` / `dec` / `and`). Authored names are **not** claimed.

Cheapest falsifier: file `0x000f7b60` is not
`56 8b f1 57 8b 46 0c`, **or** `0x000f7bc6` is not `c3`, **or**
body SHA-256 is not `4d8ea055…fae4`, **or**
`tools/call_xref_scan.py` on `0x004f7b60` is not exactly `E8` at
`0x0048e614`, **or** `0x0008e612` is not
`8b f1 e8 47 95 06 00`, **or** `0x000f7b69` is not `89 46 24`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x004f7b60` | `CUMTexture__RecreateTextureResource` | `568bf1 8b460c 894624 … b9b05b8500 … 0f9dc2 4a 23c2 c3` | thiscall; bare ret; 103 B; 3 E8 / 0 E9; 1 inbound Reset; writes `[+0x24]`/`[+8]`. HIGH on ABI, inbound, those slots. **Not** on callee bodies or authored names. |
