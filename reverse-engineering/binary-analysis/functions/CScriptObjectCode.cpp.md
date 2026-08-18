# CScriptObjectCode function map

Status: active static function map
Last updated: 2026-08-18 (POP stores stack top into symbol[attr]+8)
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
| `+0x08` | current `CMissionScriptObjectCode*` | `mov [esi+8],edi` in `CallEvent`/`CallEventDirect`; constructed at `0x00538ec0` |
| `+0x0c` | operand stack head | `lea ecx,[esi+0xc]` fed to `Push`/`RestoreStack`/`ClearStack` |
| `+0x20c` | stack depth | compared against `+0x21c` at exit; zeroed on the stop path |
| `+0x210` | running flag | `Run`'s re-entry guard sets 1, clears 0 at every exit |
| `+0x214` | instruction pointer (PC) | written by `GotoInstruction`/`CallEvent`/`Run` |
| `+0x218` | flags (printed by the trace) | trace format `"-> %4d stack size = %d flags = %d"` |
| `+0x21c` | saved stack base | snapshot before `Run`; the exit check compares `+0x20c` to it |
| `+0x220` | stop flag | set to 1 by the 10,000-step guard; `Run` exits when nonzero |
| `+0x224` | return-depth guard | `Run` zeroes it on entry; `CInstructionOP_CALLLOCAL__VFunc_0_0052ec40` is the only interpreter increment; `ExecutePop` decrements; a fetched `0x17` with this field `<= 0` exits `Run` |

### Event object (`CMissionScriptObjectCode`, 0x70 bytes)

`CallEvent`'s `eventObj` is the 0x70-byte record `CWorld__LoadScriptEvents`
allocates (`world.cpp:195`) and constructs via
`CMissionScriptObjectCode__ctor` (`0x00538ec0`; only direct `E8` is
`0x0050ad20`). The ctor installs vptr `0x005e4f54` and the `__FILE__`
pointer used for its allocations is `0x00650040` =
`C:\dev\ONSLAUGHT2\MissionScript\ScriptObjectCode.cpp`.

| Offset | Field | Witness |
| --- | --- | --- |
| `+0x00` | vptr `0x005e4f54` | `mov [esi],0x5e4f54` at `0x00538f14` |
| `+0x04` | code-array (flex) head | `lea ebx,[esi+4]; call 0x004241a0`; `Run` fetches `code = [obj+4]` |
| `+0x14` | 13-dword event-id → PC table | ctor reads 13 dwords; `CallEvent` indexes `[obj+0x14+eventId*4]`. Static users of ids 0–7 are listed below; ids 8–12 have **no** direct `E8` to `CallEvent` |
| `+0x48` | `CSPtrSet` of `CEventFunction` | ctor `call 0x004e5840` then `CSPtrSet__AddToTail` (`0x004e5b20`) |
| `+0x58` | symbol table | ctor stores the `0x00539770` reader result (`mov [esi+0x58],eax` at `0x00538fab`) |
| `+0x5c` | preamble-present dword (serialized) | ctor `lea eax,[esi+0x5c]; push 4; push eax; call 0x00548570` at `0x00539011`; `CallEvent` runs PC=0 iff this is nonzero and `+0x6c == 0` |
| `+0x60` | per-step trace dword (serialized) | ctor `lea edx,[esi+0x60]; push 4; push edx; call 0x00548570` at `0x00539004`; `Run` does `cmp dword [obj+0x60],1` at `0x00539ba4` |
| `+0x64` | instruction-count copy | ctor `mov ecx,[esi+0xc]; mov [esi+0x64],ecx` at `0x0053901e` |
| `+0x68` | owning `IScript*` | `IScript__Constructor` writes `mov [eventObj+0x68],this` at `0x005333f9`. Not a ctor-serialized field |
| `+0x6c` | preamble-already-run flag | ctor zeroes it (`mov [esi+0x6c],ebp` with `ebp=0` at `0x00538f1a`); `CallEvent`/`CallEventDirect` write `1` after the PC=0 preamble |

