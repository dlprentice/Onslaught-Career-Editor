# CScriptObjectCode__Push

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
name is a research label. Callee body `0x00441740` and
`CScriptObjectCode.cpp.md` / the CallEvent /
CallEventDirect / opcode folders were **not** written.

> Address: `0x00539420`

## Contract

`thiscall`. First insn `push esi` / `mov esi, ecx`. One
stack dword. One `ret 4` at `0x00539466`. Body
`0x00539420`–`0x00539468` is 73 bytes, SHA-256
`99b129088b9aa21dc70f4852770122ade7419cd58281983d04900fa7624502de`.
One `E8`, zero `E9`. Seven `nop`s after the `ret 4` are
**not** in the body (neighbour `CScriptObjectCode__Pop`
starts at `0x00539470`).

`[esi + [esi+0x200]*4] = arg0`, then `++[esi+0x200]`. If
the new depth `> 0x80` (128) the body `push 0x00650078`
(`FATAL ERROR: Stack out of memory`) / `push 0x0066f580`
and `E8`s table `CConsole__Printf` `0x00441740`
(`0x00539450`, `add esp, 8`), then `--[esi+0x200]` (the
overflowing store is rejected). That callee body is **not**
this proof.

Twenty-one inbound `.text` `E8`, zero `E9`. Already-pinned
fire-path sites: `0x00539a46` (`CScriptObjectCode__CallEvent`)
and `0x00539abd` (`CScriptObjectCode__CallEventDirect`).
The other nineteen sit in the instruction-opcode band
`0x0052e0d0`–`0x0052ec2a` and are **not** claimed. Full
`tools/call_xref_scan.py` set:

`0x0052e0d0` `0x0052e0e0` `0x0052e15a` `0x0052e16a`
`0x0052e1bf` `0x0052e20f` `0x0052e25f` `0x0052e2af`
`0x0052e2dd` `0x0052e3fa` `0x0052e554` `0x0052e604`
`0x0052e6aa` `0x0052e74a` `0x0052e7ea` `0x0052e88a`
`0x0052e92a` `0x0052eae2` `0x0052ec2a` `0x00539a46`
`0x00539abd`.

Zero image encodings of imm `20 94 53 00`.

Cheapest falsifier: file `0x00139420` is not `56 8b f1`,
**or** `0x00139466` is not `c2 04 00`, **or** body SHA-256
is not `99b12908…02de`, **or** `tools/call_xref_scan.py` on
`0x00539420` is not the twenty-one `E8` above, **or**
`0x0013943f` is not `3d 80 00 00 00`, **or**
`0x00139450` is not `e8 eb 82 f0 ff`, **or** a twenty-second
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539420` | `CScriptObjectCode__Push` | `56 8bf1 8b4c2408 8b8600020000 890c86 … 3d80000000 7e1f 6878006500 … e8eb82f0ff … 48 898600020000 5e c20400` | thiscall; ret 4; 73 B; 1 E8 Printf; 0 E9; 21 inbound E8. HIGH on ABI, inbound count, 128-slot ceiling, overflow reject. **Not** on Printf or the 19 opcode hosts. |
