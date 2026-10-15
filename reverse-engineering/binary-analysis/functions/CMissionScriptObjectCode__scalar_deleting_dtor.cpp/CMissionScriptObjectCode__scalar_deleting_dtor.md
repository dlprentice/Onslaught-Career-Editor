# CMissionScriptObjectCode__scalar_deleting_dtor

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`
or the already-pinned dtor)
||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. Already-pinned
`CMissionScriptObjectCode__dtor` / `CScriptObjectCode.cpp.md` /
the `0x00549220` callee were **not** written. Steward cycle 42
accepted ClearSymbolTable / Clone / CloneSymbolTable — not
redone. This wake landed `dbddd4fa` / `77bb9a17`. Did not steal
`t_a8841217`.

> Address: `0x00538ea0`

## Contract

`thiscall`, not SEH. First insn `push esi` / `mov esi, ecx`.
One stack dword. One `ret 4` (`0x00538ebd`). Body
`0x00538ea0`–`0x00538ebf` is 32 bytes, SHA-256
`a155e85757a590680414a47d46bb86eae1a033045f3a6a3126d346a30e79644a`.
Two `E8`, zero `E9`. Neighbour table
`CMissionScriptObjectCode__ctor` starts at the next byte
(`0x00538ec0`) and is owned by `t_a8841217`.

The body:

1. `E8` already-pinned `CMissionScriptObjectCode__dtor`
   `0x005391a0` (`ecx = this`).
2. `test byte [esp+8], 1`. If clear, skip the Free.
3. Else `push esi` / `E8` `0x00549220` with
   `ecx = 0x009c3df0`.

`EAX = this` at the `ret` (`8b c6`). The `0x00549220` body
is **not** this proof.

Two body `E8` sites: `0x00538ea3` `0x005391a0`,
`0x00538eb5` `0x00549220`.

Zero inbound `.text` `E8`/`E9`. One image encoding of imm
`a0 8e 53 00`: file `0x001e4f54` / VA `0x005e4f54` — the
same address already-pinned `Clone` / `dtor` write as
`[this]`. That slot's other dwords are **not** this proof.

Cheapest falsifier: file `0x00138ea0` is not `56`,
**or** `0x00138ebd` is not `c2 04 00`, **or** body SHA-256
is not `a155e857…644a`, **or** `tools/call_xref_scan.py` on
`0x00538ea0` is not empty, **or** `0x00138ea3` is not
`e8 f8 02 00 00`, **or** `0x001e4f54` is not `a0 8e 53 00`,
**or** a second encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00538ea0` | `CMissionScriptObjectCode__scalar_deleting_dtor` | `56 8bf1 e8f8020000 f644240801 740b 56 b9f03d9c00 e866030100 8bc6 5e c20400` | thiscall; ret 4 ×1; 32 B; 2 E8 / 0 E9; 0 inbound E8/E9. HIGH on ABI, unique vptr slot at `0x005e4f54`, already-pinned dtor then bit0 Free. **Not** on `0x00549220` or the ctor neighbour. |
