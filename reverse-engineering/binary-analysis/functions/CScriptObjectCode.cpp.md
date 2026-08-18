# CScriptObjectCode function map

Status: active static function map
Last updated: 2026-08-17 (CopyState/Reset/CallEvent/CallEventDirect/
GotoInstruction/Run byte-mapped from the pristine specimen)
Source File: `C:\dev\ONSLAUGHT2\MissionScript\ScriptObjectCode.cpp` (the
VM's `__FILE__` chain is established by the adjacent
[`ScriptObjectCode.cpp.md`](ScriptObjectCode.cpp.md) wave receipts) | Binary:
BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — every byte below was re-read from the pristine specimen at
file offset VA − 0x400000 with `tools/disasm_va.py`; embedded strings read
from the same image. Function names are the live Ghidra name table
(db.18627 lineage); the byte contracts below are independent of the names.

## Shape

`CScriptObjectCode` is the mission-script stack-VM instance; the shipped
global singleton is `0x0089c5e0` (every teardown arm in
[`IScript.cpp.md`](IScript.cpp.md) loads it). Measured field map from the
bodies below:

| Offset | Field | Witness |
| --- | --- | --- |
| `+0x08` | current event/script object | `mov [esi+8],edi` in `CallEvent`/`CallEventDirect`; its `+0x04` is the code array, `+0x58` the symbol table |
| `+0x0c` | operand stack head | `lea ecx,[esi+0xc]` fed to `Push`/`RestoreStack`/`ClearStack` |
| `+0x20c` | stack depth | compared against `+0x21c` at exit; zeroed on the stop path |
| `+0x210` | running flag | `Run`'s re-entry guard sets 1, clears 0 at every exit |
| `+0x214` | instruction pointer (PC) | written by `GotoInstruction`/`CallEvent`/`Run` |
| `+0x218` | flags (printed by the trace) | trace format `"-> %4d stack size = %d flags = %d"` |
| `+0x21c` | saved stack base | snapshot before `Run`; the exit check compares `+0x20c` to it |
| `+0x220` | stop flag | set to 1 by the 10,000-step guard; `Run` exits when nonzero |
| `+0x224` | return-depth guard | `Run` exits when a `0x17` (`POP_OR_STOP`) instruction fires and `+0x224 <= 0` |

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539910` | `CScriptObjectCode__CopyState` | `8b7c240c 8bf1 8b4708 8d570c 894608 8b8f14020000 898e14020000 52 8d4e0c e81afaffff … 8b8718020000 898618020000 … c7861002000000000000 8bc6 … c20400` | `ret 4`, one arg = source. Copies `[src+8]`, `[src+0x214]` (PC), calls `CScriptObjectCode__RestoreStack` (`0x00539350`) with `(dst+0xc, src+0xc)`, then copies `+0x218`, `+0x220`, `+0x21c`, `+0x224`, and zeroes the running flag `+0x210`. Returns `this`. HIGH. |
| `0x00539980` | `CScriptObjectCode__Reset` | `83c10c e958faffff` | Zero-arg tail: `add ecx,0xc; jmp 0x005393e0` = `CScriptObjectCode__ClearStack(this+0xc)`. HIGH. |
| `0x00539990` | `CScriptObjectCode__CallEvent` | `8b860c020000 85c0 7412 6860016500 6880f56600 e8937df0ff … 8b7c240c 897e08 8b476c 85c0 752b 8b475c 85c0 7424 c7861402000000000000 … e81e010000 c7476c01000000 … 8b449114 83f8ff 898614020000 7525 …` | `ret 0x10`, four args `(eventObj, eventId, args[], argCount)`. If the operand stack is not empty (`[this+0x20c] != 0`) prints `"FATAL ERROR: stack not empty on call"` (`0x00650160`). Stores `[this+8] = eventObj`; if `eventObj->[+0x6c] == 0` and `eventObj->[+0x5c] != 0` runs the preamble (`PC = 0`, `Run`, then `eventObj->[+0x6c] = 1`). Resolves the entry `eventObj->[+0x14 + eventId*4]`; `-1` means no handler, in which case it deletes each arg element via `call [elem->vtable][0](elem, 1)` and returns. Otherwise sets `PC = entry`, pushes each arg with `CScriptObjectCode__Push` (`0x00539420`), and calls `Run`. HIGH; the `eventId → handler` table shape (`+0x14`) is measured, the `+0x5c`/`+0x6c` meanings are MEDIUM. |
| `0x00539420` | `CScriptObjectCode__Push` | `8b4c2408 8b8600020000 890c86 8b8e00020000 41 898600020000 3d80000000 7e1f 6878006500 6880f56600 e8eb82f0ff … 48 898600020000 … c20400` | `ret 4`; `this` = the stack head (`this+0xc` of the VM). `sp = [head+0x200]; [head + sp*4] = arg; sp++`; if `sp > 0x80` (128) it prints `"FATAL ERROR: Stack out of memory"` (`0x00650078`) and decrements the depth back (the overflowing push is rejected). HIGH — the 128-slot stack ceiling the schema records is byte-verified here. |
| `0x005393e0` | `CScriptObjectCode__ClearStack` | `8b8600020000 85c0 7423 … 8b4c86fc 85c9 7406 8b11 6a01 ff12 … 48 898600020000 75dd` | Zero-arg; walks the stack top-down, `call [elem->vtable][0](elem, 1)` for each non-null element, and zeroes the depth `+0x200`. HIGH. |
| `0x00539350` | `CScriptObjectCode__RestoreStack` | `8b8600020000 85c0 7423 … 8b7c240c 33c9 8b8700020000 898600020000 7e2c … 8b2c02 8928 … c7870002000000000000 … c20400` | `ret 4`; `this` = destination head, arg = source head. First clears the destination (the same delete loop as `ClearStack`), then copies the source's depth and each element dword `[src + i*4] → [dst + i*4]` (a **shallow move** of the pointer array), and zeroes the source depth. HIGH. |
| `0x00539a60` | `CScriptObjectCode__CallEventDirect` | `8b7c2410 8bf1 897e08 8b476c 85c0 7529 8b475c 85c0 7422 c7861402000000000000 8b860c020000 89861c020000 e86b000000 c7476c01000000 … 8b5c241c 8b8e0c020000 85db 898e1c020000 7e19 … e85ef9ffff … 8b442414 8bce 898614020000 e826000000 …` | `ret 0x10`, four args `(eventObj, entryPC, args[], argCount)`. Same preamble as `CallEvent` (PC = 0 + `Run` + `eventObj->[+0x6c] = 1` when `+0x6c == 0` and `+0x5c != 0`); snapshots the stack base (`+0x21c = +0x20c`); pushes each arg; sets `PC = entryPC` (taken directly, not looked up); calls `Run`. This is the entry `CEventFunction__Execute` uses for named callbacks. HIGH. |
| `0x00539ae0` | `CScriptObjectCode__GotoInstruction` | `8b442404 898114020000 e811000000 c20400` | `ret 4`: `PC = arg; Run()`. HIGH — the jump-into-script primitive behind `IScript`'s 2001 teardown. |
| `0x00539b00` | `CScriptObjectCode__Run` | `b801000000 398610020000 7516 6808026500 6880f56600 e87f7df0ff … 8b8e14020000 898610020000 8b4608 … 8b5004 8b4058 8b3c8a … 8b17 8bcf ff5208 83f817 750e 8b8624020000 85c0 0f8e94000000 … 8b9e14020000 8d4e0c 8d4301 898614020000 … 50 51 56 8bcf ff12 …` | The interpreter loop. Re-entry guard: if `[this+0x210] == 1` prints `"ERROR: VM tryin to run VM whilst it was already running."` (`0x00650208`) and returns; else sets the flag. Each step: `instr = code[PC]` with `code = [obj+4]`, `symbols = [obj+0x58]`; `opcode = instr->vtable[8]()`; if `opcode == 0x17` (`POP_OR_STOP` / `CInstructionOP_RETURN__ExecutePop`, per the [VM schema](../missionscript-vm-datatype-opcode-schema.v1.json)) and `[this+0x224] <= 0` → exit; if the stop flag `[this+0x220] != 0` → exit; otherwise `PC++` and `instr->vtable[0](this, &stack[this+0xc], symbols)`. A `0x2710` (10,000) instruction guard prints `"FATAL ERROR :Infinite loop in script!"` (`0x006501bc`) and sets the stop flag. If `[obj+0x60] == 1` it traces `"-> %4d stack size = %d flags = %d"` (`0x006501e4`) per step. On exit: stop path zeroes `+0x20c`; normal path compares stack depth `+0x20c` against the saved base `+0x21c` and prints `"FATAL ERROR:  stack was different size when exiting"` (`0x00650188`) on mismatch. HIGH. |

## Wiring with the rest of the script system

- `IScript`'s message arms call the singleton: 2001 →
  `CopyState`/`Reset`/`GotoInstruction`; 2002 → `Reset`/`CallEvent`
  ([`IScript.cpp.md`](IScript.cpp.md)).
- `CEventFunction__Execute` (`0x0052fda0`) stages its parameter wrappers and
  calls `CallEventDirect` ([`EventFunction.cpp.md`](EventFunction.cpp.md)).
- `CMissionScriptObjectCode__ctor` (`0x00538ec0`) is the derived loader
  (`CWorld__LoadScriptEvents` constructs it per script file; see
  [`CScriptEventNB.cpp.md`](CScriptEventNB.cpp.md)).

## Stack discipline (settled this slice)

The operand stack is an **inline 128-dword array**: head at `+0xc` of the VM
object, depth at `[head+0x200]` (the `+0x20c` field `Run` and `CallEvent`
already read). `Push` stores at `[head + depth*4]` and rejects past 128 with
`"FATAL ERROR: Stack out of memory"`; `ClearStack` and `RestoreStack` delete
each resident element through its `vtable[0](elem, 1)` (the shared
value-delete convention), and `RestoreStack` then shallow-moves the source's
pointer array into the destination.

## Open questions (cheapest falsifier first)

- The instruction vtable contract: `vtable[8]` = opcode getter and
  `vtable[0]` = executor (this map); byte-map one instruction class's two
  slots to pin the getter's return width.
- `eventObj->[+0x5c]` (preamble present) and `eventObj->[+0x6c]` (preamble
  run) — which structure owns those fields and what sets them.
- `[obj+0x60]` — who enables the per-step trace flag.
