# CScriptObjectCode__ClearSymbolTable

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`
or `Symtab.cpp.md`)
|| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. Already-pinned `ReadSymbolTable` /
`GetInstruction` / `CScriptObjectCode.cpp.md` / `Symtab.cpp.md` /
the inbound dtor / the three callee bodies were **not** written.
Sibling `t_61ed7f04` owns `CloneSymbolTable` and was **not** stolen.

> Address: `0x00539510`

## Contract

`thiscall` SEH. First insn `push -1` / `push 0x005d7580` /
`fs:[0]` install. Zero stack args. One bare `ret`
(`0x005395ab`). Body `0x00539510`–`0x005395ab` is 156 bytes,
SHA-256
`9edfbd2f987d2787d6dae35a3eb9021f974ab9a10d47d17f3a741f6f6077ba32`.
Three `E8`, zero `E9`. Four nops after the `ret` are **not**
in the body (neighbour table
`CScriptObjectCode__CloneSymbolTable` starts at `0x005395b0`).

Incoming ECX is parked in `EBP`. `[this+8]` is the loop count.
`jle` `0x0053958c` skips the row loop when that count is
`<= 0`. Each live slot is `esi = [[this] + edi*4]`. A null
slot is skipped. A live slot:

1. If `[esi+8] != 0`, `push 1` / `call [[esi+8]]` (indirect;
   not an `E8`).
2. `E8` `0x0052f740` with `ecx = esi`.
3. `E8` `0x00549220` with `ecx = 0x009c3df0` and the row
   pushed.
4. `[[this] + edi*4] = 0`.

After the loop (and on the count `<= 0` path): `E8`
`0x00465570` with `ecx = this`. Those three callee bodies,
the `[esi+8]` vtable slot, and the `0x009c3df0` object are
**not** this proof. `EAX` at the `ret` is whatever the last
callee left.

Three body `E8` sites: `0x00539569` `0x0052f740`,
`0x00539574` `0x00549220`, `0x00539596` `0x00465570`.

One inbound `.text` `E8`, zero `E9`: `0x0053924e` inside
table `CMissionScriptObjectCode__dtor` (not claimed). That
host does `ebp = [esi+0x58]`; null skips; else `ecx = ebp`
then this call, then Free of the same pointer, then
`[esi+0x58] = 0`. Zero image encodings of imm
`10 95 53 00`.

Cheapest falsifier: file `0x00139510` is not `6a ff`,
**or** `0x001395ab` is not `c3`, **or** body SHA-256 is not
`9edfbd2f…ba32`, **or** `tools/call_xref_scan.py` on
`0x00539510` is not the one `E8` above, **or**
`0x00139569` is not `e8 d2 61 ff ff`, **or** `0x00139596`
is not `e8 d5 bf f2 ff`, **or** a second inbound `E8`/`E9`
exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539510` | `CScriptObjectCode__ClearSymbolTable` | `6aff 6880755d00 64a100000000 50 64892500000000 83ec08 … 8b4c2410 5f5d 64890d00000000 83c414 c3` | thiscall SEH; bare ret ×1; 156 B; 3 E8 / 0 E9; 1 inbound E8. HIGH on ABI, inbound set, count-gated `[[this]+i*4]` drain then `E8` `0x00465570`. **Not** on callee bodies, `[row+8]` class, or the dtor. |
