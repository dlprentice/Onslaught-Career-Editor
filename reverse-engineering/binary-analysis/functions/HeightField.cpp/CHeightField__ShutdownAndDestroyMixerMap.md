# CHeightField__ShutdownAndDestroyMixerMap

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

> Address: `0x00490f40`

## Contract

`thiscall`. Zero stack args. `ECX` is this for the first call only.
Body `0x00490f40`–`0x00490f4e` is 15 bytes, SHA-256
`aef3d7ab0d2b073954461343f78dfe2e98fd31fe9b1e28ddd54597c8e6fb7dc7`.
One `E8`, one tail `E9`. No local `ret`: the tail is a jump.

```
call 0x0047e8a0
mov  ecx, 0x0089bd80
jmp  0x00523230
```

`0x0047e8a0` is the already-pinned
`CHeightField__FreeOwnedBuffers_24_1028`. `0x00523230` is the table
label `CMixerMap__Destroy`. That body is **not** claimed.

One inbound `.text` `E8`, zero inbound `E9`: `0x0046ca0e` inside
`CGame__Shutdown`. The site loads the BSS this first:

```
mov  ecx, 0x006fadc8
call 0x00490f40
```

File `0x0006ca09` is `b9 c8 ad 6f 00 e8 2d 45 02 00`.

Cheapest falsifier: file `0x00090f40` is not `e8 5b d9 fe ff`,
**or** `0x00090f45` is not `b9 80 bd 89 00`, **or** `0x00090f4a` is
not `e9 e1 22 09 00`, **or** body SHA-256 is not `aef3d7ab…7dc7`,
**or** `tools/call_xref_scan.py` on `0x00490f40` is not exactly `E8`
at `0x0046ca0e`, **or** `0x0006ca09` is not
`b9 c8 ad 6f 00 e8 2d 45 02 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00490f40` | `CHeightField__ShutdownAndDestroyMixerMap` | `e85bd9feff b980bd8900 e9e1220900` | thiscall; call FreeOwnedBuffers then `ecx=0x0089bd80` / `jmp 0x00523230`; inbound `CGame__Shutdown` `mov ecx,0x006fadc8`. HIGH on ABI, inbound, both transfers. **Not** on mixer-destroy body. |
