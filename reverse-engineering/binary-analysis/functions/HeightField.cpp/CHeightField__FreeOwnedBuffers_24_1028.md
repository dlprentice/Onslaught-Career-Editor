# CHeightField__FreeOwnedBuffers_24_1028

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label.

> Address: `0x0047e8a0`

## Contract

`thiscall`. Zero stack args. `ECX`→`ESI`. One bare `ret` (`c3`) at
`0x0047e8dc`. Body `0x0047e8a0`–`0x0047e8dc` is 61 bytes, SHA-256
`3520b38adab136cb31a708e4413ce3e0d505c1097417c77806039fac835de511`.
Two `E8`, both `CDXMemoryManager__Free` (`0x00549220`) with
`ecx = 0x009c3df0`. Zero `E9`.

If `[this+0x24]` is live: `push` that pointer, Free, then
`[this+0x24] = 0`. If `[this+0x1028]` is live: same, then
`[this+0x1028] = 0`. Null slots are skipped. Who first writes those
pointers is **not** claimed.

Two inbound `.text` rel32s:

| kind | site | owner (table label) |
| --- | --- | --- |
| `E9` | `0x00490e20` | `CHeightField__FreeOwnedBuffers_Thunk` (`e9 7b da fe ff`) |
| `E8` | `0x00490f40` | `CHeightField__ShutdownAndDestroyMixerMap` |

Thunk inbound is one `E9` at `0x00490a35`. That wrapper is the
already-pinned atexit slot `0x00490a30`:

```
mov  ecx, 0x006fadc8
jmp  0x00490e20
```

Shutdown inbound is one `E8` at `0x0046ca0e`. The site loads the same
this first:

```
mov  ecx, 0x006fadc8
call 0x00490f40
```

`0x00490f40` is `call 0x0047e8a0` / `mov ecx, 0x0089bd80` /
`jmp 0x00523230`. The mixer tail is **not** claimed.

So both live paths free the BSS instance. File `0x00090a30` is
`b9 c8 ad 6f 00 e9 e6 03 00 00`. File `0x0006ca09` is
`b9 c8 ad 6f 00 e8 2d 45 02 00`.

Cheapest falsifier: file `0x0007e8a0` is not `56 8b f1 8b 46 24`,
**or** `0x0007e8dc` is not `c3`, **or** body SHA-256 is not
`3520b38a…e511`, **or** `tools/call_xref_scan.py` on `0x0047e8a0` is
not exactly `E9` at `0x00490e20` and `E8` at `0x00490f40`, **or**
`0x00090a30` is not `b9 c8 ad 6f 00 e9 e6 03 00 00`, **or**
`0x0006ca09` is not `b9 c8 ad 6f 00 e8 2d 45 02 00`, **or**
`0x0007e8b5` is not `c7 46 24 00 00 00 00`, **or** `0x0007e8d1` is
not `c7 86 28 10 00 00 00 00 00 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0047e8a0` | `CHeightField__FreeOwnedBuffers_24_1028` | `568bf1 8b4624 85c0 7412 50 b9f03d9c00 e8… c7462400000000 … c7862810000000000000 5e c3` | thiscall; bare ret; Free `[+0x24]` then `[+0x1028]` via `0x009c3df0`; both inbound this=`0x006fadc8`. HIGH on ABI, inbound set, both frees, both this-loads. **Not** on pointer producers or mixer tail. |
