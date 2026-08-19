# CScriptObjectCode__RestoreStack

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`)
| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. Already-pinned `ClearStack` /
`CScriptObjectCode.cpp.md` / CopyState were **not** written.

> Address: `0x00539350`

## Contract

`thiscall`. First insn `push esi` / `mov esi, ecx`. One
stack dword (source head). Two `ret 4` sites
(`0x005393c0` after the copy, `0x005393d1` when source
depth `<= 0`). Body `0x00539350`–`0x005393d3` is 132
bytes, SHA-256
`874c50976e660bee9fecf97a8fdcdf5c63608f8c96ec1d6817b04fda58e199e0`.
Zero `E8`, zero `E9`. Nops after the last `ret 4` are
**not** in the body (already-pinned neighbour
`CScriptObjectCode__ClearStack` starts at `0x005393e0`).

Incoming ECX is the destination head. The body first
drains dest top-down (`elem = [esi + depth*4 - 4]`; if
live, `push 1` / `call [vtable+0]`; `--depth`) — the same
shape as ClearStack, inlined. Then
`[dest+0x200] = [src+0x200]`. If that count `> 0` it
copies each dword `[src + i*4] → [dest + i*4]` (a
**shallow move** of the pointer array). Both exits store
`[src+0x200] = 0` and return `EAX = dest`. Slot-0 bodies
are **not** this proof.

One inbound `.text` `E8`, zero `E9`: `0x00539931` inside
table `CScriptObjectCode__CopyState` (not claimed). Zero
image encodings of imm `50 93 53 00`.

Cheapest falsifier: file `0x00139350` is not `56 8b f1`,
**or** `0x001393d1` is not `c2 04 00`, **or** body
SHA-256 is not `874c5097…99e0`, **or**
`tools/call_xref_scan.py` on `0x00539350` is not the one
`E8` above, **or** `0x00139364` is not `8b 4c 86 fc`,
**or** `0x001393b1` is not `c7 87 00 02 00 00 00 00 00 00`,
**or** a second inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539350` | `CScriptObjectCode__RestoreStack` | `56 8bf1 57 8b8600020000 85c0 7423 … 8b4c86fc … 6a01 ff12 … 8b7c240c … 8928 … c7870002000000000000 … c20400` | thiscall; ret 4 ×2; 132 B; 0 E8/E9; 1 inbound E8. HIGH on ABI, inbound set, dest drain, shallow pointer move, source depth 0. **Not** on slot-0 or CopyState. |
