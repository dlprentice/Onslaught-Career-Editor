# CLandscapeTexture__Constructor

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Installed vptr COL names `.?AVCLandscapeIB@@`. That is **not**
a live rename. Callee `0x00488210` body is **not** this proof.

> Address: `0x0048e330`

## Contract

`thiscall`. `ECX`→`ESI`. Zero stack args. Bare `ret` at
`0x0048e348`. Body `0x0048e330`–`0x0048e348` is 25 bytes,
SHA-256
`36377d473d6e83fefbd2a00a877abdef843e000eec9e1adf7cf52f09aab1708b`.
One `E8` (`0x0048e333` → table `CIBuffer__Constructor`
`0x00488210`). Zero `E9`. Four `nop`s after the `ret` are **not**
in the body.

Zero inbound `.text` `E8`/`E9`. Unique image copy of imm
`30 e3 48 00` is `push 0x0048e330` at `0x0055061c` inside
already-named `CDXPatchManager__Init` (`0x00550430`), paired with
`push 0x0048e350` at `0x00550617` then
`eh_vector_constructor_iterator` `0x0055dc20`. That Init body is
**not** claimed.

After the base call: `[this] = 0x005dc1d8` (unique image dword
`d8 c1 5d 00`) and `[this+0x2c] = 0`. `EAX` is `this`.
`[0x005dc1d8-4] = 0x00614830`; that COL `+0x0c` is type
descriptor `0x0062d848` whose name at `+8` is
`.?AVCLandscapeIB@@` (file `0x0022d850`). Slot 0 of that vptr is
already-named `CLandscapeIB__VFunc_0_00550680`. Already-pinned
CLandscapeTexture slots live at the **next** vptr `0x005dc1f0`
(COL `.?AVCLandscapeTexture@@`). Authored rename is **not**
claimed.

Cheapest falsifier: file `0x0008e330` is not
`56 8b f1 e8 d8 9e ff ff`, **or** `0x0008e348` is not `c3`,
**or** body SHA-256 is not `36377d47…708b`, **or**
`tools/call_xref_scan.py` on `0x0048e330` is not empty, **or**
`0x0008e338` is not `c7 06 d8 c1 5d 00`, **or** `0x0008e33e`
is not `c7 46 2c 00 00 00 00`, **or** `0x001dc1d4` is not
`30 48 61 00`, **or** `0x0022d850` is not
`2e 3f 41 56 43 4c 61 6e 64 73 63 61 70 65 49 42 40 40 00`,
**or** the image contains a second `d8 c1 5d 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e330` | `CLandscapeTexture__Constructor` | `568bf1 e8d89effff c706d8c15d00 c7462c00000000 8bc6 5e c3` | thiscall; bare ret; 25 B; 1 E8 `0x00488210` / 0 E9; 0 inbound; unique vptr `0x005dc1d8`; COL `.?AVCLandscapeIB@@`; zeros `[+0x2c]`; EAX=this. HIGH on ABI, that plant, that store, that COL string. **Not** on callee body, Init algebra, or a rename. |
