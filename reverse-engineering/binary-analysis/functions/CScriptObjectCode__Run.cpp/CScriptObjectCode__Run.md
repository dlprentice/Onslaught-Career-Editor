# CScriptObjectCode__Run

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
name is a research label. Callee bodies `0x004418a0` /
`0x00441740` / `0x005394a0` and `CScriptObjectCode.cpp.md` /
the CallEvent / CallEventDirect / GotoInstruction folders
were **not** written.

> Address: `0x00539b00`

## Contract

`thiscall`. First insn `push ecx` / `push esi` /
`mov esi, ecx`. Zero stack args. Three bare `ret` sites
(`0x00539b27` re-entry, `0x00539c2c` stop-path,
`0x00539c70` drain/normal). Body `0x00539b00`–`0x00539c70`
is 369 bytes, SHA-256
`d305b87f56233b53b96f379cdbf9a94918dcb7bb4a46f3c50f99a5602fbfda6d`.
Five `E8`, one `E9`. Fifteen `nop`s after the last `ret`
are **not** in the body (neighbour starts at `0x00539c80`).

If `[esi+0x210] == 1`, the body `push 0x00650208`
(`ERROR: VM tryin to run VM whilst it was already running.`)
/ `push 0x0066f580` and `E8`s table
`CConsole__PrintfNoNewline` `0x004418a0` (`0x00539b1c`,
`add esp, 8`), then `ret`. Else `[esi+0x210] = 1` and
`+0x218` / `+0x224` / `+0x220` are zeroed.

Loop fetch is `instr = [[obj+4] + PC*4]` with
`obj = [esi+8]`, `PC = [esi+0x214]`,
`symbols = [obj+0x58]`. Opcode is `call [vtable+8]`. If
`eax == 0x17` and `[esi+0x224] <= 0`, or
`[esi+0x220] != 0`, the body exits. Else `PC++` and
`call [vtable+0](vm, esi+0xc, symbols)`. If
`[obj+0x60] == 1` it `E8`s table `CConsole__Printf`
`0x00441740` (`0x00539bc3`) with
`0x006501e4` (`-> %4d stack size = %d flags = %d`). After
`0x2710` steps it `E8`s Printf (`0x00539bf1`) with
`0x006501bc` (`FATAL ERROR :Infinite loop in script!`),
stores `[esi+0x220] = 1`, and `E9`s `0x00539b5a`.

Exit always stores `[esi+0x210] = 0`. Stop-path
(`[esi+0x220] == 1`) stores `[esi+0x20c] = 0` and `ret`.
Else if `[esi+0x20c] != [esi+0x21c]` it `E8`s Printf
(`0x00539c47`) with `0x00650188`
(`FATAL ERROR:  stack was different size when exiting`).
While `[esi+0x20c] != 0` it `E8`s table
`CScriptObjectCode__RemoveTop` `0x005394a0`
(`0x00539c5e`, `ecx = esi+0xc`). Those callee bodies,
opcode identities, and instruction contents are **not**
this proof.

Five inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x005399dd` | already-pinned `CScriptObjectCode__CallEvent` |
| `0x00539a54` | already-pinned `CScriptObjectCode__CallEvent` |
| `0x00539a90` | already-pinned `CScriptObjectCode__CallEventDirect` |
| `0x00539ad5` | already-pinned `CScriptObjectCode__CallEventDirect` |
| `0x00539aea` | already-pinned `CScriptObjectCode__GotoInstruction` |

Zero image encodings of imm `00 9b 53 00`.

Cheapest falsifier: file `0x00139b00` is not `51 56 8b f1`,
**or** `0x00139c70` is not `c3`, **or** body SHA-256 is not
`d305b87f…da6d`, **or** `tools/call_xref_scan.py` on
`0x00539b00` is not the five `E8` above, **or**
`0x00139b0a` is not `39 86 10 02 00 00`, **or**
`0x00139b1c` is not `e8 7f 7d f0 ff`, **or**
`0x00139c03` is not `e9 52 ff ff ff`, **or**
`0x00139c5e` is not `e8 3d f8 ff ff`, **or** a sixth
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539b00` | `CScriptObjectCode__Run` | `51 56 8bf1 b801000000 57 398610020000 7516 … e87f7df0ff … c3 / … e9 52ffffff … e83df8ffff … 5f5e59 c3` | thiscall; bare ret ×3; 369 B; 5 E8 PrintfNoNewline / Printf ×3 / RemoveTop; 1 E9; 5 inbound E8. HIGH on ABI, inbound set, re-entry `+0x210`, 0x17 / stop exits, 0x2710 guard, drain. **Not** on callee bodies or opcode identities. |
