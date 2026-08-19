# CScriptObjectCode__GetTop

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
`CScriptObjectCode.cpp.md` / the Push / Pop / RemoveTop
folders were **not** written.

> Address: `0x005394e0`

## Contract

`thiscall`. First insn `mov eax, [ecx+0x200]` (incoming
ECX is the stack head; not saved). One stack dword. Two
`ret 4` sites (`0x00539505` miss, `0x0053950c` hit). Body
`0x005394e0`–`0x0053950e` is 47 bytes, SHA-256
`60fee3b9800287563649c9cfa809c2f4077b3186e9c13f408be28d90027d5279`.
One `E8`, zero `E9`. One `nop` after the last `ret 4` is
**not** in the body (neighbour starts at `0x00539510`).

`idx = [ecx+0x200] - arg0`. If `idx <= 0`, the body
`push edx` / `push 0x006500f4`
(`FATAL ERROR: Stack item does not exist in call to GetTop - %d`)
/ `push 0x0066f580` and `E8`s table `CConsole__Printf`
`0x00441740` (`0x005394fb`, `add esp, 0xc`), then
`xor eax, eax` / `ret 4`. Else it returns
`EAX = [ecx + idx*4 - 4]` (arg 0 is the top). It does
**not** decrement depth. That callee body is **not** this
proof.

Four inbound `.text` `E8`, zero `E9`, all in the
instruction-opcode band and **not** claimed. Full
`tools/call_xref_scan.py` set: `0x0052e33b` `0x0052e348`
`0x0052e9dc` `0x0052e9f8`. Zero image encodings of imm
`e0 94 53 00`.

Cheapest falsifier: file `0x001394e0` is not
`8b 81 00 02 00 00`, **or** `0x0013950c` is not
`c2 04 00`, **or** body SHA-256 is not `60fee3b9…5279`,
**or** `tools/call_xref_scan.py` on `0x005394e0` is not
the four `E8` above, **or** `0x001394fb` is not
`e8 40 82 f0 ff`, **or** `0x00139508` is not
`8b 44 81 fc`, **or** a fifth inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005394e0` | `CScriptObjectCode__GetTop` | `8b8100020000 8b542404 2bc2 85c0 7f18 … e84082f0ff … 33c0 c20400 / 8b4481fc c20400` | thiscall; ret 4 ×2; 47 B; 1 E8 Printf; 0 E9; 4 inbound E8. HIGH on ABI, inbound set, idx=`depth-arg`, miss-return-0, arg0=top. **Not** on Printf or the opcode hosts. |
