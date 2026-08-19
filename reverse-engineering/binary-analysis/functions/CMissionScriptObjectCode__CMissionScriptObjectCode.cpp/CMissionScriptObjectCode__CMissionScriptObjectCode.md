# CMissionScriptObjectCode__CMissionScriptObjectCode

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`,
`ScriptObjectCode.cpp.md`, or the already-pinned
`0x00538ec0` ctor)
|| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Adopted `t_15e3a6ed` after
independent re-derivation (steward cycle 44 re-read the
child; this card owns the land). The Ghidra database was
not opened. Table name is a research label. Already-pinned
`CMissionScriptObjectCode__ctor` `0x00538ec0` /
`CVM__Destructor` / `FUN_005398c0` /
`CScriptObjectCode.cpp.md` / table `CWaitingThread__ctor_base`
/ inbound host / sibling `0x00539f40` were **not** written.

> Address: `0x00539c80`

## Contract

`thiscall`, not SEH. First insn `push esi` / `mov esi, ecx`.
Zero stack args. One bare `ret` (`0x00539c95`). Body
`0x00539c80`–`0x00539c95` is 22 bytes, SHA-256
`6852d07bd9ea1022107b2e68d592b48e7121a12251ea44ca0ea1f2f6c39a41d9`.
One `E8`, zero `E9`. Ten nops after the `ret` are **not**
in the body (neighbour table `CXBOXAsyncCache__LoadAsync`
starts at `0x00539ca0`).

The body:

1. `E8` `0x00528bc0` (`ecx = this`; table
   `CWaitingThread__ctor_base`, not claimed).
2. Stores imm `0x005e4f5c` at `[this]` (**not** the
   already-pinned `0x00538ec0` vptr imm `0x005e4f54`).
3. Stores byte `0` at `[this+0x20]`.

`EAX = this` at the `ret` (`8b c6`). The `0x00528bc0` body,
the pointed-to table at `0x005e4f5c`, and the class of
`this` are **not** this proof.

One body `E8` site: `0x00539c83` `0x00528bc0`.

One inbound `.text` `E8`, zero `E9`: `0x00465ffb` inside
table `CFEPMultiplayerStart__ctor` (not claimed; host
`0x00465f10`–`0x00466115`). Independently re-read at the
site: `lea edi, [esi+0x37dc]` (`0x00465fec`), then
`lea ecx, [edi+0xc]` / `[edi] = ebp` / this call. Zero
image encodings of imm `c0 9c 53 00`.

Cheapest falsifier: file `0x00139c80` is not `56`,
**or** `0x00139c95` is not `c3`, **or** body SHA-256 is not
`6852d07b…41d9`, **or** `tools/call_xref_scan.py` on
`0x00539c80` is not the one `E8` above, **or**
`0x00139c88` is not `c7 06 5c 4f 5e 00`, **or**
`0x00139c83` is not `e8 38 ef fe ff`, **or** a second
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539c80` | `CMissionScriptObjectCode__CMissionScriptObjectCode` | `56 8bf1 e838effeff c7065c4f5e00 c6462000 8bc6 5e c3` | thiscall; bare ret ×1; 22 B; 1 E8 / 0 E9; 1 inbound E8. HIGH on ABI, inbound set, vptr imm `0x005e4f5c`, `[+0x20]=0`, EAX=this. **Not** on `0x00528bc0`, the inbound host, or class identity. |
