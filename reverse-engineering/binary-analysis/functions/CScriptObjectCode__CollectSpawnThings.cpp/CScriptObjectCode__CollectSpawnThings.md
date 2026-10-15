# CScriptObjectCode__CollectSpawnThings

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`)
||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). Child report
`local-lab/hermes-kanban-campaign-2026-08-18/collectspawnthings-005392a0/REPORT.md`
was treated as data and re-derived. The Ghidra database was not
opened. Table name is a research label. Already-pinned
`GetInstruction` / `ClearSymbolTable` / `CMissionScriptObjectCode__dtor`
/ `CScriptObjectCode.cpp.md` / the inbound LoadWorld host / the
`0x0050d9e0` callee were **not** written. Steward cycle 42
accepted ClearSymbolTable / Clone / CloneSymbolTable — not
redone. Did not steal `t_a8841217`.

> Address: `0x005392a0`

## Contract

`thiscall`, not SEH. First insn `push ebp`. Incoming ECX is
parked in `EDI`. `EBP` is the loop index (`xor ebp, ebp`),
not a frame pointer. Zero stack args. One bare `ret`
(`0x00539345`). Body `0x005392a0`–`0x00539345` is 166 bytes,
SHA-256
`0faa4f269d18023ba27e37a4b506cb5262bcceaaea8de91d3086c1fb378f71d7`.
Two `E8`, zero `E9`. Ten nops after the `ret` are **not**
in the body (already-pinned neighbour
`CScriptObjectCode__RestoreStack` starts at `0x00539350`).

`jle` `0x00539343` skips the walk when `[this+0xc] <= 0`.
Each slot is `esi = [[this+4] + i*4]`. `call [[esi]+8]`
(indirect). `cmp eax, 0x18` / `jne` next. Match path:

1. `edx = [esi+4]`; `esi = [[(edx & 0xff) << 6] + 0x0064ce20]`.
2. Two-byte C-string walk against imm `0x0064f9fc`
   (`"SpawnThing"`). A mismatch `jne`s to the increment.
3. `back = i - DH([slot+4])`, `other = [[this+4]+back*4]`,
   `ecx = [this+0x58]`, `push [other+4]`, `E8` already-pinned
   `GetInstruction` `0x00539760`.
4. `ecx = [eax+8]`, `call [[ecx]+0x38]` (indirect), cdecl
   `push eax` / `E8` `0x0050d9e0` / `add esp, 4`.

No store to `this`. `EAX` at the `ret` is leftover. Slot
types, the `0x0064ce20` row class, both vfuncs, and the
schema name of opcode `0x18` are **not** this proof.

Two body `E8` sites: `0x0053931f` `0x00539760`,
`0x0053932d` `0x0050d9e0`.

One inbound `.text` `E8`, zero `E9`: `0x0050d401` inside
table `CWorld__LoadWorld` (not claimed). That host walks
`esi = [[edx+0x120]]` as a `[node+4]` list; `eax = [node]`,
then `eax = [eax+4]`; null skips; else `ecx = eax` then
this call. Zero image encodings of imm `a0 92 53 00`.

Cheapest falsifier: file `0x001392a0` is not `55`,
**or** `0x00139345` is not `c3`, **or** body SHA-256 is not
`0faa4f26…71d7`, **or** `tools/call_xref_scan.py` on
`0x005392a0` is not the one `E8` above, **or**
`0x0013931f` is not `e8 3c 04 00 00`, **or**
`0x001392c0` is not `83 f8 18`, **or** a second inbound
`E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005392a0` | `CScriptObjectCode__CollectSpawnThings` | `55 57 8bf9 33ed 8b470c 85c0 0f8e92000000 … 45 3be8 0f8c72ffffff 5e5b5f5d c3` | thiscall; bare ret ×1; 166 B; 2 E8 / 0 E9; 1 inbound E8. HIGH on ABI, inbound set, `[[slot]+8]==0x18` then `"SpawnThing"` walk, already-pinned GetInstruction. **Not** on vfuncs, `0x0050d9e0`, or LoadWorld. |
