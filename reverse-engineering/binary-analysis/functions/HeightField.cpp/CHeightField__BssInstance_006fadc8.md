# CHeightField BSS instance at 0x006fadc8

Status: active static function note
Last updated: 2026-08-19
Summary: `0x006fadc8` is one BSS blob, not a pointer slot. 167 image
copies of the immediate are all `mov ecx`. Ctor installs no vtable.
`[+0x1028]` is a heap word-grid pointer; `[+0x102c]` is a float scale.
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` after
`t_2743a32e`. The Ghidra database was not opened. Table names are
labels. Occupancy only; no authored class promotion.

> Address: `0x0047e870`

## Contract

`0x006fadc8` sits in the uninitialised tail of `.data` (BSS).
`pe_read_va` refuses it. There is no `.?AVCHeightField` or
`.?AVCStaticShadows` string in the image.

Every image encoding of imm `0x006fadc8` is `b9 c8 ad 6f 00`
(`mov ecx, 0x006fadc8`). Count **167**. Zero `push`, zero
`mov [abs]`, zero non-`b9`.

Construction: dword `0x0062242c` = `0x00490a10` (`FUN_00490a10`).
That wrapper is `mov ecx, 0x006fadc8` / `call 0x00490e10`
(`CHeightField__Constructor`) / `push 0x00490a30` / atexit.
`0x00490e10` forwards to `0x0047e870`
(`CHeightField__ResetCoreBuffersAndFlags`):

```
8b d1 57 b9 00 04 00 00 33 c0 8d 7a 28 … 89 82 28 10 00 00
```

`rep stosd` 0x400 dwords at `this+0x28`, then
`mov [edx+0x1028], eax` with EAX=0. **No vtable store.**

`[+0x1028]` is a pointer: sample bodies `mov r32, [this+0x1028]`
then a word load. Load overlays `push 1; push 0x13dc; push edi`
at `0x0047f7d2`. `[+0x102c]` is a float: `fmul [ecx+0x102c]` at
`0x0047ec3f`. No this-relative store of `+0x102c` was claimed here.

This is the shared `this` of `0x0047eb00` / `0x0047eb80` /
`0x0047ec60` / `0x00490a40`. Did not pile `CMonitor.cpp.md`.

Cheapest falsifier: file `0x0007e870` is not
`8b d1 57 b9 00 04 00 00 33 c0 8d 7a 28`, **or** `0x0007e88d` is
not `89 82 28 10 00 00`, **or** `0x00090a10` is not
`b9 c8 ad 6f 00 e8 f6 03 00 00 68 30 0a 49 00 e8 82 d5 0c 00 59 c3`,
**or** file `0x0022242c` is not `10 0a 49 00`, **or**
`operand_scan` of `0x006fadc8` is not 167 `mov ecx` with 0 non-`b9`,
**or** the image contains `.?AVCHeightField`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0047e870` | `CHeightField__ResetCoreBuffersAndFlags` | `8bd157 b900040000 33c0 8d7a28 … 898228100000` | zeros `+0x28` grid and `[+0x1028]`; no vtable. HIGH. |
| `0x00490a10` | `FUN_00490a10` | `b9c8ad6f00 e8f6030000 68300a4900 … c3` | CRT dyninit: this-load, ctor, atexit. HIGH. |
| `0x00490e10` | `CHeightField__Constructor` | `56 8b f1 e8 58 da fe ff 8b c6 5e c3` | `call 0x0047e870`; EAX=this. HIGH. |
