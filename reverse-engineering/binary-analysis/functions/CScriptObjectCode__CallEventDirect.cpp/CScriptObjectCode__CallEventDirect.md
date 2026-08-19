# CScriptObjectCode__CallEventDirect

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
name is a research label. Callee bodies `0x00539b00` /
`0x00539420` and `CScriptObjectCode.cpp.md` /
`EventFunction.cpp.md` / the IScript wrapper folders /
`CScriptObjectCode__CallEvent.cpp` were **not** written.

> Address: `0x00539a60`

## Contract

`thiscall`. First insn `push ebx` / `push esi` / `push edi`
then `mov edi, [esp+0x10]` / `mov esi, ecx`. Four stack
dwords. One `ret 0x10` at `0x00539add`. Body
`0x00539a60`–`0x00539adf` is 128 bytes, SHA-256
`471c0da50c71125e80390a80c065e6f063e96aefe382de893eaa6380560ba073`.
Three `E8`, zero `E9`. Neighbour
`CScriptObjectCode__GotoInstruction` starts immediately at
`0x00539ae0` (no pad). This is **not** the id-table fire
path (`CScriptObjectCode__CallEvent` ends at the `nop` at
`0x00539a5f`).

No `+0x20c` stack-empty printf. `[esi+8] = [esp+0x10]`
(first stack arg, the event object). If `[eventObj+0x6c]
== 0` and `[eventObj+0x5c] != 0`: `[esi+0x214] = 0`,
`[esi+0x21c] = [esi+0x20c]`, `E8` table
`CScriptObjectCode__Run` `0x00539b00` (`0x00539a90`), then
`[eventObj+0x6c] = 1`.

Then `[esi+0x21c] = [esi+0x20c]` again. If argCount
`[esp+0x1c] > 0`, the body walks `args[]` at `[esp+0x18]`
through table `CScriptObjectCode__Push` `0x00539420`
(`0x00539abd`, `ecx = esi+0xc`). Then
`[esi+0x214] = [esp+0x14]` (entry PC taken directly, **not**
`[obj+id*4+0x14]`) and `E8` Run `0x00539b00`
(`0x00539ad5`). Those callee bodies, named-callback
occupancy, and the Execute host are **not** this proof.

One inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x0052fe24` | table `CEventFunction__Execute` |

The host plants `push ebp` / `push edx` / `push [this+8]` /
`push [this+0x1c]` then `ecx = 0x0089c5e0` before that
`E8`. Zero image encodings of imm `60 9a 53 00`. That host
is **not** claimed.

Cheapest falsifier: file `0x00139a60` is not `53 56 57`,
**or** `0x00139add` is not `c2 10 00`, **or** body SHA-256
is not `471c0da5…a073`, **or** `tools/call_xref_scan.py` on
`0x00539a60` is not the one `E8` above, **or**
`0x00139a69` is not `89 7e 08`, **or** `0x00139a90` is not
`e8 6b 00 00 00`, **or** `0x00139abd` is not
`e8 5e f9 ff ff`, **or** `0x00139acf` is not
`89 86 14 02 00 00`, **or** `0x00139ad5` is not
`e8 26 00 00 00`, **or** a second inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539a60` | `CScriptObjectCode__CallEventDirect` | `53 56 57 8b7c2410 8bf1 897e08 8b476c … e86b000000 c7476c01000000 … e85ef9ffff … 898614020000 e826000000 5f5e5b c21000` | thiscall; ret 0x10; 128 B; 3 E8 Run / Push / Run; 0 E9; 1 inbound E8. HIGH on ABI, inbound set, `[this+8]` store, same preamble as CallEvent, PC = entryPC not slot. **Not** on callee bodies, Execute, or named-callback occupancy. |
