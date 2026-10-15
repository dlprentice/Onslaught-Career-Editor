# CScriptObjectCode__GetInstruction

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`)
|| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Child report
`local-lab/hermes-kanban-campaign-2026-08-18/getinstruction-00539760/REPORT.md`
was treated as data and re-derived. The Ghidra database was not
opened. Table name is a research label. Already-pinned
`InitRuntime` / `CopyState` / `CScriptObjectCode.cpp.md` / the
opcode hosts / `CEventFunction` / `CollectSpawnThings` /
`ReadSymbolTable` were **not** written.

> Address: `0x00539760`

## Contract

`thiscall`. First insn `mov eax, [ecx]` / `mov ecx, [esp+4]`.
One stack dword (index). One `ret 4` site (`0x00539769`). Body
`0x00539760`–`0x0053976b` is 12 bytes, SHA-256
`a7a4a67db52176623a58c6892f73d1ded127a5f9c5c3671075925406464ae3d2`.
Zero `E8`, zero `E9`. Four nops after the `ret 4` are
**not** in the body (neighbour table
`CScriptObjectCode__ReadSymbolTable` starts at `0x00539770`).

Incoming ECX is a pointer whose first dword is the array base.
The body does `table = [this]`, `index = arg0`,
`EAX = [table + index*4]`. It does **not** bounds-check and
does **not** write memory. That is `return [this+0][index]`,
not `return this[index]`. The pointed-to slots are **not**
this proof; the table name is not a claim that they are
instructions.

Seven inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x0052e2cb` | table `CInstructionOP_PUSH__VFunc_00_0052e2c0` |
| `0x0052e2f9` | table `CInstructionOP_POP__VFunc_0_0052e2f0` |
| `0x0052e9c9` | table `CInstructionOP_GETTOP__VFunc_0_0052e9c0` |
| `0x0052fb03` | table `CEventFunction__CEventFunction` |
| `0x0052fc72` | table `CEventFunction__Clone` |
| `0x0052fca2` | table `CEventFunction__Clone` |
| `0x0053931f` | table `CScriptObjectCode__CollectSpawnThings` |

Those hosts are **not** claimed. Zero image encodings of imm
`60 97 53 00`.

Cheapest falsifier: file `0x00139760` is not `8b 01`,
**or** `0x00139769` is not `c2 04 00`, **or** body SHA-256 is
not `a7a4a67d…e3d2`, **or** `tools/call_xref_scan.py` on
`0x00539760` is not the seven `E8` above, **or**
`0x00139766` is not `8b 04 88`, **or** an eighth inbound
`E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539760` | `CScriptObjectCode__GetInstruction` | `8b01 8b4c2404 8b0488 c20400` | thiscall; ret 4 ×1; 12 B; 0 E8/E9; 7 inbound E8. HIGH on ABI, inbound set, `EAX = [[this]+index*4]`. **Not** on the hosts or slot types. |
