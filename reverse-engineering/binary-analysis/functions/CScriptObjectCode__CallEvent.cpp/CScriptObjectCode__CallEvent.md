# CScriptObjectCode__CallEvent

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`)
| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Callee bodies `0x00441740` / `0x00539b00` / `0x00539420`
and `CScriptObjectCode.cpp.md` / the IScript wrapper folders
landed this wake were **not** written.

> Address: `0x00539990`

## Contract

`thiscall`. First insn `push esi` / `mov esi, ecx`. Four
stack dwords. Two `ret 0x10` sites (`0x00539a21` on the
slot-`-1` discard, `0x00539a5c` on the live path / empty
argCount). Body `0x00539990`–`0x00539a5e` is 207 bytes,
SHA-256
`8dfb9982f332d3bc9ee0cf62d202ac85ca334f02be4cd4989195a6d9d99c15f2`.
Four `E8`, zero `E9`. One `nop` after the last `ret 0x10`
is **not** in the body (neighbour
`CScriptObjectCode__CallEventDirect` starts at `0x00539a60`).

If `[esi+0x20c] != 0`, the body `push 0x00650160`
(`FATAL ERROR: stack not empty on call`) / `push 0x0066f580`
and `E8`s table `CConsole__Printf` `0x00441740`
(`0x005399a8`, `add esp, 8`). It does **not** return there.

Then `[esi+8] = [esp+0xc]` (first stack arg, the event
object). If `[eventObj+0x6c] == 0` and `[eventObj+0x5c] !=
0`: `[esi+0x214] = 0`, `[esi+0x21c] = [esi+0x20c]`, `E8`
table `CScriptObjectCode__Run` `0x00539b00` (`0x005399dd`),
then `[eventObj+0x6c] = 1`.

Slot load is `eax = [[esi+8] + eventId*4 + 0x14]`
(`mov eax, [ecx+edx*4+0x14]` at `0x005399f0`);
`[esi+0x214] = eax`. If `eax == -1` and argCount `> 0`,
the body walks `args[]` and `push 1` / `call [vtable+0]`
on each live pointer, then `ret 0x10`. If `eax != -1`, it
stores `[esi+0x21c] = [esi+0x20c]`, optionally walks
`args[]` through table `CScriptObjectCode__Push`
`0x00539420` (`ecx = esi+0xc`), then `E8` Run
`0x00539b00` (`0x00539a54`). Those callee bodies, the
13-slot name table, and authored event names are **not**
this proof.

Eight inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x0053352a` | already-pinned `IScript__CallEvent0AndRegisterNestedListeners` |
| `0x005335c5` | already-pinned `IScript__CallEventId6_OrReset` |
| `0x0053364e` | already-pinned `IScript__CreateThingRef` |
| `0x00533685` | already-pinned `IScript__CallEventId5_OrReset` |
| `0x005337bd` | already-pinned `IScript__CreateThingRefWithSquad` |
| `0x00533805` | already-pinned `IScript__CallEventId3_OrReset` |
| `0x00533835` | already-pinned `IScript__VFunc_2_00533810` |
| `0x00538638` | table `IScript__HandleMessage` |

Zero image encodings of imm `90 99 53 00`. The HandleMessage
host is **not** claimed.

Cheapest falsifier: file `0x00139990` is not `56 8b f1`,
**or** `0x00139a5c` is not `c2 10 00`, **or** body SHA-256
is not `8dfb9982…15f2`, **or** `tools/call_xref_scan.py` on
`0x00539990` is not the eight `E8` above, **or**
`0x00139994` is not `8b 86 0c 02 00 00`, **or**
`0x001399f0` is not `8b 44 91 14`, **or** `0x001399f4` is
not `83 f8 ff`, **or** `0x00139a54` is not
`e8 a7 00 00 00`, **or** a ninth inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539990` | `CScriptObjectCode__CallEvent` | `56 8bf1 57 8b860c020000 85c0 7412 6860016500 … e8937df0ff … 897e08 … 8b449114 83f8ff … c21000` | thiscall; ret 0x10 ×2; 207 B; 4 E8 Printf / Run / Push / Run; 0 E9; 8 inbound E8. HIGH on ABI, inbound set, `+0x20c` printf, `[this+8]` store, slot `[obj+id*4+0x14]`, `-1` discard vs Run. **Not** on callee bodies, 13-slot names, or HandleMessage. |
