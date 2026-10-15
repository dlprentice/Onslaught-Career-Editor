# CScriptObjectCode__Clone

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`)
|| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. Already-pinned `ClearSymbolTable` /
`ReadSymbolTable` / `GetInstruction` / `CScriptObjectCode.cpp.md`
/ the inbound host / the seven callee bodies were **not** written.
Sibling `t_61ed7f04` owns `CloneSymbolTable` and was **not**
stolen. Steward cycle 41 accepted GetInstruction / ReadSymbolTable
— not redone.

> Address: `0x00539040`

## Contract

`thiscall` SEH. First insn `push -1` / `push 0x005d7541` /
`fs:[0]` install. Zero stack args. One bare `ret`
(`0x00539191`). Body `0x00539040`–`0x00539191` is 338 bytes,
SHA-256
`5f6b1efdd2d25b4b8891591ed62e62db8bbae45912bb09e89117cce8a725556a`.
Seven `E8`, zero `E9`. Fourteen nops after the `ret` are
**not** in the body (neighbour table
`CMissionScriptObjectCode__dtor` starts at `0x005391a0`).

Incoming ECX (source) is parked in `EBX`. The body:

1. `E8` `0x005490e0` with `ecx = 0x009c3df0` and stack
   `0x53` / `0x00650040` / `0x76` / `0x70`. The C string at
   `0x00650040` is
   `C:\\dev\\ONSLAUGHT2\\MissionScript\\ScriptObjectCode.cpp`.
   Alloc failure zeroes `ESI` and still falls through.
2. Live dest: `E8` `0x004241a0` (`ecx = dest+4`), `E8`
   `0x004e5840` (`ecx = dest+0x48`), then stores
   `[dest] = 0x005e4f54`, `[dest+0x64] = 0`,
   `[dest+0x6c] = 0`, `[dest+0x5c] = 0`, `[dest+0x60] = 0`,
   and `rep stosd` of 13 dwords `-1` at `dest+0x14`.
3. Count-gated on `[src+0xc]`: each slot does
   `call [[slot]+4]` (indirect; not an `E8`), then `E8`
   `0x00424260` (`ecx = dest+4`).
4. Copies 13 dwords from `src+0x14` onto `dest+0x14`.
5. `E8` `0x005395b0` with `ecx = [src+0x58]`; stores
   `EAX` to `[dest+0x58]`. That callee body is **not**
   this proof.
6. Walks `[src+0x48]` with `E8` `0x0052fbb0` then `E8`
   `0x004e5b20` (`ecx = dest+0x48`). The walk writes
   `[src+0x50]`.
7. Copies `[src+0x6c]` / `[src+0x60]` / `[src+0x5c]` /
   `[src+0x64]` onto dest. `EAX = dest` at the `ret`.

Those seven callee bodies, the `[slot]+4` vtable slot, and
the `0x009c3df0` object are **not** this proof.

Seven body `E8` sites: `0x0053906c` `0x005490e0`,
`0x0053908c` `0x004241a0`, `0x00539099` `0x004e5840`,
`0x005390e7` `0x00424260`, `0x0053911d` `0x005395b0`,
`0x0053913f` `0x0052fbb0`, `0x00539147` `0x004e5b20`.

One inbound `.text` `E8`, zero `E9`: `0x0050ac5a` inside
table `CWorld__CloneScriptObjectCodeByName` (not claimed).
That host plants `ecx = [edi+4]`. Zero image encodings of
imm `40 90 53 00`.

Cheapest falsifier: file `0x00139040` is not `6a ff`,
**or** `0x00139191` is not `c3`, **or** body SHA-256 is not
`5f6b1efd…556a`, **or** `tools/call_xref_scan.py` on
`0x00539040` is not the one `E8` above, **or**
`0x0013911d` is not `e8 8e 04 00 00`, **or** `0x001390a9`
is not `c7 06 54 4f 5e 00`, **or** a second inbound
`E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539040` | `CScriptObjectCode__Clone` | `6aff 6841755d00 64a100000000 50 64892500000000 51 … 8bc6 5e5d5b 64890d00000000 83c410 c3` | thiscall SEH; bare ret ×1; 338 B; 7 E8 / 0 E9; 1 inbound E8. HIGH on ABI, inbound set, 0x70 alloc, vptr imm, `EAX=dest`. **Not** on callee bodies (incl. `0x005395b0`) or the host. |
