# CScriptObjectCode__ReadSymbolTable

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
name is a research label. Already-pinned `GetInstruction` /
`InitRuntime` / `CScriptObjectCode.cpp.md` / `Symtab.cpp.md` /
the inbound ctor / the six callee bodies were **not** written.

> Address: `0x00539770`

## Contract

`thiscall` SEH. First insn `push -1` / `push 0x005d75f9` /
`fs:[0]` install. One stack dword (the `CDXMemBuffer*`).
One `ret 4` site (`0x00539890`). Body `0x00539770`–
`0x00539892` is 291 bytes, SHA-256
`befb8eb8879c2749d776a6208edf7075191ff4a5c368cc1ad5d93290a1289a9f`.
Eleven `E8`, zero `E9`. Thirteen nops after the `ret 4` are
**not** in the body (table `FUN_005398a0` starts at
`0x005398a0`).

Incoming ECX is parked in `EBP`. The stack arg is parked in
`EDI`. `EAX = this` at the `ret`. The body:

1. `E8` `0x004241a0` with `ecx = this`, stack dwords
   `[0x005db5f8]` (value `0x10`) then `1`.
2. `E8` `0x00548570` reads 4 bytes into a local count.
   `jle` `0x00539870` skips the row loop when that count
   is `<= 0`.
3. Each row: `E8` `0x005490e0` alloc `0x18` (push
   `0x121` / `0x00650134` / `0x18` / `0x18`;
   `ecx = 0x009c3df0`). The C string at `0x00650134` is
   `C:\dev\ONSLAUGHT2\MissionScript\Symtab.cpp`. Alloc
   failure zeroes `ESI` and still falls into the append.
4. Live row: `E8` `0x0052f790` (`ecx = row`, arg =
   buffer). Then `E8` `0x00548570` reads 4 bytes; if that
   dword is 0, `[row+8] = 0`, else cdecl `E8` `0x0052ec60`
   (`add esp, 8`) and `[row+8] = EAX`. Then three more
   `E8` `0x00548570` into `[row+0xc]`, `[row+0x10]`,
   `[row+0x14]`.
5. `E8` `0x004241f0` (`ecx = this`, arg = row).
6. After the loop (and on the count `<= 0` path): `E8`
   `0x00548570` into `[this+0x10]`.

Those six callee bodies, the `0x18`-byte row layout names,
and the two `0x004241a0` stack-arg names are **not** this
proof.

Eleven body `E8` sites: `0x00539799` `0x004241a0`,
`0x005397b1` / `0x00539804` / `0x0053982b` / `0x00539838`
/ `0x00539845` / `0x00539878` `0x00548570`,
`0x005397da` `0x005490e0`, `0x005397f1` `0x0052f790`,
`0x00539818` `0x0052ec60`, `0x00539855` `0x004241f0`.

One inbound `.text` `E8`, zero `E9`: `0x00538f94` inside
table `CMissionScriptObjectCode__ctor` (not claimed). That
host allocs `0x14`, plants `ecx = alloc` / `push buffer`,
then `mov [esi+0x58], eax`. Zero image encodings of imm
`70 97 53 00`.

Cheapest falsifier: file `0x00139770` is not `6a ff`,
**or** `0x00139890` is not `c2 04 00`, **or** body SHA-256
is not `befb8eb8…9a9f`, **or** `tools/call_xref_scan.py` on
`0x00539770` is not the one `E8` above, **or**
`0x00139799` is not `e8 02 aa ee ff`, **or** `0x00139881`
is not `8b c5`, **or** a second inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539770` | `CScriptObjectCode__ReadSymbolTable` | `6aff 68f9755d00 64a100000000 50 64892500000000 83ec10 … 8bc5 5f5d5b 64890d00000000 83c41c c20400` | thiscall SEH; ret 4 ×1; 291 B; 11 E8 / 0 E9; 1 inbound E8. HIGH on ABI, inbound set, count-gated 0x18 row loop, `[this+0x10]` trailer Read, EAX=this. **Not** on callee bodies, row field names, or the ctor. |