`CScriptObjectCode__Clone` copies the four trailer dwords on the success
path (`mov [esi+0x6c],[ebx+0x6c]` / `+0x60` / `+0x5c` / `+0x64` at
`0x00539165..0x0053917f`) and zeroes `+0x5c` only on the allocation-failure
arm at `0x00539265`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00538ec0` | `CMissionScriptObjectCode__ctor` | `6aff 6812755d00 … c706544f5e00 896e6c e84ef60000 … 8d5660 6a04 52 8bcf e85ff50000 8d465c 6a04 50 8bcf e852f50000 8b4e0c 89 4e64 … c20400` | `ret 4`; arg = `CDXMemBuffer*`. Inits flex array at `+4` and `CSPtrSet` at `+0x48`, installs vptr `0x005e4f54`, zeroes `+0x6c`, reads the instruction stream through `CAsmInstruction__SpawnFromOpcode` (`0x0052d3d0`), reads 13 event PCs into `+0x14`, stores the symbol table at `+0x58`, appends each `CEventFunction` (`0x0052fa70`) onto `+0x48`, then reads the two serialized trailer dwords into `+0x60` then `+0x5c` and copies the flex count to `+0x64`. HIGH on the layout and the two trailer reads. |
| `0x0052da00` | `FUN_0052da00` | `b817000000 c3` at file offset `0x0012da00` | Zero-arg `ret`. `mov eax,0x17; ret` — a 32-bit EAX constant 23. This is `CInstructionOP_RETURN` vtable `0x005e4bd0[+8]`, the getter `Run` calls via `call [edx+8]` at `0x00539b5e` and then `cmp eax,0x17`. The same address is also stored at `.rdata` `0x005dab54` (a second, non-RETURN vtable), so the thunk is not class-exclusive; the current name `FUN_0052da00` is the honest label. HIGH on the RETURN-slot contract and the return width (32-bit EAX, not a byte). |
| `0x0052e0f0` | `CInstructionOP_RETURN__ExecutePop` | `578b7c2408 8b8724020000 85c0 7e72 … 898724020000 e85db30000 … ff5030 898714020000 … c7 00 f84a5e00 c7400401000000 e8c1b20000 … c20c00` | `ret 0xc`; `CInstructionOP_RETURN` vtable `0x005e4bd0[+0]`, the executor `Run` calls via `call [edx]` at `0x00539b9f` with `(vm, &stack, symbols)`. If `[vm+0x224] <= 0` it returns immediately. Else it decrements `+0x224`, `Pop`s (`0x00539470`), reads a scalar through the element's `vtable[+0x30]`, writes that value to `vm+0x214` (PC), deletes the element, and pushes an 8-byte `CInt` (`vptr 0x005e4af8`, value 1). HIGH. Reachable only after `CALLLOCAL` has incremented `+0x224`; a top-level `0x17` still exits `Run` without calling this function. |
| `0x0052ec40` | `CInstructionOP_CALLLOCAL__VFunc_0_0052ec40` | `8b442404 8b4904 898814020000 8b8824020000 41 898824020000 c20c00` at file offset `0x0012ec40` | `ret 0xc`. `vm = arg0`; `PC = [instr+4]` (the attribute); `[vm+0x224]++`. This is `CInstructionOP_CALLLOCAL` vtable `0x005e4bb0[+0]`. The only interpreter increment of the return-depth guard. HIGH. |
| `0x0052d990` | `FUN_0052d990` | `b819000000 c3` | `mov eax,0x19; ret` — 32-bit opcode getter at `CInstructionOP_CALLLOCAL` vtable `0x005e4bb0[+8]`. HIGH. |
| `0x0052e0a0` | `CInstructionOP_PUSHPC__VFunc_0_0052e0a0` | `56 688f000000 8bf1 68c4c56400 6a18 6a08 … c700f84a5e00 894804 e84bb30000 … c20c00` | `ret 0xc`. Allocates an 8-byte `CInt` (`vptr 0x005e4af8`) whose value is the instruction attribute `[this+4]` and `Push`es it. That attribute is a stored PC, not the live `vm+0x214`. Together with `CALLLOCAL` this is the compiled call sequence (push return PC, then jump and increment depth). HIGH on the bytes. The pairing is unused on the 762-object corpus (0× `0x19`, 0× `0x1a` in 55,836 instructions). |
| `0x0052e2f0` | `CInstructionOP_POP__VFunc_0_0052e2f0` | `8b4104 8b4c240c 56 50 e862b40000 8bf0 8b4e08 85c9 7406 8b11 6a01 ff12 8b4c240c e85ab10000 894608 5e c20c00` | `ret 0xc`. `symbol = CScriptObjectCode__GetInstruction(symbols, attr)` (`0x00539760` = `[table][index]`); if `[symbol+8]` delete via `vtable[0](1)`; `[symbol+8] = Pop(stack)` (`0x00539470`). HIGH. All 128 shipped `hit` 13-slot bodies start with this opcode, so CallEvent id 4's argc=1 thing-ref lands in that local. |
| `0x00539760` | `CScriptObjectCode__GetInstruction` | `8b01 8b4c2404 8b0488 c20400` | `ret 4`. `return [this][index]`. Used as the symbol-table indexer by PUSH/POP. HIGH on the bytes; the name is the table label, not a claim that the table holds instructions. |
| `0x00539470` | `CScriptObjectCode__Pop` | `8b8100020000 85c0 7515 689c006500 … 33c0 c3 48 898100020000 8b0481 c3` | Zero-arg. `this` = stack head. Empty (`[head+0x200]==0`) prints via `0x0065009c` and returns 0; else `--depth` and return `[head + depth*4]`. HIGH. |
| `0x00539910` | `CScriptObjectCode__CopyState` | `8b7c240c 8bf1 8b4708 8d570c 894608 8b8f14020000 898e14020000 52 8d4e0c e81afaffff … 8b8718020000 898618020000 … c7861002000000000000 8bc6 … c20400` | `ret 4`, one arg = source. Copies `[src+8]`, `[src+0x214]` (PC), calls `CScriptObjectCode__RestoreStack` (`0x00539350`) with `(dst+0xc, src+0xc)`, then copies `+0x218`, `+0x220`, `+0x21c`, `+0x224`, and zeroes the running flag `+0x210`. Returns `this`. HIGH. |
| `0x00539980` | `CScriptObjectCode__Reset` | `83c10c e958faffff` | Zero-arg tail: `add ecx,0xc; jmp 0x005393e0` = `CScriptObjectCode__ClearStack(this+0xc)`. HIGH. |
| `0x00539990` | `CScriptObjectCode__CallEvent` | `8b860c020000 85c0 7412 6860016500 6880f56600 e8937df0ff … 8b7c240c 897e08 8b476c 85c0 752b 8b475c 85c0 7424 c7861402000000000000 … e81e010000 c7476c01000000 … 8b449114 83f8ff 898614020000 7525 …` | `ret 0x10`, four args `(eventObj, eventId, args[], argCount)`. If the operand stack is not empty (`[this+0x20c] != 0`) prints `"FATAL ERROR: stack not empty on call"` (`0x00650160`). Stores `[this+8] = eventObj`; if `eventObj->[+0x6c] == 0` and `eventObj->[+0x5c] != 0` runs the preamble (`PC = 0`, `Run`, then `eventObj->[+0x6c] = 1`). Resolves the entry `eventObj->[+0x14 + eventId*4]`; `-1` means no handler, in which case it deletes each arg element via `call [elem->vtable][0](elem, 1)` and returns. Otherwise sets `PC = entry`, pushes each arg with `CScriptObjectCode__Push` (`0x00539420`), and calls `Run`. HIGH on the dispatch; `+0x5c`/`+0x6c` are now owned (see the event-object table) and the preamble-present *meaning* of a nonzero `+0x5c` stays MEDIUM. |
| `0x00539420` | `CScriptObjectCode__Push` | `8b4c2408 8b8600020000 890c86 8b8e00020000 41 898600020000 3d80000000 7e1f 6878006500 6880f56600 e8eb82f0ff … 48 898600020000 … c20400` | `ret 4`; `this` = the stack head (`this+0xc` of the VM). `sp = [head+0x200]; [head + sp*4] = arg; sp++`; if `sp > 0x80` (128) it prints `"FATAL ERROR: Stack out of memory"` (`0x00650078`) and decrements the depth back (the overflowing push is rejected). HIGH — the 128-slot stack ceiling the schema records is byte-verified here. |
| `0x005393e0` | `CScriptObjectCode__ClearStack` | `8b8600020000 85c0 7423 … 8b4c86fc 85c9 7406 8b11 6a01 ff12 … 48 898600020000 75dd` | Zero-arg; walks the stack top-down, `call [elem->vtable][0](elem, 1)` for each non-null element, and zeroes the depth `+0x200`. HIGH. |
| `0x00539350` | `CScriptObjectCode__RestoreStack` | `8b8600020000 85c0 7423 … 8b7c240c 33c9 8b8700020000 898600020000 7e2c … 8b2c02 8928 … c7870002000000000000 … c20400` | `ret 4`; `this` = destination head, arg = source head. First clears the destination (the same delete loop as `ClearStack`), then copies the source's depth and each element dword `[src + i*4] → [dst + i*4]` (a **shallow move** of the pointer array), and zeroes the source depth. HIGH. |
| `0x00539a60` | `CScriptObjectCode__CallEventDirect` | `8b7c2410 8bf1 897e08 8b476c 85c0 7529 8b475c 85c0 7422 c7861402000000000000 8b860c020000 89861c020000 e86b000000 c7476c01000000 … 8b5c241c 8b8e0c020000 85db 898e1c020000 7e19 … e85ef9ffff … 8b442414 8bce 898614020000 e826000000 …` | `ret 0x10`, four args `(eventObj, entryPC, args[], argCount)`. Same preamble as `CallEvent` (PC = 0 + `Run` + `eventObj->[+0x6c] = 1` when `+0x6c == 0` and `+0x5c != 0`); snapshots the stack base (`+0x21c = +0x20c`); pushes each arg; sets `PC = entryPC` (taken directly, not looked up); calls `Run`. This is the entry `CEventFunction__Execute` uses for named callbacks. HIGH. |
| `0x00539ae0` | `CScriptObjectCode__GotoInstruction` | `8b442404 898114020000 e811000000 c20400` | `ret 4`: `PC = arg; Run()`. HIGH — the jump-into-script primitive behind `IScript`'s 2001 teardown. |
| `0x00539b00` | `CScriptObjectCode__Run` | `b801000000 398610020000 7516 6808026500 6880f56600 e87f7df0ff … 8b8e14020000 898610020000 8b4608 … 8b5004 8b4058 8b3c8a … 8b17 8bcf ff5208 83f817 750e 8b8624020000 85c0 0f8e94000000 … 8b9e14020000 8d4e0c 8d4301 898614020000 … 50 51 56 8bcf ff12 …` | The interpreter loop. Re-entry guard: if `[this+0x210] == 1` prints `"ERROR: VM tryin to run VM whilst it was already running."` (`0x00650208`) and returns; else sets the flag. Each step: `instr = code[PC]` with `code = [obj+4]`, `symbols = [obj+0x58]`; `opcode = instr->vtable[+8]()` (32-bit EAX); if `opcode == 0x17` and `[this+0x224] <= 0` → exit **without** calling the executor; if the stop flag `[this+0x220] != 0` → exit; otherwise `PC++` and `instr->vtable[+0](this, &stack[this+0xc], symbols)`. A `0x2710` (10,000) instruction guard prints `"FATAL ERROR :Infinite loop in script!"` (`0x006501bc`) and sets the stop flag. If `[obj+0x60] == 1` it traces `"-> %4d stack size = %d flags = %d"` (`0x006501e4`) per step. On exit: stop path zeroes `+0x20c`; normal path compares stack depth `+0x20c` against the saved base `+0x21c` and prints `"FATAL ERROR:  stack was different size when exiting"` (`0x00650188`) on mismatch. HIGH. |

## Wiring with the rest of the script system

- `IScript`'s message arms call the singleton: 2001 →
  `CopyState`/`Reset`/`GotoInstruction`; 2002 → `Reset`/`CallEvent`
  ([`IScript.cpp.md`](IScript.cpp.md)).
- `CEventFunction__Execute` (`0x0052fda0`) stages its parameter wrappers and
  calls `CallEventDirect` ([`EventFunction.cpp.md`](EventFunction.cpp.md)).
- `CMissionScriptObjectCode__ctor` (`0x00538ec0`) is the derived loader
  (`CWorld__LoadScriptEvents` constructs it per script file; see
  [`CScriptEventNB.cpp.md`](CScriptEventNB.cpp.md)).

## Instruction factory — `CAsmInstruction__SpawnFromOpcode` (`0x0052d3d0`)

The 27-opcode dispatch is byte-settled against the
[VM schema](../missionscript-vm-datatype-opcode-schema.v1.json):

1. `mov ecx,[esp+8]` takes the bytecode reader; `lea eax,[esp+0xc]` reuses the
   argument slot as a 4-byte buffer and `call 0x00548570`
   (`CDXMemBuffer__Read`) reads the instruction **attribute** (the "second
   dword" the schema names).
2. `mov eax,[esp+8]; cmp eax,0x1a; ja 0x52d8cb` bounds-checks the **opcode
   argument** (arg0, already decoded by the caller) against 26; out of range
   prints `"FATAL ERROR: uknown instruction in spawn"` (`0x0064cab8`, the
   shipped typo) and returns null.
3. `jmp dword [eax*4 + 0x0052d8e4]` dispatches through the 27-entry jump table
   (entries `0x0052d3f7` … `0x0052d89b`, one case body per opcode).
4. Each case allocates **0xc** bytes (`AsmInstruction.cpp` `__FILE__`
   `0x0064c5c4`, per-case `__LINE__` `0x57`/`0x58`/… rising), stores the
   attribute at `instr+0x04`, and installs the per-opcode vtable at `instr+0`
   with the exact law **`vtable = 0x005e4d40 − 0x10 × opcode`** — verified for
   all 27 opcodes against the schema's vtable column (`NOOP_0` `0x005e4d40`
   down to `PUSHPC` `0x005e4ba0`).

So an instruction object is a 12-byte `{vtable, attribute}` pair, and
`Run`'s two virtual calls are `vtable[+8]` (opcode getter) and `vtable[+0]`
(executor) over that pair. The `0x10` stride is three method pointers plus
the adjacent class's Complete Object Locator: `vtable[-4]` of RETURN is
`0x00618f80`, and `vtable[+0xc]` is POINTER's COL `0x00618e90`, not a fourth
RETURN virtual.

## Instruction class pin — `CInstructionOP_RETURN` (opcode `0x17`)

RTTI name `.?AVCInstructionOP_RETURN@@` at `0x0064c8a0`. Vtable
`0x005e4bd0` (file offset `0x001e4bd0`), three slots, zero direct `E8`/`E9`
callers (virtual only):

| Slot | Address | Current name | Body |
| --- | --- | --- | --- |
| `+0` | `0x0052e0f0` | `CInstructionOP_RETURN__ExecutePop` | nested-return executor (`ret 0xc`) |
| `+4` | `0x0052d9d0` | `CInstructionOP_RETURN__VFunc_1_0052d9d0` | clone: alloc `0xc` (`asminstruction.h:114`), install the same vptr `0x005e4bd0`, copy `[this+4]` |
| `+8` | `0x0052da00` | `FUN_0052da00` | `mov eax,0x17; ret` — 32-bit opcode getter |

The NOOP class (`vtable 0x005e4d40`) uses the same three-slot shape with
`SharedVFunc__ReturnZero_00405930` (`xor eax,eax; ret`) at `[+8]`, which is
the opcode-0 instance of the same getter-width law. Cheapest falsifier: a
`CInstructionOP_RETURN` instance whose `vtable[+8]` is not `0x0052da00`, or
`FUN_0052da00` returning anything other than `0x17` in EAX.

The getter width is therefore a 32-bit integer in EAX. `Run`'s
`cmp eax,0x17` is a full-dword compare, not a byte test.

A prior copied-runtime proof that serialized `+0x60 == 1` (and not `0` or
`2`) enables the per-step trace on a disposable Level 100 copy lives at
`local-lab/vm-trace-pilot-2026-08-02/vm-trace.ready.json` (SHA-256
`ad373947273ad083c9c37a53aba876e28399cba26821ae067df59d207e4ced09`,
re-hashed this slice). Its static-anchor bytes
`8d56606a04528bcfe85ff50000` / `8d465c6a04508bcfe852f50000` /
`837a60017521` match the ctor/`Run` reread above. The 136-line runtime
count was **not** re-executed here.

## Call/return depth — `CALLLOCAL` increments `+0x224`

`CInstructionOP_CALLLOCAL` (opcode `0x19`, vtable `0x005e4bb0`) is the
matching pair of `RETURN`:

| Slot | Address | Current name | Body |
| --- | --- | --- | --- |
| `+0` | `0x0052ec40` | `CInstructionOP_CALLLOCAL__VFunc_0_0052ec40` | `PC = attribute; [vm+0x224]++` (`ret 0xc`) |
| `+4` | `0x0052d9a0` | `CInstructionOP_CALLLOCAL__VFunc_1_0052d9a0` | 12-byte clone, same shape as RETURN's clone |
| `+8` | `0x0052d990` | `FUN_0052d990` | `mov eax,0x19; ret` |

A whole-`.text` scan of `[reg+0x224]` in `0x0052d000..0x0053a200` finds
exactly these interpreter writers: `ExecutePop` (read + decrement),
`CALLLOCAL` (read + increment), `Run` (zero on entry + the `<= 0` stop
test), `CopyState` (copy), and `InitRuntime` (zero). Five `IScript__*Wait` constructors
(`PlayAnimationWait`, `PlayCharMessageWait`,
`PlayPCharMessageWait`, `Pause`, `FollowWaypointWait`) allocate a
**0x228-byte CVM**, `rep movsd` 0x81 stack dwords, copy this same
six-dword tail, install vptr `0x005e4f1c`, then write live
`[0x0089c800]=1` so `Run` yields. That is construction plus a stop,
not an interpreter increment. See
[`IScript.cpp.md`](IScript.cpp.md) → "Wait helpers".

Cheapest falsifier: another instruction class whose executor writes
`[vm+0x224]` outside that census, or a shipped script that returns from a
local call without a preceding `CALLLOCAL`.

## Stack discipline (settled this slice)

The operand stack is an **inline 128-dword array**: head at `+0xc` of the VM
object, depth at `[head+0x200]` (the `+0x20c` field `Run` and `CallEvent`
already read). `Push` stores at `[head + depth*4]` and rejects past 128 with
`"FATAL ERROR: Stack out of memory"`; `ClearStack` and `RestoreStack` delete
each resident element through its `vtable[0](elem, 1)` (the shared
value-delete convention), and `RestoreStack` then shallow-moves the source's
pointer array into the destination.

## Event-id table — static `CallEvent` users of slots 0–7

`CScriptObjectCode__CallEvent` has exactly eight direct `E8` sites. All
eight live in `IScript`. Arg order is `(eventObj, eventId, args, argCount)`
with `this = 0x0089c5e0`. `eventObj` is always `[IScript+0xc]`. Every
wrapper except id 0 also consults `[0x008a9ac0]==4` (`GAME_STATE_LEVEL_LOST`)
and Reset()s instead of calling. `0x0089c528` is a `.data` BSS scratch pointer (PE
`to_offset` refuses it as uninitialised); `CreateThingRef` /
`CreateThingRefWithSquad` store a freshly allocated wrapper there and pass
`argCount=1`; the OrReset / 2002 / VFunc_2 paths pass the same address with
`argCount=0`.

| Id | Name (table `0x0064fef8`) | Arity | Caller | Site |
| --- | --- | --- | --- | --- |
| 0 | `init` | 0 | `IScript__CallEvent0AndRegisterNestedListeners` | `0x0053352a` |
| 1 | `arrived` | 1 | `IScript__CreateThingRef` | `0x0053364e` |
| 2 | `timer` | 0 | `IScript__HandleMessage` 2002 arm | `0x00538638` |
| 3 | `died` | 0 | `IScript__CallEventId3_OrReset` | `0x00533805` |
| 4 | `hit` | 1 | `IScript__CreateThingRefWithSquad` | `0x005337bd` |
| 5 | `started_dying` | 0 | `IScript__CallEventId5_OrReset` | `0x00533685` |
| 6 | `ready` | 0 | `IScript__CallEventId6_OrReset` | `0x005335c5` |
| 7 | `shutdown` | 0 | `IScript__VFunc_2_00533810` | `0x00533835` |
| 8 | `notdefined4` | 0 | *(none)* | — |
| 9 | `notdefined5` | 0 | *(none)* | — |
| 10 | `notdefined6` | 0 | *(none)* | — |
| 11 | `notdefined7` | 0 | *(none)* | — |
| 12 | `notdefined8` | 0 | *(none)* | — |

The names are the 13 `{int32 id, char* name, int32 arity}` records at
`.data` `0x0064fef8` (file `0x0024fef8`), independently re-read 2026-08-18.
They match the wrapper immediates above. Authored *behavior* of each
handler is still open.

Shipped occupancy (safe-copy `local-lab/safe-copy-bea-pristine/data/Resources`,
301 `.aya`, 115 worlds, **762** script objects, 0 parse failures, parser
`local-lab/msl/script_parse.py` mirroring ctor `0x00538ec0`):

| Id | Name | Objects with IP `!= -1` | First opcode of those IPs |
| --- | --- | --- | --- |
| 0 | `init` | 573 | `5` 320 / `24` 137 / `23` 116 |
| 1 | `arrived` | **0** (all `-1`) | — |
| 2 | `timer` | **0** (all `-1`) | — |
| 3 | `died` | 265 | `5` 145 / `24` 113 / `23` 7 |
| 4 | `hit` | 128 | all opcode `6` (POP → `symbol[attr]+8`) |
| 5 | `started_dying` | 142 | `5` 99 / `24` 39 / `23` 4 |
| 6 | `ready` | 6 | `5` 6 |
| 7 | `shutdown` | 3 | `5` 3 |
| 8–12 | `notdefined*` | **0** (all `-1`) | — |

`CallEvent` already no-ops an IP of `-1`. The eight IScript wrappers still
*fire* ids 0–7. Shipped objects have no compiled 13-slot body for
`arrived` / `timer` / `notdefined*`. Those two names also do **not** live
as `CEventFunction` listen-strings (measured below). The fire sites are:

- **arrived (id 1).** Only `E8` to `IScript__CreateThingRef`
  (`0x005335d0`) is `0x00538583` inside
  `CScriptEventNB__UpdateWaypointFollowing`: the end-of-waypoint-chain
  arm (`[this+0x14]` advanced to null and `[this+0x1c] == 0`). It boxes
  `[IScript+0x24]` as a `CInt` (`vptr 0x005e4af8`) at BSS `0x0089c528`
  and `CallEvent(eventObj, 1, &0x0089c528, 1)`. `FollowWaypoint`
  (`0x00537d70`) is the writer of `+0x24` (`mov [esi+0x24],eax` at
  `0x00537dc7` from `args[1]->vtable[+0x30]()`, which for `CInt` is
  `SharedVFunc__ReturnField04_0052f540`). 19 shipped native-0 `CALL`s:
 that second arg is always a `CInt` **0** (13) or **1** (6). Only
 other `IScript+0x24` access in `0x00533000..0x00539000` is the
 arrived() box. Flag=1: 600 Ship/Slave, 731/732 messages, 741/742
 Marshall. On the
 shipped corpus the lookup is always `-1`, so the wrapper deletes the
 `CInt` and returns.
- **timer (id 2).** `IScript__SetTimer` (`0x005358e0`, `ret 0xc`, zero
  direct `E8` — registry command `"SetTimer"`) calls
  `CEventManager__AddEvent_TimeFromNow` (`0x0044b2d0`) with event
  **2002** (`push 0x7d2` at `0x005358fd`) against the same `IScript`.
  `HandleMessage`'s 2002 arm then `CallEvent(eventObj, 2, &0x0089c528, 0)`.
  Zero compiled `SetTimer` uses (native-corpus `DORMANT_CANDIDATE`) and
  zero `SetTimer(` / `timer()` / `event("timer")` in 733 loose
  `.msl`. The 2002 arm can still fire if something else schedules 2002;
  the 13-slot body is still `-1`.

### Named `CEventFunction` occupancy (the `+0x48` set)

`CEventFunction__CEventFunction` (`0x0052fa70`, `ret 8`) is **not** an
id-table writer. Independently re-read 2026-08-18 from file offset
`0x0012fa70`:

| Offset | Field | Witness |
| --- | --- | --- |
| `+0` | vptr `0x005e4ef8` | `mov [edi],0x5e4ef8` at `0x0052fabd` after the `CMonitor` base install |
| `+8` | entry PC | `lea ecx,[edi+8]; push 4; push ecx; call 0x00548570` at `0x0052fab0` |
| `+0xc` | `CSPtrSet` of name wrappers | `lea ecx,[edi+0xc]; call 0x004e5840`; each param is a symbol index resolved through `[owner+0x58]`, datatype **must** be `3` (`cmp eax,3` at `0x0052fb12`) else `"FATAL ERROR: Event Function was expecting a string"` (`0x0064cd38`) |
| `+0x1c` | owner `CMissionScriptObjectCode*` | `mov [edi+0x1c],eax` at `0x0052fac3` |

`CEventFunction__Execute` (`0x0052fda0`) is the **only** `E8` to
`CallEventDirect` (`0x00539a60` at `0x0052fe24`):
`CallEventDirect(owner=this+0x1c, entryPC=this+8, args=local[], count)`.
`Execute` itself has exactly two `E8` sites, both already mapped:
`CScriptEventNB__PostEvent` `0x00538c3b` and
`CScriptEventNB__HandleEventMessage` `0x00538d68`. Named handlers
therefore never consult the 13-slot table.

Registration is `IScript__CallEvent0AndRegisterNestedListeners`
(`0x00533500`): after `CallEvent(id=0)` it walks `eventObj+0x48` and
for each function's `+0xc` name wrappers calls
`CScriptEventNB__RegisterEventListener` (`0x00538960`) on singleton
`0x0089c590` (`push name; push function` at `0x0053355d`). Only `E8` to
`0x00533500` is `CComplexThing__HandleEvent` `0x004f4359` (message
**2001** on a thing that has `[this+0x74]`).

Same 762-object safe-copy parse, 0 failures:

| | count |
| --- | --- |
| `CEventFunction` records | **994** |
| objects with at least one | 386 |
| objects with none | 376 |
| unique listen-strings | 364 |
| listen-string `arrived` | **0** |
| listen-string `timer` | **0** |
| listen-string `game playing` | 92 |

Top listen-strings after `game playing`: `Target Emplacements` 17,
`Marshall Destroyed` 14, `Lock Buildings` 11, `run away` 11. Strings
that merely *contain* those words are different names (`Gill-M Arrived`
8, `Carrier Arrived` 2, `Transports Arrived` 2, `Start Timer` 2,
`Timer Pulse` 5, `Start Race Timer` 5) and are not id-1 / id-2.

Spot-check (parser `read_event` vs the ctor reads above): `110` RLWD
`Scout` has evtab died=`1` and one named handler `{entry:5, "game playing"}`;
`200` RLWD `FighterAttack` has init=`1`, hit=`30`, and named entries
2 / 9 / 16 / 23. The named PCs are not id-table slots.

Every one of the 994 named entries is opcode `0x13`
(`CInstructionOP_JMPFALSE`). Independently re-read executor
`0x0052e950` (`ret 0xc`, file `0x0012e950`): `Pop` (`0x00539470`),
`call [elem->vtable+0x3c]`, if AL is 0 write `instr+4` to `vm+0x214`
(PC), then delete the element. All 994 jumps are **forward** (min
delta 1, max 367, mode 6 with 127). `nparam` is 1 on every record.
Zero named entries share a PC with a 13-slot IP.

The popped value is a `CBoolDataType` (`vtable 0x005e4d50`, RTTI
`.?AVCBoolDataType@@` — not a distinct `CEventFunctionParam` class).
`Execute` installs that vtable on an 8-byte wrapper and copies
`byte [listenerElement+0x14]` into `wrapper+4`. Slot `+0x3c` is
`CBoolDataType__VFunc_15_0052e480` (`mov al,[ecx+4]; ret` at file
`0x0012e480`). `PostEvent` / `HandleEventMessage` write
`element+0x14 = 1` before `Execute`, so the posted path falls through
into the body; a 0 skips to the attribute PC (the instruction after
the handler). Scout: entry 5 `JMPFALSE 14`, body
`PlayCharMessage` + `PostEvent("Enemy Engaged")`, target 14 is
`op0d` immediately after.

Immediately after the guard: PUSH 833 / CALL 147 / NOOP_0D 14
(the 14 NOOP_0D rows are the empty delta-1 handlers). Walking past
a leading PUSH run, **518** of 994 hit a `CALL` as the first
native. Top shipped first-natives (parser `natives.json`, native 0
=`FollowWaypoint`): `SetObjective` 75, `Pause` 68,
`PlayCharMessageWait` 59, `Print` 47, `PlayCharMessage` 32,
`SetAIState` 26, `GetThingRef` 25. This is occupancy, not a claim
that those natives are the authored purpose of the event.

Every named-event JMPFALSE target is opcode `0x0d`. Independently
re-read 2026-08-18 (994/994, 0 oob). RTTI at vtable `0x005e4c70`
(COLOC `0x00618e40` → `.?AVCInstructionOP_LABEL@@`): getter
`FUN_0052dcd0` is `mov eax,0x0d; ret`; executor is
`SharedVFunc__NoOp_Ret0C` (`0x00453ac0`, `ret 0xc`). Opcode
`0x0e` is `.?AVCInstructionOP_REMOVE_TOP@@` (vtable `0x005e4c60`,
COLOC `0x00618f30`): getter `FUN_0052dc80` is `mov eax,0x0e; ret`;
executor `CInstructionOP_REMOVE_TOP__VFunc_0_0052e320` (`0x0052e320`)
calls `CScriptObjectCode__RemoveTop` (`0x005394a0`) on the operand
stack — dec depth, `vtable[0](elem, 1)` the discarded top, or
print `FATAL ERROR: RemoveTop called on empty stack`
(`0x006500c4`). Opcode immediately before the end-label: `0x0e`
671 / `0x0d` 309 / `0x13` 14 (the empty delta-1 handlers). The
309 are not adjacent handlers: every one is an internal join
`LABEL` that a body `JMPFALSE` (255) or `JMP` (54) already
targets, immediately followed by the handler's end `LABEL`.
Zero unreferenced. The
compiled shape is `JMPFALSE L` / body / optional `REMOVE_TOP` /
`L: LABEL`. The skip lands on a no-op so the VM continues after
the handler; `REMOVE_TOP` drops a leftover statement value so
`CallEventDirect`'s exit-depth check can pass.

Thing-side fire of the 13-slot ids (not IScript `HandleMessage`)
is owned by [`CComplexThing.cpp.md`](CComplexThing.cpp.md):
`SetScript` → thing-event 2001 → `CallEvent(id=0)` + register
`+0x48` names; non-unit things then get thing-event 2003 →
`CallEvent(id=6)`. `AddShutdownEvent` → `CallEvent(id=3)` then
deletes the IScript and schedules thing-event 2000 →
`CallEvent(id=7)` only if `+0x74` is still live (it is not, on
that path). `Hit` → `CallEvent(id=4)`. `StartDieProcess` on
`CComplexThing` cannot reach `CallEvent(id=5)` because it calls
`AddShutdownEvent` first. The two reachable `CallEventId5` sites
keep `+0x74` live: `CFeature__VFunc_50_0044cd80` (slot 50, no
teardown) and `CUnit__MarkDestroyedAndCleanupLinks` (slot 50 of
three unit vtables; fires after count teardown, before `+0x144`
cleanup).

733 loose `MissionScripts/**/*.msl` contain zero `arrived(`, `timer(`,
`SetTimer(`, `event("arrived"`, or `event("timer"`.

Cheapest falsifier: a shipped object whose 13-slot `arrived`/`timer` IP
is not `-1`; a `CEventFunction` whose string symbol value is exactly
`arrived` or `timer`; a second `E8` to `CreateThingRef` or
`CallEventDirect`.

Object trailers (ctor writes A → `+0x60`, B → `+0x5c`):

| trailerA (`+0x60`) | trailerB (`+0x5c`) | count |
| --- | --- | --- |
| 0 | 1 | 715 |
| 0 | 0 | 47 |

No shipped object has trailerA `== 1`, so the Run-time trace compare at
`0x00539ba4` is off for the whole corpus. 715 objects have a one-time
PC=0 preamble; 47 do not.

Cheapest falsifier for a missing static user of 8–12: another `E8` to `0x00539990`
outside the eight-site census. `CallEventDirect` is not an id-table
lookup: its only `E8` is `CEventFunction__Execute` passing `this+8`.

## Open questions (cheapest falsifier first)

- Who increments `vm+0x224`: CLOSED — `CInstructionOP_CALLLOCAL__VFunc_0_0052ec40`
  (`0x0052ec40`) is the only interpreter increment. `PUSHPC`
  (`CInstructionOP_PUSHPC__VFunc_0_0052e0a0`) pushes the *attribute* as a
  `CInt`. Shipped pairing: **neither opcode occurs**. Same 762-object
  parse, 55,836 instructions: counts for `0x19` CALLLOCAL and `0x1a`
  PUSHPC are both 0. Also unused: `0x00` NOOP and `0x11`
  COMPARE_NOT_EQUAL. Nested `ExecutePop` is therefore unreachable on
  the corpus. Cheapest falsifier: one compiled object whose stream
  contains opcode `0x19` or `0x1a`.
- `+0x5c` / trailerB: CLOSED as the one-time PC=0 preamble flag.
  Shipped split is 715 ones / 47 zeros (safe-copy census above). Authored
  name of the field is still open.
- trailerA / `+0x60`: CLOSED as 0 in all 762 shipped objects. The
  `== 1` trace compare is unused on the corpus.
- The 13 event-id slots at `eventObj+0x14`. CLOSED: names and arities
  come from `.data` `0x0064fef8`; static users of 0–7 are the IScript
  wrappers above. Ids 8–12 (`notdefined4`–`notdefined8`) have no direct
  `E8`. `arrived` / `timer` have no shipped 13-slot body and no
  same-name `CEventFunction`; they fire (and no-op) from the waypoint
  end-of-chain / `SetTimer`→2002 paths above. Authored arrival/delay
  behavior on the corpus is the named-string set, not those two ids.
- The second `.rdata` holder of `FUN_0052da00` at `0x005dab54`: CLOSED as
  `CWarspiteDomeBehaviourType` vtable `0x005dab50[+4]` (cohort census
  `col_ptr 0x005dab4c`). Same thunk body (`mov eax,0x17; ret`), different
  class; do not rename it to a RETURN getter.
