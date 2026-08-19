# CScriptObjectCode__Pop

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
`CScriptObjectCode.cpp.md` / the Push / RemoveTop folders
were **not** written.

> Address: `0x00539470`

## Contract

`thiscall`. First insn `mov eax, [ecx+0x200]` (incoming
ECX is the stack head; not saved). Zero stack args. Two
bare `ret` sites (`0x0053948e` empty, `0x00539499` live).
Body `0x00539470`–`0x00539499` is 42 bytes, SHA-256
`ec680849063096a0b785619c2b7ffccfcf2d46e0c020b33c2ee674e898904643`.
One `E8`, zero `E9`. Six `nop`s after the last `ret` are
**not** in the body (already-pinned neighbour
`CScriptObjectCode__RemoveTop` starts at `0x005394a0`).

If `[ecx+0x200] == 0`, the body `push 0x0065009c`
(`FATAL ERROR: Pop called on empty stack`) /
`push 0x0066f580` and `E8`s table `CConsole__Printf`
`0x00441740` (`0x00539484`, `add esp, 8`), then
`xor eax, eax` / `ret`. Else it stores `--[ecx+0x200]`
and returns `EAX = [ecx + newDepth*4]` (the pointer).
Unlike already-pinned `RemoveTop`, this path does **not**
call `vtable[+0](1)`. That callee body is **not** this
proof.

Twenty-nine inbound `.text` `E8`, zero `E9`. All sit in
the instruction-opcode band `0x0052e10e`–`0x0052ea6f` and
are **not** claimed. Full `tools/call_xref_scan.py` set:

`0x0052e10e` `0x0052e18a` `0x0052e193` `0x0052e1da`
`0x0052e1e3` `0x0052e22a` `0x0052e233` `0x0052e27a`
`0x0052e283` `0x0052e311` `0x0052e389` `0x0052e392`
`0x0052e4d9` `0x0052e4e2` `0x0052e589` `0x0052e592`
`0x0052e639` `0x0052e642` `0x0052e6d9` `0x0052e6e2`
`0x0052e779` `0x0052e782` `0x0052e819` `0x0052e822`
`0x0052e8b9` `0x0052e8c2` `0x0052e958` `0x0052ea15`
`0x0052ea6f`.

Zero image encodings of imm `70 94 53 00`.

Cheapest falsifier: file `0x00139470` is not
`8b 81 00 02 00 00`, **or** `0x00139499` is not `c3`,
**or** body SHA-256 is not `ec680849…4643`, **or**
`tools/call_xref_scan.py` on `0x00539470` is not the
twenty-nine `E8` above, **or** `0x00139484` is not
`e8 b7 82 f0 ff`, **or** `0x0013948c` is not `33 c0`,
**or** a thirtieth inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539470` | `CScriptObjectCode__Pop` | `8b8100020000 85c0 7515 689c006500 … e8b782f0ff … 33c0 c3 / 48 898100020000 8b0481 c3` | thiscall; bare ret ×2; 42 B; 1 E8 Printf; 0 E9; 29 inbound E8. HIGH on ABI, inbound count, empty-return-0, dec-and-return-pointer. **Not** on Printf or the opcode hosts. |
