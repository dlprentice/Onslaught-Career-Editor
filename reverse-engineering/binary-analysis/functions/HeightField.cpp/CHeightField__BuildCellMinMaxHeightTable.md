# CHeightField__BuildCellMinMaxHeightTable

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. The Ghidra
database was not opened. Table name is a research label.

> Address: `0x00490e30`

## Contract

`thiscall`. Zero stack args. `ECX` is this (parked, then recovered as
`[esp+0x1c]` after four pushes). Bare `ret` (`c3`) at `0x00490f09`.
Body `0x00490e30`–`0x00490f09` is 218 bytes, SHA-256
`758092cf50cf6aa9568b424a6011fde4856f24c06d7877ffaa1f28fced3864c7`.
One body `E8`: `0x0047ea20` (`CHeightField__GetHeightSamplePacked16`)
at `0x00490e79`. Zero `E9`.

One inbound `E8`, at `0x0046d244` inside `CGame__PostLoadProcess`:

```
mov  ecx, 0x006fadc8
call 0x00490e30
```

So this is the shared BSS instance already pinned on Load / sample.

The body walks a 0x200×0x200 grid in 8-wide cells. Each cell samples
a 9×9 window of packed words via `0x0047ea20` (`EDX` = `esi+ebp`,
stack = `eax+[esp+0x18]`, `ECX` = this). Word min starts at `0x7fff`;
word max starts at `0xffff8000` and is compared as `AX`. After the
window:

```
fld   [this+0x102c]
fimul sign-extended max
fstp  [cursor]
fld   [this+0x102c]
fimul sign-extended min
fstp  [cursor+4]
```

`cursor` starts at `this+0x13dc` and advances 8 bytes per cell.
Authored cell-size names and what the table is *for* are **not**
claimed. `0x0047ea20` first gates stay on that body.

Cheapest falsifier: file `0x00090e30` is not `83 ec 14 53 89 4c 24 10`,
**or** `0x00090f09` is not `c3`, **or** body SHA-256 is not
`758092cf…64c7`, **or** `tools/call_xref_scan.py` on `0x00490e30` is
not exactly `E8` at `0x0046d244`, **or** `0x0006d23f` is not
`b9 c8 ad 6f 00 e8 e7 3b 02 00`, **or** `0x00090eb8` is not
`d9 81 2c 10 00 00`, **or** `0x00090e39` is not `81 c1 dc 13 00 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00490e30` | `CHeightField__BuildCellMinMaxHeightTable` | `83ec14 53 894c2410 55 81c1dc130000 … d9812c100000 da4c2414 … c3` | thiscall; bare ret; this=`0x006fadc8`; writes float pairs at `+0x13dc` as word-max/min × `[+0x102c]`. HIGH on ABI, inbound, dest, scale. Not on authored names. |
