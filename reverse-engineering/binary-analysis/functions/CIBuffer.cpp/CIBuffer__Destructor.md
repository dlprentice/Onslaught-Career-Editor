# CIBuffer__Destructor

Status: active static function note
Last updated: 2026-08-19
Source File: IBuffer.cpp / DX (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Callee bodies `0x00512cc0` / `0x00549220` / `0x00512d50` are
**not** this proof.

> Address: `0x00488290`

## Contract

`thiscall` with an SEH frame (`push -1` / `0x005d2dd8` /
`fs:[0]`). `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x00488324`. Body `0x00488290`–`0x00488324` is 149 bytes,
SHA-256
`f3eda241a7f9d7ad2305af2cba96f6f2e71936f608c9cd2bcc7d5891df6c38c1`.
Three `E8` (`0x004882c0` → table
`CShaderBase__UnlinkFromRenderObjectLists` `0x00512cc0`,
`ecx = 0x00855bb0`, arg `this`; `0x004882fd` → already-named
`CDXMemoryManager__Free` `0x00549220`; `0x0048830f` → table
`DeviceObject__dtor_body` `0x00512d50`, `ecx = this`). Zero
`E9`. Four `nop`s after the `ret` are **not** in the body.

Two inbound `.text` transfers, zero extra `E8`/`E9`:

| site | host (label only) |
| --- | --- |
| `0x00488273` | table `CIBuffer__ScalarDeletingDestructor` (`E8`) |
| `0x0048e350` | table `CIBuffer__Destructor_thunk` (`E9`; five bytes `e9 3b 9f ff ff`) |

Zero image encodings of imm `90 82 48 00`. Those two hosts are
**not** claimed beyond that transfer.

`edi` is 0. Stores `[this] = 0x005dbec4` (same vptr as the
already-pinned constructor; imm `c4 be 5d 00` still occurs
exactly twice: constructor `0x0008823c` and here `0x000882b0`).
Then:

- call table `0x00512cc0` with `ecx = 0x00855bb0` and arg `this`
- if `[this+0x18]` is 0 or 1 and `[this+8]` is live: `[vtable+8]`
  on that pointer, then `[this+8] = 0`. Any other `[this+0x18]`
  skips that arm and leaves `[this+8]`
- if `[this+0x1c]` is live: `push` it, `mov ecx, 0x009c3df0`,
  `call 0x00549220`, then `[this+0x1c] = 0`
- `mov ecx, this` and call table `0x00512d50`

`EAX` is not contracted. Authored names of `[+0x18]` and
`[vtable+8]` are **not** claimed.

Cheapest falsifier: file `0x00088290` is not
`6a ff 68 d8 2d 5d 00`, **or** `0x00088324` is not `c3`,
**or** body SHA-256 is not `f3eda241…38c1`, **or**
`tools/call_xref_scan.py` on `0x00488290` is not the two
transfers above, **or** `0x000882ae` is not
`c7 06 c4 be 5d 00`, **or** `0x000882b7` is not
`b9 b0 5b 85 00`, **or** `0x000882c8` is not `83 f8 01`,
**or** `0x000882f8` is not `b9 f0 3d 9c 00`, **or**
`0x0008e350` is not `e9 3b 9f ff ff`, **or** the image
contains a third `c4 be 5d 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00488290` | `CIBuffer__Destructor` | `6aff 68d82d5d00 … c706c4be5d00 … e8fba90800 … 8b4618 83f801 … e81e0f0c00 … e83caa0800 … c3` | thiscall; SEH; bare ret; 149 B; 3 E8 `0x00512cc0` / `0x00549220` / `0x00512d50` / 0 E9; 2 inbound (E8 `0x00488273`, E9 `0x0048e350`); same vptr `0x005dbec4`; +0x18 in {0,1} then `[+8]` `[vtable+8]` and store 0; Free `[+0x1c]` via `0x009c3df0`. HIGH on ABI, inbound set, those stores, those compares. **Not** on callee bodies or authored slot names. |
