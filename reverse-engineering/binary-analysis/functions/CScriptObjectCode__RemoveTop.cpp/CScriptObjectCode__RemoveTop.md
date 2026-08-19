# CScriptObjectCode__RemoveTop

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
`CScriptObjectCode.cpp.md` / the Run folder / the
REMOVE_TOP opcode thunk were **not** written.

> Address: `0x005394a0`

## Contract

`thiscall`. First insn `mov eax, [ecx+0x200]` (incoming
ECX is the stack head; not saved). Zero stack args. Two
bare `ret` sites (`0x005394bc` empty, `0x005394d1` after
the delete). Body `0x005394a0`–`0x005394d1` is 50 bytes,
SHA-256
`dc3578e681b098b93a83e38f5f7c06548c2b3e709d0fc8ddf3127f05bf0bb728`.
One `E8`, zero `E9`. Nops after the last `ret` are **not**
in the body (neighbour `CScriptObjectCode__GetTop` starts
at `0x005394e0`).

If `[ecx+0x200] == 0`, the body `push 0x006500c4`
(`FATAL ERROR: RemoveTop called on empty stack`) /
`push 0x0066f580` and `E8`s table `CConsole__Printf`
`0x00441740` (`0x005394b4`, `add esp, 8`), then `ret`.
Else it stores `--[ecx+0x200]`, loads
`elem = [ecx + newDepth*4]`, and if `elem != 0` does
`push 1` / `call [vtable+0]`. That slot-0 body is **not**
this proof. Unlike table `Pop`, this path does not return
the pointer.

Two inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x0052e324` | table `CInstructionOP_REMOVE_TOP__VFunc_0_0052e320` |
| `0x00539c5e` | already-pinned `CScriptObjectCode__Run` |

Zero image encodings of imm `a0 94 53 00`. The opcode
thunk is **not** claimed.

Cheapest falsifier: file `0x001394a0` is not
`8b 81 00 02 00 00`, **or** `0x001394d1` is not `c3`,
**or** body SHA-256 is not `dc3578e6…b728`, **or**
`tools/call_xref_scan.py` on `0x005394a0` is not the two
`E8` above, **or** `0x001394b4` is not
`e8 87 82 f0 ff`, **or** `0x001394be` is not
`89 81 00 02 00 00`, **or** a third inbound `E8`/`E9`
exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005394a0` | `CScriptObjectCode__RemoveTop` | `8b8100020000 85c0 7513 68c4006500 … e88782f0ff … c3 / 48 898100020000 8b0c81 85c9 7406 8b01 6a01 ff10 c3` | thiscall; bare ret ×2; 50 B; 1 E8 Printf; 0 E9; 2 inbound E8. HIGH on ABI, inbound set, empty printf, dec-and-delete. **Not** on Printf, slot-0, or the opcode thunk. |
